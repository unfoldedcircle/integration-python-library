"""
Integration driver API for Remote Two.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import json
import logging
import os
import socket
from asyncio import AbstractEventLoop
from typing import Any

import websockets
from pyee import AsyncIOEventEmitter

# workaround for pylint error: E0611: No name 'ConnectionClosedOK' in module 'websockets' (no-name-in-module)
from websockets.exceptions import ConnectionClosedOK

# workaround for pylint error: E1101: Module 'websockets' has no 'serve' member (no-member)
from websockets.server import serve
from zeroconf import IPVersion
from zeroconf.asyncio import AsyncServiceInfo, AsyncZeroconf

import ucapi.api_definitions as uc
from ucapi.entities import Entities

_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.DEBUG)


class IntegrationAPI:
    """Integration API to communicate with Remote Two."""

    def __init__(self, loop: AbstractEventLoop):
        """
        Create an integration driver API instance.

        :param loop: event loop
        """
        self._loop = loop
        self._events = AsyncIOEventEmitter(self._loop)
        self._driver_info: dict[str, Any] = {}
        self._driver_path: str | None = None
        self._state: uc.DeviceStates = uc.DeviceStates.DISCONNECTED
        self._server_task = None
        self._clients = set()

        self._interface: str | None = os.getenv("UC_INTEGRATION_INTERFACE")
        self._port: int | str | None = os.getenv("UC_INTEGRATION_HTTP_PORT")
        self._https_enabled: bool = os.getenv("UC_INTEGRATION_HTTPS_ENABLED", "false").lower() in ("true", "1")
        self._disable_mdns_publish: bool = os.getenv("UC_DISABLE_MDNS_PUBLISH", "false").lower() in ("true", "1")

        self._config_dir_path: str | None = os.getenv("UC_CONFIG_HOME")

        self._available_entities = Entities("available", self._loop)
        self._configured_entities = Entities("configured", self._loop)

        # Setup event loop
        asyncio.set_event_loop(self._loop)

    async def init(self, driver_path: str):
        """
        Load driver configuration and start integration-API WebSocket server.

        :param driver_path: path to configuration file
        """
        self._driver_path = driver_path
        self._port = self._driver_info["port"] if "port" in self._driver_info else self._port

        @self._configured_entities.events.on(uc.Events.ENTITY_ATTRIBUTES_UPDATED)
        async def event_handler(entity_id, entity_type, attributes):
            data = {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "attributes": attributes,
            }

            await self._broadcast_event(uc.WsMsgEvents.ENTITY_CHANGE, data, uc.EventCategory.ENTITY)

        # Load driver config
        with open(self._driver_path, "r", encoding="utf-8") as file:
            self._driver_info = json.load(file)

        # Set driver URL
        # TODO verify _get_driver_url: logic might not be correct,
        #      move all parameter logic inside method to better understand what this does
        self._driver_info["driver_url"] = self._get_driver_url(
            self._driver_info["driver_url"] if "driver_url" in self._driver_info else self._interface, self._port
        )

        # Set driver name
        name = _get_default_language_string(self._driver_info["name"], "Unknown driver")
        # TODO there seems to be missing something with `url`
        # url = self._interface

        # TODO: add support for secured WS
        addr = (
            socket.gethostbyname(socket.gethostname()) if self._driver_info["driver_url"] is None else self._interface
        )

        # addr = address if address else None

        if self._disable_mdns_publish is False:
            # Setup zeroconf service info
            info = AsyncServiceInfo(
                "_uc-integration._tcp.local.",
                f"{self._driver_info['driver_id']}._uc-integration._tcp.local.",
                addresses=[addr] if addr else None,
                port=int(self._port),
                properties={
                    "name": name,
                    "ver": self._driver_info["version"],
                    "developer": self._driver_info["developer"]["name"],
                },
            )
            zeroconf = AsyncZeroconf(ip_version=IPVersion.V4Only)
            await zeroconf.async_register_service(info)

        self._server_task = self._loop.create_task(self._start_web_socket_server())

        _LOG.info(
            "Driver is up: %s, version: %s, listening on: %s",
            self._driver_info["driver_id"],
            self._driver_info["version"],
            self._driver_info["driver_url"],
        )

    def _get_driver_url(self, driver_url: str | None, port: int | str) -> str | None:
        if driver_url is not None:
            if driver_url.startswith("ws://") or driver_url.startswith("wss://"):
                return driver_url

            return "ws://" + self._interface + ":" + port

        return None

    async def _start_web_socket_server(self) -> None:
        async with serve(self._handle_ws, self._interface, int(self._port)):
            await asyncio.Future()

    async def _handle_ws(self, websocket) -> None:
        try:
            self._clients.add(websocket)
            _LOG.info("WS: Client added")

            # authenticate on connection
            await self._authenticate(websocket, True)

            async for message in websocket:
                # process message
                await self._process_ws_message(websocket, message)

        except ConnectionClosedOK:
            _LOG.info("WS: Connection Closed")

        except websockets.exceptions.ConnectionClosedError:
            _LOG.info("WS: Connection Closed")

        finally:
            self._clients.remove(websocket)
            _LOG.info("WS: Client removed")
            self._events.emit(uc.Events.DISCONNECT)

    async def _send_ok_result(self, websocket, req_id: int, msg_data: dict[str, Any] | None = None) -> None:
        await self._send_response(websocket, req_id, "result", msg_data, uc.StatusCodes.OK)

    async def _send_error_result(
        self,
        websocket,
        req_id: int,
        status_code: uc.StatusCodes = uc.StatusCodes.SERVER_ERROR,
        msg_data: dict[str, Any] | None = None,
    ) -> None:
        await self._send_response(websocket, req_id, "result", msg_data, status_code)

    async def _send_response(
        self,
        websocket,
        req_id: int,
        msg: str,
        msg_data: dict[str, Any] | list[Any] | None,
        status_code=uc.StatusCodes.OK,
    ) -> None:
        data = {
            "kind": "resp",
            "req_id": req_id,
            "code": int(status_code),
            "msg": msg,
            "msg_data": msg_data if msg_data is not None else {},
        }

        if websocket in self._clients:
            data_dump = json.dumps(data)
            _LOG.debug("->: %s", data_dump)
            await websocket.send(data_dump)
        else:
            _LOG.error("Error sending response: connection no longer established")

    async def _broadcast_event(self, msg: str, msg_data: dict[str, Any], category: str) -> None:
        data = {"kind": "event", "msg": msg, "msg_data": msg_data, "cat": category}

        for websocket in self._clients:
            data_dump = json.dumps(data)
            _LOG.debug("->: %s", data_dump)
            await websocket.send(data_dump)

    async def _send_event(self, websocket, msg: str, msg_data: dict[str, Any], category: str) -> None:
        data = {"kind": "event", "msg": msg, "msg_data": msg_data, "cat": category}

        if websocket in self._clients:
            data_dump = json.dumps(data)
            _LOG.debug("->: %s", data_dump)
            await websocket.send(data_dump)
        else:
            _LOG.error("Error sending event: connection no longer established")

    async def _process_ws_message(self, websocket, message) -> None:
        _LOG.debug("<-: %s", message)

        data = json.loads(message)
        kind = data["kind"]
        req_id = data["id"] if "id" in data else None
        msg = data["msg"]
        msg_data = data["msg_data"] if "msg_data" in data else None

        if kind == "req":
            if req_id is None:
                _LOG.warning("Ignoring request message with missing 'req_id': %s", message)
            else:
                await self._handle_ws_request_msg(websocket, msg, req_id, msg_data)
        elif kind == "event":
            self._handle_ws_event_msg(msg, msg_data)

    async def _handle_ws_request_msg(self, websocket, msg: str, req_id: int, msg_data: dict[str, Any] | None) -> None:
        if msg == uc.WsMessages.GET_DRIVER_VERSION:
            await self._send_response(websocket, req_id, uc.WsMsgEvents.DRIVER_VERSION, self.get_driver_version())
        elif msg == uc.WsMessages.GET_DEVICE_STATE:
            await self._send_response(websocket, req_id, uc.WsMsgEvents.DEVICE_STATE, {"state": self.state})
        elif msg == uc.WsMessages.GET_AVAILABLE_ENTITIES:
            available_entities = self._available_entities.get_all()
            await self._send_response(
                websocket,
                req_id,
                uc.WsMsgEvents.AVAILABLE_ENTITIES,
                {"available_entities": available_entities},
            )
        elif msg == uc.WsMessages.GET_ENTITY_STATES:
            entity_states = await self._configured_entities.get_states()
            await self._send_response(
                websocket,
                req_id,
                uc.WsMsgEvents.ENTITY_STATES,
                entity_states,
            )
        elif msg == uc.WsMessages.ENTITY_COMMAND:
            await self._entity_command(websocket, req_id, msg_data)
        elif msg == uc.WsMessages.SUBSCRIBE_EVENTS:
            await self._subscribe_events(msg_data)
            await self._send_ok_result(websocket, req_id)
        elif msg == uc.WsMessages.UNSUBSCRIBE_EVENTS:
            await self._unsubscribe_events(msg_data)
            await self._send_ok_result(websocket, req_id)
        elif msg == uc.WsMessages.GET_DRIVER_METADATA:
            await self._send_response(websocket, req_id, uc.WsMsgEvents.DRIVER_METADATA, self._driver_info)
        elif msg == uc.WsMessages.SETUP_DRIVER:
            await self._setup_driver(websocket, req_id, msg_data)
        elif msg == uc.WsMessages.SET_DRIVER_USER_DATA:
            await self._set_driver_user_data(websocket, req_id, msg_data)

    def _handle_ws_event_msg(self, msg: str, _msg_data: dict[str, Any] | None) -> None:
        if msg == uc.WsMsgEvents.CONNECT:
            self._events.emit(uc.Events.CONNECT)
        elif msg == uc.WsMsgEvents.DISCONNECT:
            self._events.emit(uc.Events.DISCONNECT)
        elif msg == uc.WsMsgEvents.ENTER_STANDBY:
            self._events.emit(uc.Events.ENTER_STANDBY)
        elif msg == uc.WsMsgEvents.EXIT_STANDBY:
            self._events.emit(uc.Events.EXIT_STANDBY)
        elif msg == uc.WsMsgEvents.ABORT_DRIVER_SETUP:
            self._events.emit(uc.Events.SETUP_DRIVER_ABORT)

    async def _authenticate(self, websocket, success: bool) -> None:
        await self._send_response(
            websocket,
            0,
            uc.WsMessages.AUTHENTICATION,
            {},
            uc.StatusCodes.OK if success else uc.StatusCodes.UNAUTHORIZED,
        )

    def get_driver_version(self) -> dict[str, dict[str, Any]]:
        """Get driver version information."""
        return {
            "name": self._driver_info["name"]["en"],
            "version": {
                "api": self._driver_info["min_core_api"],
                "driver": self._driver_info["version"],
            },
        }

    # TODO use a property setter?
    async def set_device_state(self, state: uc.DeviceStates) -> None:
        """Set new state."""
        self._state = state

        await self._broadcast_event(uc.WsMsgEvents.DEVICE_STATE, {"state": self.state}, uc.EventCategory.DEVICE)

    async def _subscribe_events(self, msg_data: dict[str, Any] | None) -> None:
        if msg_data is None:
            _LOG.warning("Ignoring _subscribe_events: called with empty msg_data")
            return
        for entity_id in msg_data["entity_ids"]:
            entity = self._available_entities.get(entity_id)
            if entity is not None:
                self._configured_entities.add(entity)
            else:
                _LOG.warning(
                    "WARN: cannot subscribe entity %s: entity is not available",
                    entity_id,
                )

        self._events.emit(uc.Events.SUBSCRIBE_ENTITIES, msg_data["entity_ids"])

    async def _unsubscribe_events(self, msg_data: dict[str, Any] | None) -> bool:
        if msg_data is None:
            _LOG.warning("Ignoring _unsubscribe_events: called with empty msg_data")
            return False

        res = True

        for entity_id in msg_data["entity_ids"]:
            if self._configured_entities.remove(entity_id) is False:
                res = False

        self._events.emit(uc.Events.UNSUBSCRIBE_ENTITIES, msg_data["entity_ids"])

        return res

    async def _entity_command(self, websocket, req_id: int, msg_data: dict[str, Any] | None) -> None:
        if msg_data is None:
            _LOG.warning("Ignoring _entity_command: called with empty msg_data")
            return
        self._events.emit(
            uc.Events.ENTITY_COMMAND,
            websocket,
            req_id,
            msg_data["entity_id"],
            msg_data["entity_type"],
            msg_data["cmd_id"],
            msg_data["params"] if "params" in msg_data else None,
        )

    async def _setup_driver(self, websocket, req_id: int, msg_data: dict[str, Any] | None) -> None:
        if msg_data is None:
            _LOG.warning("Ignoring _setup_driver: called with empty msg_data")
            return
        self._events.emit(uc.Events.SETUP_DRIVER, websocket, req_id, msg_data["setup_data"])

    async def _set_driver_user_data(self, websocket, req_id: int, msg_data: dict[str, Any] | None) -> None:
        if "input_values" in msg_data:
            self._events.emit(uc.Events.SETUP_DRIVER_USER_DATA, websocket, req_id, msg_data["input_values"])
        elif "confirm" in msg_data:
            self._events.emit(uc.Events.SETUP_DRIVER_USER_CONFIRMATION, websocket, req_id, data=None)
        else:
            _LOG.warning("Unsupported set_driver_user_data payload received")

    async def acknowledge_command(self, websocket, req_id: int, status_code=uc.StatusCodes.OK) -> None:
        """Acknowledge a command from Remote Two."""
        await self._send_response(websocket, req_id, "result", {}, status_code)

    async def driver_setup_progress(self, websocket) -> None:
        """Send a driver setup progress event to Remote Two."""
        data = {"event_type": "SETUP", "state": "SETUP"}

        await self._send_event(websocket, uc.WsMsgEvents.DRIVER_SETUP_CHANGE, data, uc.EventCategory.DEVICE)

    async def request_driver_setup_user_confirmation(self, websocket, title, msg1=None, image=None, msg2=None) -> None:
        """Request a user confirmation during the driver setup process."""
        data = {
            "event_type": "SETUP",
            "state": "WAIT_USER_ACTION",
            "require_user_action": {
                "confirmation": {
                    "title": _to_language_object(title),
                    "message1": _to_language_object(msg1),
                    "image": image,
                    "message2": _to_language_object(msg2),
                }
            },
        }

        await self._send_event(websocket, uc.WsMsgEvents.DRIVER_SETUP_CHANGE, data, uc.EventCategory.DEVICE)

    async def request_driver_setup_user_input(self, websocket, title, settings: dict[str, Any]) -> None:
        """Request a user input during the driver setup process."""
        data = {
            "event_type": "SETUP",
            "state": "WAIT_USER_ACTION",
            "require_user_action": {"input": {"title": _to_language_object(title), "settings": settings}},
        }

        await self._send_event(websocket, uc.WsMsgEvents.DRIVER_SETUP_CHANGE, data, uc.EventCategory.DEVICE)

    async def driver_setup_complete(self, websocket) -> None:
        """Send a driver setup complete event to Remote Two."""
        data = {"event_type": "STOP", "state": "OK"}

        await self._send_event(websocket, uc.WsMsgEvents.DRIVER_SETUP_CHANGE, data, uc.EventCategory.DEVICE)

    async def driver_setup_error(self, websocket, error="OTHER") -> None:
        """Send a driver setup error event to Remote Two."""
        data = {"event_type": "STOP", "state": "ERROR", "error": error}

        await self._send_event(websocket, uc.WsMsgEvents.DRIVER_SETUP_CHANGE, data, uc.EventCategory.DEVICE)

    ##############
    # Properties #
    ##############
    # TODO redesign event callback: don't expose AsyncIOEventEmitter! The client may not emit events!!!
    @property
    def events(self) -> AsyncIOEventEmitter:
        """Return event emitter."""
        return self._events

    @property
    def state(self) -> str:
        """Return driver state."""
        return self._state

    @property
    def config_dir_path(self) -> str | None:
        """Return configuration directory path."""
        return self._config_dir_path

    @property
    def available_entities(self) -> Entities:
        """Return the available entities."""
        return self._available_entities

    @property
    def configured_entities(self) -> Entities:
        """Return the configured entities."""
        return self._configured_entities


def _to_language_object(text: str | dict[str, str] | None) -> dict[str, str] | None:
    if text is None:
        return None
    if isinstance(text, str):
        return {"en": text}

    return text


def _get_default_language_string(text: str | dict[str, str] | None, default_text="Undefined") -> str:
    if text is None:
        return default_text

    if "en" in text:
        return text["en"]

    for index, key, value in text.items():
        if index == 0:
            default_text = value

        if key.startswith("en_"):
            return text[key]

    return default_text
