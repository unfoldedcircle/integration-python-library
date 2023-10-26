"""
Integration driver API for Remote Two.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL 2.0, see LICENSE for more details.
"""

import asyncio
import json
import logging
import os
import socket
from asyncio import AbstractEventLoop

import websockets
from pyee import AsyncIOEventEmitter
from zeroconf import IPVersion
from zeroconf.asyncio import AsyncServiceInfo, AsyncZeroconf

import ucapi.api_definitions as uc
from ucapi import entities

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class IntegrationAPI:
    """Integration API to communicate with Remote Two."""

    def __init__(self, loop: AbstractEventLoop):
        """
        Create an integration driver API instance.

        :param loop: event loop
        """
        self._loop = loop
        self.events = AsyncIOEventEmitter(self._loop)
        self.driverInfo = {}
        self._driver_path = None
        self.state = uc.DEVICE_STATES.DISCONNECTED
        self._server_task = None
        self._clients = set()

        self._interface = os.getenv("UC_INTEGRATION_INTERFACE")
        self._port = os.getenv("UC_INTEGRATION_HTTP_PORT")
        # TODO: add support for secured
        self._https_enabled = os.getenv("UC_INTEGRATION_HTTPS_ENABLED", "False").lower() in ("true", "1", "t")
        self._disable_mdns_publish = os.getenv("UC_DISABLE_MDNS_PUBLISH", "False").lower() in ("true", "1", "t")

        self.configDirPath = os.getenv("UC_CONFIG_HOME")

        self.availableEntities = entities.Entities("available", self._loop)
        self.configuredEntities = entities.Entities("configured", self._loop)

        # Setup event loop
        asyncio.set_event_loop(self._loop)

    async def init(self, driver_path):
        """
        Load driver configuration and start integration-API WebSocket server.

        :param driver_path: path to configuration file
        """
        self._driver_path = driver_path
        self._port = self.driverInfo["port"] if "port" in self.driverInfo else self._port

        @self.configuredEntities.events.on(uc.EVENTS.ENTITY_ATTRIBUTES_UPDATED)
        async def event_handler(entity_id, entity_type, attributes):
            data = {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "attributes": attributes,
            }

            await self._broadcast_event(uc.MSG_EVENTS.ENTITY_CHANGE, data, uc.EVENT_CATEGORY.ENTITY)

        # Load driver config
        with open(self._driver_path, "r", encoding="utf-8") as file:
            self.driverInfo = json.load(file)

        # Set driver URL
        # TODO verify _get_driver_url: logic might not be correct,
        #      move all parameter logic inside method to better understand what this does
        self.driverInfo["driver_url"] = self._get_driver_url(
            self.driverInfo["driver_url"] if "driver_url" in self.driverInfo else self._interface, self._port
        )

        # Set driver name
        name = _get_default_language_string(self.driverInfo["name"], "Unknown driver")
        # TODO there seems to be missing something with `url`
        # url = self._interface

        addr = socket.gethostbyname(socket.gethostname()) if self.driverInfo["driver_url"] is None else self._interface

        if self._disable_mdns_publish is False:
            # Setup zeroconf service info
            info = AsyncServiceInfo(
                "_uc-integration._tcp.local.",
                f"{self.driverInfo['driver_id']}._uc-integration._tcp.local.",
                addresses=[addr],
                port=int(self._port),
                properties={
                    "name": name,
                    "ver": self.driverInfo["version"],
                    "developer": self.driverInfo["developer"]["name"],
                },
            )
            zeroconf = AsyncZeroconf(ip_version=IPVersion.V4Only)
            await zeroconf.async_register_service(info)

        self._server_task = self._loop.create_task(self._start_web_socket_server())

        LOG.info(
            "Driver is up: %s, version: %s, listening on: %s",
            self.driverInfo["driver_id"],
            self.driverInfo["version"],
            self.driverInfo["driver_url"],
        )

    def _get_driver_url(self, driver_url: str | None, port: int | str) -> str | None:
        if driver_url is not None:
            if driver_url.startswith("ws://") or driver_url.startswith("wss://"):
                return driver_url

            return "ws://" + self._interface + ":" + port

        return None

    async def _start_web_socket_server(self):
        async with websockets.serve(self._handle_ws, self._interface, int(self._port)):
            await asyncio.Future()

    async def _handle_ws(self, websocket):
        try:
            self._clients.add(websocket)
            LOG.info("WS: Client added")

            # authenticate on connection
            await self._authenticate(websocket, True)

            async for message in websocket:
                # process message
                await self._process_ws_message(websocket, message)

        except websockets.ConnectionClosedOK:
            LOG.info("WS: Connection Closed")

        except websockets.exceptions.ConnectionClosedError:
            LOG.info("WS: Connection Closed")

        finally:
            self._clients.remove(websocket)
            LOG.info("WS: Client removed")
            self.events.emit(uc.EVENTS.DISCONNECT)

    async def _send_ok_result(self, websocket, req_id, msg_data={}):
        await self._send_response(websocket, req_id, "result", msg_data, 200)

    async def _send_error_result(self, websocket, req_id, status_code=500, msg_data={}):
        await self._send_response(websocket, req_id, "result", msg_data, status_code)

    async def _send_response(self, websocket, req_id, msg, msg_data, status_code=uc.STATUS_CODES.OK):
        data = {
            "kind": "resp",
            "req_id": req_id,
            "code": int(status_code),
            "msg": msg,
            "msg_data": msg_data,
        }

        if websocket in self._clients:
            data_dump = json.dumps(data)
            LOG.debug("->: %s", data_dump)
            await websocket.send(data_dump)
        else:
            LOG.error("Error sending response: connection no longer established")

    async def _broadcast_event(self, msg, msg_data, category):
        data = {"kind": "event", "msg": msg, "msg_data": msg_data, "cat": category}

        for websocket in self._clients:
            data_dump = json.dumps(data)
            LOG.debug("->: %s", data_dump)
            await websocket.send(data_dump)

    async def _send_event(self, websocket, msg, msg_data, category):
        data = {"kind": "event", "msg": msg, "msg_data": msg_data, "cat": category}

        if websocket in self._clients:
            data_dump = json.dumps(data)
            LOG.debug("->: %s", data_dump)
            await websocket.send(data_dump)
        else:
            LOG.error("Error sending event: connection no longer established")

    async def _process_ws_message(self, websocket, message):
        LOG.debug("<-: %s", message)

        data = json.loads(message)
        kind = data["kind"]
        req_id = data["id"] if "id" in data else None
        msg = data["msg"]
        msg_data = data["msg_data"] if "msg_data" in data else None

        if kind == "req":
            if msg == uc.MESSAGES.GET_DRIVER_VERSION:
                await self._send_response(websocket, req_id, uc.MSG_EVENTS.DRIVER_VERSION, self.getDriverVersion())
            elif msg == uc.MESSAGES.GET_DEVICE_STATE:
                await self._send_response(websocket, req_id, uc.MSG_EVENTS.DEVICE_STATE, self.state)
            elif msg == uc.MESSAGES.GET_AVAILABLE_ENTITIES:
                available_entities = self.availableEntities.getEntities()
                await self._send_response(
                    websocket,
                    req_id,
                    uc.MSG_EVENTS.AVAILABLE_ENTITIES,
                    {"available_entities": available_entities},
                )
            elif msg == uc.MESSAGES.GET_ENTITY_STATES:
                entity_states = await self.configuredEntities.getStates()
                await self._send_response(
                    websocket,
                    req_id,
                    uc.MSG_EVENTS.ENTITY_STATES,
                    entity_states,
                )
            elif msg == uc.MESSAGES.ENTITY_COMMAND:
                await self._entity_command(websocket, req_id, msg_data)
            elif msg == uc.MESSAGES.SUBSCRIBE_EVENTS:
                await self._subscribe_events(msg_data)
                await self._send_ok_result(websocket, req_id)
            elif msg == uc.MESSAGES.UNSUBSCRIBE_EVENTS:
                await self._unsubscribe_events(msg_data)
                await self._send_ok_result(websocket, req_id)
            elif msg == uc.MESSAGES.GET_DRIVER_METADATA:
                await self._send_response(websocket, req_id, uc.MSG_EVENTS.DRIVER_METADATA, self.driverInfo)
            elif msg == uc.MESSAGES.SETUP_DRIVER:
                await self._setup_driver(websocket, req_id, msg_data)
            elif msg == uc.MESSAGES.SET_DRIVER_USER_DATA:
                await self._set_driver_user_data(websocket, req_id, msg_data)

        elif kind == "event":
            if msg == uc.MSG_EVENTS.CONNECT:
                self.events.emit(uc.EVENTS.CONNECT)
            elif msg == uc.MSG_EVENTS.DISCONNECT:
                self.events.emit(uc.EVENTS.DISCONNECT)
            elif msg == uc.MSG_EVENTS.ENTER_STANDBY:
                self.events.emit(uc.EVENTS.ENTER_STANDBY)
            elif msg == uc.MSG_EVENTS.EXIT_STANDBY:
                self.events.emit(uc.EVENTS.EXIT_STANDBY)
            elif msg == uc.MSG_EVENTS.ABORT_DRIVER_SETUP:
                self.events.emit(uc.EVENTS.SETUP_DRIVER_ABORT)

    async def _authenticate(self, websocket, success):
        await self._send_response(
            websocket,
            0,
            uc.MESSAGES.AUTHENTICATION,
            {},
            uc.STATUS_CODES.OK if success else uc.STATUS_CODES.UNAUTHORIZED,
        )

    def getDriverVersion(self):
        return {
            "name": self.driverInfo["name"]["en"],
            "version": {
                "api": self.driverInfo["min_core_api"],
                "driver": self.driverInfo["version"],
            },
        }

    async def setDeviceState(self, state):
        self.state = state

        await self._broadcast_event(uc.MSG_EVENTS.DEVICE_STATE, {"state": self.state}, uc.EVENT_CATEGORY.DEVICE)

    async def _subscribe_events(self, subscribe):
        for entityId in subscribe["entity_ids"]:
            entity = self.availableEntities.getEntity(entityId)
            if entity is not None:
                self.configuredEntities.addEntity(entity)
            else:
                LOG.warning(
                    "WARN: cannot subscribe entity %s: entity is not available",
                    entityId,
                )

        self.events.emit(uc.EVENTS.SUBSCRIBE_ENTITIES, subscribe["entity_ids"])

    async def _unsubscribe_events(self, unsubscribe):
        res = True

        for entityId in unsubscribe["entity_ids"]:
            if self.configuredEntities.removeEntity(entityId) is False:
                res = False

        self.events.emit(uc.EVENTS.UNSUBSCRIBE_ENTITIES, unsubscribe["entity_ids"])

        return res

    async def _entity_command(self, websocket, req_id, msg_data):
        self.events.emit(
            uc.EVENTS.ENTITY_COMMAND,
            websocket,
            req_id,
            msg_data["entity_id"],
            msg_data["entity_type"],
            msg_data["cmd_id"],
            msg_data["params"] if "params" in msg_data else None,
        )

    async def _setup_driver(self, websocket, req_id, data):
        self.events.emit(uc.EVENTS.SETUP_DRIVER, websocket, req_id, data["setup_data"])

    async def _set_driver_user_data(self, websocket, req_id, data):
        if "input_values" in data:
            self.events.emit(uc.EVENTS.SETUP_DRIVER_USER_DATA, websocket, req_id, data["input_values"])
        elif "confirm" in data:
            self.events.emit(uc.EVENTS.SETUP_DRIVER_USER_CONFIRMATION, websocket, req_id, data=None)
        else:
            LOG.warning("Unsupported set_driver_user_data payload received")

    async def acknowledgeCommand(self, websocket, req_id, status_code=uc.STATUS_CODES.OK):
        await self._send_response(websocket, req_id, "result", {}, status_code)

    async def driverSetupProgress(self, websocket):
        data = {"event_type": "SETUP", "state": "SETUP"}

        await self._send_event(websocket, uc.MSG_EVENTS.DRIVER_SETUP_CHANGE, data, uc.EVENT_CATEGORY.DEVICE)

    async def requestDriverSetupUserConfirmation(self, websocket, title, msg1=None, image=None, msg2=None):
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

        await self._send_event(websocket, uc.MSG_EVENTS.DRIVER_SETUP_CHANGE, data, uc.EVENT_CATEGORY.DEVICE)

    async def requestDriverSetupUserInput(self, websocket, title, settings):
        data = {
            "event_type": "SETUP",
            "state": "WAIT_USER_ACTION",
            "require_user_action": {"input": {"title": _to_language_object(title), "settings": settings}},
        }

        await self._send_event(websocket, uc.MSG_EVENTS.DRIVER_SETUP_CHANGE, data, uc.EVENT_CATEGORY.DEVICE)

    async def driverSetupComplete(self, websocket):
        data = {"event_type": "STOP", "state": "OK"}

        await self._send_event(websocket, uc.MSG_EVENTS.DRIVER_SETUP_CHANGE, data, uc.EVENT_CATEGORY.DEVICE)

    async def driverSetupError(self, websocket, error="OTHER"):
        data = {"event_type": "STOP", "state": "ERROR", "error": error}

        await self._send_event(websocket, uc.MSG_EVENTS.DRIVER_SETUP_CHANGE, data, uc.EVENT_CATEGORY.DEVICE)


def _to_language_object(text):
    if text is None:
        return None
    if isinstance(text, str):
        return {"en": text}

    return text


def _get_default_language_string(text, default_text="Undefined"):
    if text is None:
        return default_text

    if "en" in text:
        return text["en"]

    for index, key, value in text.items():
        if index == 0:
            default_text = value

        if key.startswith("en-"):
            return text[key]

    return default_text
