"""
Integration driver API for Remote Two/3.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import json
import logging
import os
import socket
from asyncio import AbstractEventLoop
from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any, Callable

import websockets
from pyee.asyncio import AsyncIOEventEmitter

# Note: websockets v14 doesn't have websockets.server anymore
from websockets import serve

# workaround for pylint error: E0611: No name 'ConnectionClosedOK' in module 'websockets' (no-name-in-module)  # noqa
from websockets.exceptions import ConnectionClosedOK
from zeroconf import IPVersion
from zeroconf.asyncio import AsyncServiceInfo, AsyncZeroconf

from . import api_definitions as uc
from .entities import Entities
from .entity import EntityTypes
from .media_player import Attributes as MediaAttr

# Classes are dynamically created at runtime using the Google Protobuf builder pattern.
# pylint: disable=no-name-in-module
from .proto.ucr_integration_voice_pb2 import (
    IntegrationMessage,
    RemoteVoiceBegin,
    RemoteVoiceData,
    RemoteVoiceEnd,
)
from .voice_assistant import (
    DEFAULT_AUDIO_CHANNELS,
    DEFAULT_SAMPLE_FORMAT,
    DEFAULT_SAMPLE_RATE,
    AudioConfiguration,
)
from .voice_assistant import Commands as VaCommands
from .voice_stream import (
    VoiceEndReason,
    VoiceSession,
    VoiceSessionKey,
    VoiceStreamHandler,
)

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.DEBUG)


@dataclass(slots=True)
class _VoiceSessionContext:
    session: VoiceSession
    timeout_task: asyncio.Task | None = None
    handler_task: asyncio.Task | None = None


# pylint: disable=too-many-public-methods, too-many-lines
class IntegrationAPI:
    """Integration API to communicate with Remote Two/3."""

    DEFAULT_VOICE_SESSION_TIMEOUT_S: int = 30

    def __init__(self, loop: AbstractEventLoop | None = None):
        """
        Create an integration driver API instance.

        :param loop: optional event loop. The currently running event loop is used if
                     not provided.
        """
        self._loop = loop if loop else asyncio.get_event_loop()
        self._events = AsyncIOEventEmitter(self._loop)

        self._setup_handler: uc.SetupHandler | None = None
        self._driver_info: dict[str, Any] = {}
        self._driver_path: str | None = None
        self._state: uc.DeviceStates = uc.DeviceStates.DISCONNECTED

        self._server_task = None
        self._clients = set()

        self._config_dir_path = self._resolve_config_dir()

        self._available_entities = Entities("available", self._loop)
        self._configured_entities = Entities("configured", self._loop)

        self._voice_handler: VoiceStreamHandler | None = None
        self._voice_session_timeout: int = self.DEFAULT_VOICE_SESSION_TIMEOUT_S
        # Active voice sessions
        self._voice_sessions: dict[VoiceSessionKey, _VoiceSessionContext] = {}
        # Enforce: at most one active session per entity_id (across all websockets)
        self._voice_session_by_entity: dict[str, VoiceSessionKey] = {}

        # Setup event loop
        asyncio.set_event_loop(self._loop)

    @staticmethod
    def _resolve_config_dir() -> str:
        return os.getenv("UC_CONFIG_HOME") or os.getenv("HOME") or "./"

    @staticmethod
    def _voice_key(websocket: Any, session_id: int) -> VoiceSessionKey:
        return websocket, int(session_id)

    async def init(
        self, driver_path: str, setup_handler: uc.SetupHandler | None = None
    ):
        """
        Load driver configuration and start integration-API WebSocket server.

        :param driver_path: path to configuration file
        :param setup_handler: optional driver setup handler if the driver metadata
               contains a setup_data_schema object
        """
        self._driver_path = driver_path
        self._setup_handler = setup_handler

        self._configured_entities.add_listener(
            uc.Events.ENTITY_ATTRIBUTES_UPDATED, self._on_entity_attributes_updated
        )

        # Load driver config
        with open(self._driver_path, "r", encoding="utf-8") as file:
            self._driver_info = json.load(file)

        # publishing interface, defaults to "0.0.0.0" if not set
        interface = os.getenv("UC_INTEGRATION_INTERFACE")
        if os.getenv("UC_INTEGRATION_HTTP_PORT"):
            port = int(os.getenv("UC_INTEGRATION_HTTP_PORT"))
        else:
            port = self._driver_info["port"] if "port" in self._driver_info else 9090

        _adjust_driver_url(self._driver_info, port)

        disable_mdns_publish = os.getenv(
            "UC_DISABLE_MDNS_PUBLISH", "false"
        ).lower() in ("true", "1")

        if disable_mdns_publish is False:
            # Setup zeroconf service info
            name = f'{self._driver_info["driver_id"]}._uc-integration._tcp.local.'
            hostname = local_hostname()
            driver_name = _get_default_language_string(
                self._driver_info["name"], "Unknown driver"
            )

            _LOG.debug("Publishing driver: name=%s, host=%s:%d", name, hostname, port)

            info = AsyncServiceInfo(
                "_uc-integration._tcp.local.",
                name,
                addresses=[interface] if interface else None,
                port=port,
                properties={
                    "name": driver_name,
                    "ver": self._driver_info["version"],
                    "developer": self._driver_info["developer"]["name"],
                },
                server=hostname,
            )
            zeroconf = AsyncZeroconf(ip_version=IPVersion.V4Only)
            await zeroconf.async_register_service(info)

        host = interface if interface is not None else "0.0.0.0"
        self._server_task = self._loop.create_task(
            self._start_web_socket_server(host, port)
        )

        _LOG.info(
            "Driver is up: %s, version: %s, api: %s, listening on: %s:%d",
            self._driver_info["driver_id"],
            self._driver_info["version"],
            __version__,
            host,
            port,
        )

    async def _on_entity_attributes_updated(self, entity_id, entity_type, attributes):
        data = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "attributes": attributes,
        }

        await self._broadcast_ws_event(
            uc.WsMsgEvents.ENTITY_CHANGE, data, uc.EventCategory.ENTITY
        )

    async def _start_web_socket_server(self, host: str, port: int) -> None:
        async with serve(self._handle_ws, host, port):
            await asyncio.Future()

    async def _handle_ws(self, websocket) -> None:
        try:
            self._clients.add(websocket)
            _LOG.info("WS: Client added: %s", websocket.remote_address)

            # authenticate on connection
            await self._authenticate(websocket, True)

            self._events.emit(uc.Events.CLIENT_CONNECTED)

            async for message in websocket:
                # Distinguish between text (str) and binary (bytes-like) messages
                if isinstance(message, str):
                    # JSON text message
                    await self._process_ws_message(websocket, message)
                elif isinstance(message, (bytes, bytearray, memoryview)):
                    # Binary message (protobuf in future)
                    await self._process_ws_binary_message(websocket, bytes(message))
                else:
                    _LOG.warning(
                        "[%s] WS: Unsupported message type %s",
                        websocket.remote_address,
                        type(message).__name__,
                    )

        except ConnectionClosedOK:
            _LOG.info("[%s] WS: Connection closed", websocket.remote_address)

        except websockets.exceptions.ConnectionClosedError as e:
            # no idea why they made code & reason deprecated...
            _LOG.info(
                "[%s] WS: Connection closed with error %d: %s",
                websocket.remote_address,
                e.code,
                e.reason,
            )

        except websockets.exceptions.WebSocketException as e:
            _LOG.error(
                "[%s] WS: Connection closed due to processing error: %s",
                websocket.remote_address,
                e,
            )

        finally:
            # Cleanup any active voice sessions associated with this websocket
            keys_to_cleanup = [k for k in self._voice_sessions if k[0] is websocket]
            for key in keys_to_cleanup:
                try:
                    await self._cleanup_voice_session(key, VoiceEndReason.REMOTE)
                except Exception as ex:  # pylint: disable=W0718
                    _LOG.exception(
                        "[%s] WS: Error during voice session cleanup for session_id=%s: %s",
                        websocket.remote_address,
                        key[1],
                        ex,
                    )

            self._clients.remove(websocket)
            _LOG.info("[%s] WS: Client removed", websocket.remote_address)
            self._events.emit(uc.Events.CLIENT_DISCONNECTED)

    async def _send_ok_result(
        self, websocket, req_id: int, msg_data: dict[str, Any] | list | None = None
    ) -> None:
        """
        Send a WebSocket success message with status code OK.

        :param websocket: client connection
        :param req_id: request message identifier
        :param msg_data: message data payload

        Raises:
            websockets.ConnectionClosed: When the connection is closed.
        """
        await self._send_ws_response(
            websocket, req_id, "result", msg_data, uc.StatusCodes.OK
        )

    async def _send_error_result(
        self,
        websocket,
        req_id: int,
        status_code: uc.StatusCodes = uc.StatusCodes.SERVER_ERROR,
        msg_data: dict[str, Any] | None = None,
    ) -> None:
        """
        Send a WebSocket error response message.

        :param websocket: client connection
        :param req_id: request message identifier
        :param status_code: status code
        :param msg_data: message data payload

        Raises:
            websockets.ConnectionClosed: When the connection is closed.
        """
        await self._send_ws_response(websocket, req_id, "result", msg_data, status_code)

    # pylint: disable=R0917
    async def _send_ws_response(
        self,
        websocket,
        req_id: int,
        msg: str,
        msg_data: dict[str, Any] | list | None,
        status_code: uc.StatusCodes = uc.StatusCodes.OK,
    ) -> None:
        """
        Send a WebSocket response message.

        :param websocket: client connection
        :param req_id: request message identifier
        :param msg: message name
        :param msg_data: message data payload
        :param status_code: status code

        Raises:
            websockets.ConnectionClosed: When the connection is closed.
        """
        data = {
            "kind": "resp",
            "req_id": req_id,
            "code": int(status_code),
            "msg": msg,
            "msg_data": msg_data if msg_data is not None else {},
        }

        if websocket in self._clients:
            data_dump = json.dumps(data)
            if _LOG.isEnabledFor(logging.DEBUG):
                _LOG.debug(
                    "[%s] ->: %s", websocket.remote_address, filter_log_msg_data(data)
                )
            await websocket.send(data_dump)
        else:
            _LOG.error("Error sending response: connection no longer established")

    async def _broadcast_ws_event(
        self, msg: str, msg_data: dict[str, Any], category: uc.EventCategory
    ) -> None:
        """
        Send the given event-message to all connected WebSocket clients.

        If a client is no longer connected, a log message is printed and the remaining
        clients are notified.

        :param msg: event message name
        :param msg_data: message data payload
        :param category: event category
        """
        data = {"kind": "event", "msg": msg, "msg_data": msg_data, "cat": category}
        data_dump = json.dumps(data)

        for websocket in self._clients.copy():
            if _LOG.isEnabledFor(logging.DEBUG):
                _LOG.debug(
                    "[%s] =>: %s", websocket.remote_address, filter_log_msg_data(data)
                )
            try:
                await websocket.send(data_dump)
            except websockets.exceptions.WebSocketException:
                pass

    async def _send_ws_event(
        self, websocket, msg: str, msg_data: dict[str, Any], category: uc.EventCategory
    ) -> None:
        """
        Send an event-message to the given WebSocket client.

        :param websocket: client connection
        :param msg: event message name
        :param msg_data: message data payload
        :param category: event category

        Raises:
            websockets.ConnectionClosed: When the connection is closed.
        """
        data = {"kind": "event", "msg": msg, "msg_data": msg_data, "cat": category}
        data_dump = json.dumps(data)

        if websocket in self._clients:
            if _LOG.isEnabledFor(logging.DEBUG):
                _LOG.debug(
                    "[%s] ->: %s", websocket.remote_address, filter_log_msg_data(data)
                )
            await websocket.send(data_dump)
        else:
            _LOG.error("Error sending event: connection no longer established")

    async def _process_ws_message(self, websocket, message) -> None:
        _LOG.debug("[%s] <-: %s", websocket.remote_address, message)

        data = json.loads(message)
        kind = data["kind"]
        req_id = data["id"] if "id" in data else None
        msg = data["msg"]
        msg_data = data["msg_data"] if "msg_data" in data else None

        if kind == "req":
            if req_id is None:
                _LOG.warning(
                    "Ignoring request message with missing 'req_id': %s", message
                )
            else:
                await self._handle_ws_request_msg(websocket, msg, req_id, msg_data)
        elif kind == "event":
            await self._handle_ws_event_msg(msg, msg_data)

    async def _process_ws_binary_message(self, websocket, data: bytes) -> None:
        """Process a binary WebSocket message using protobuf IntegrationMessage.

        - Deserializes ``IntegrationMessage`` from the incoming bytes.
        - Dispatches to specific handlers based on the concrete oneof field.
        - Logs errors on deserialization failures and unknown message kinds.
        """
        if _LOG.isEnabledFor(logging.DEBUG):
            _LOG.debug(
                "[%s] <-: <binary %d bytes>", websocket.remote_address, len(data)
            )

        # Parse IntegrationMessage from bytes
        try:
            imsg = IntegrationMessage()
            imsg.ParseFromString(data)
        except Exception as ex:  # pylint: disable=W0718
            _LOG.error(
                "[%s] proto: Failed to parse IntegrationMessage (%d bytes): %s",
                websocket.remote_address,
                len(data),
                ex,
            )
            return

        kind = imsg.WhichOneof("message")
        if kind == "voice_begin":
            await self._on_remote_voice_begin(websocket, imsg.voice_begin)
        elif kind == "voice_data":
            await self._on_remote_voice_data(websocket, imsg.voice_data)
        elif kind == "voice_end":
            await self._on_remote_voice_end(websocket, imsg.voice_end)
        else:
            # Either empty oneof or a newer message type unknown to this client
            _LOG.info(
                "[%s] proto: Received unsupported or unknown IntegrationMessage: %s",
                websocket.remote_address,
                kind,
            )

    async def _on_remote_voice_begin(self, websocket, msg: RemoteVoiceBegin) -> None:
        """Handle a RemoteVoiceBegin protobuf message.

        Behavior:
        - If no voice handler is registered: log a concise info line and ignore
          the stream (drop subsequent data/end silently).
        - If a handler is registered: create a VoiceSession and invoke the
          handler in the background.
        """
        if self._voice_handler is None:
            # Log once per stream and ignore further binary messages.
            _LOG.warning(
                "[%s] proto VoiceBegin: no voice handler registered! Ignoring voice stream",
                websocket.remote_address,
            )
            return

        session_id = int(getattr(msg, "session_id", 0) or 0)
        key = self._voice_key(websocket, session_id)
        ctx = self._voice_sessions.get(key)
        if ctx is None:
            _LOG.error(
                "[%s] proto VoiceBegin: no voice session for session_id=%s",
                websocket.remote_address,
                session_id,
            )
            return

        session = ctx.session

        # verify AudioConfiguration in session from voice_start command
        cfg = getattr(msg, "configuration", None)
        audio_cfg = AudioConfiguration.from_proto(cfg) or AudioConfiguration()
        if audio_cfg != session.config:
            _LOG.error(
                "[%s] proto VoiceBegin: audio cfg does not match voice_start",
                websocket.remote_address,
            )
            return

        if _LOG.isEnabledFor(logging.DEBUG):
            _LOG.debug(
                "[%s] proto VoiceBegin: session_id=%s cfg(ch=%s sr=%s fmt=%s)",
                websocket.remote_address,
                session.session_id,
                session.config.channels,
                session.config.sample_rate,
                session.config.sample_format,
            )

        # Invoke handler in the background so the WS loop is not blocked
        ctx.handler_task = self._loop.create_task(self._run_voice_handler(session))

    async def _on_remote_voice_data(self, websocket, msg: RemoteVoiceData) -> None:
        """Handle a RemoteVoiceData protobuf message.

        If no voice handler is registered, this function returns immediately
        without logging to avoid noise (as per default behavior).
        """
        if self._voice_handler is None:
            # already logged in RemoteVoiceBegin
            return

        session_id = int(getattr(msg, "session_id", 0) or 0)
        key = self._voice_key(websocket, session_id)
        ctx = self._voice_sessions.get(key)
        if ctx is None:
            _LOG.error(
                "[%s] proto VoiceData: no voice session for session_id=%s",
                websocket.remote_address,
                session_id,
            )
            return

        samples = getattr(msg, "samples", b"") or b""
        if samples:
            try:
                ctx.session.feed(bytes(samples))
            except Exception as ex:  # pylint: disable=W0718
                _LOG.error(
                    "[%s] proto VoiceData: session %s processing error: %s",
                    websocket.remote_address,
                    session_id,
                    ex,
                )

    async def _on_remote_voice_end(self, websocket, msg: RemoteVoiceEnd) -> None:
        """Handle a RemoteVoiceEnd protobuf message.

        If no voice handler is registered, do nothing (default ignore behavior).
        """
        if self._voice_handler is None:
            return
        session_id = int(getattr(msg, "session_id", 0) or 0)
        await self._cleanup_voice_session(self._voice_key(websocket, session_id))

    async def _cleanup_voice_session(
        self,
        key: VoiceSessionKey,
        end_reason: VoiceEndReason = VoiceEndReason.NORMAL,
    ) -> None:
        """Cleanup internal state for a voice session context."""
        ctx = self._voice_sessions.pop(key, None)
        if ctx is None:
            return

        # Cancel timeout task if present
        t = ctx.timeout_task
        if t is not None and not t.done():
            t.cancel()

        # Enforce entity_id uniqueness index cleanup
        if self._voice_session_by_entity.get(ctx.session.entity_id) == key:
            self._voice_session_by_entity.pop(ctx.session.entity_id, None)

        # End session iterator
        if not ctx.session.closed:
            ctx.session.end(end_reason)

        # Note: do not cancel handler task; handler should exit on session.end()
        ctx.handler_task = None

    def set_voice_stream_handler(self, handler: VoiceStreamHandler | None) -> None:
        """Register or clear the voice stream handler.

        Passing ``None`` clears the handler. When no handler is registered,
        binary voice messages are ignored and only the initial begin is logged.
        """
        self._voice_handler = handler

    async def broadcast_assistant_event(self, event: uc.AssistantEvent) -> None:
        """Broadcast an assistant event to all connected WebSocket clients."""
        await self._broadcast_ws_event(
            uc.WsMsgEvents.ASSISTANT_EVENT,
            asdict(event),
            uc.EventCategory.ENTITY,
        )

    async def send_assistant_event(self, client, event: uc.AssistantEvent) -> None:
        """Send an assistant event to the given client connection."""
        await self._send_ws_event(
            client,
            uc.WsMsgEvents.ASSISTANT_EVENT,
            asdict(event),
            uc.EventCategory.ENTITY,
        )

    async def _run_voice_handler(self, session: VoiceSession) -> None:
        """Run the user-provided voice handler safely.

        Accepts both sync and async callables. Ensures session cleanup on exit.
        """
        handler = self._voice_handler
        if handler is None:
            # Handler cleared after session start; just end the session
            session.end(VoiceEndReason.LOCAL)
            return
        try:
            result = handler(session)
            if asyncio.iscoroutine(result):
                await result
        except Exception as ex:  # pylint: disable=W0718
            _LOG.exception("Voice handler failed for session %s", session.session_id)
            if not session.closed:
                session.end(VoiceEndReason.ERROR, ex)
        finally:
            # Ensure iterator is unblocked and session is cleaned up
            await self._cleanup_voice_session(session.session_id)

    def _schedule_voice_timeout(self, key: VoiceSessionKey) -> None:
        """Schedule the timeout task for a voice session.

        Starts counting immediately at creation time. When the timeout expires and the
        session is still active, the handler is notified (invoked) if not already
        started, the session is ended, and cleanup is performed.
        """
        ctx = self._voice_sessions.get(key)
        if ctx is None:
            return

        # Cancel pre-existing task if any (defensive)
        existing = ctx.timeout_task
        if existing is not None and not existing.done():
            existing.cancel()

        ctx.timeout_task = self._loop.create_task(self._voice_session_timeout_task(key))

    async def _voice_session_timeout_task(self, key: VoiceSessionKey) -> None:
        """Timeout watchdog for a voice session."""
        try:
            await asyncio.sleep(self._voice_session_timeout)
        except asyncio.CancelledError:
            return

        # If still active after timeout; take action
        ctx = self._voice_sessions.get(key)
        if ctx is None:
            return

        _LOG.warning(
            "Voice session %s timed out after %ss",
            ctx.session.session_id,
            self._voice_session_timeout,
        )

        # If handler not started yet, start it now (best effort)
        if ctx.handler_task is None and self._voice_handler is not None:
            try:
                ctx.handler_task = self._loop.create_task(
                    self._run_voice_handler(ctx.session)
                )
            except Exception:  # pylint: disable=W0718
                _LOG.exception(
                    "Failed to start voice handler on timeout for session %s",
                    ctx.session.session_id,
                )

        # End and cleanup
        ctx.session.end(VoiceEndReason.TIMEOUT)
        await self._cleanup_voice_session(key)

    async def _handle_ws_request_msg(
        self, websocket, msg: str, req_id: int, msg_data: dict[str, Any] | None
    ) -> None:
        if msg == uc.WsMessages.GET_DRIVER_VERSION:
            await self._send_ws_response(
                websocket,
                req_id,
                uc.WsMsgEvents.DRIVER_VERSION,
                self.get_driver_version(),
            )
        elif msg == uc.WsMessages.GET_DEVICE_STATE:
            await self._send_ws_response(
                websocket,
                req_id,
                uc.WsMsgEvents.DEVICE_STATE,
                {"state": self.device_state},
            )
        elif msg == uc.WsMessages.GET_AVAILABLE_ENTITIES:
            available_entities = self._available_entities.get_all()
            await self._send_ws_response(
                websocket,
                req_id,
                uc.WsMsgEvents.AVAILABLE_ENTITIES,
                {"available_entities": available_entities},
            )
        elif msg == uc.WsMessages.GET_ENTITY_STATES:
            entity_states = await self._configured_entities.get_states()
            await self._send_ws_response(
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
            await self._send_ws_response(
                websocket, req_id, uc.WsMsgEvents.DRIVER_METADATA, self._driver_info
            )
        elif msg == uc.WsMessages.SETUP_DRIVER:
            if not await self._setup_driver(websocket, req_id, msg_data):
                # sleep for web-configurator quirks...
                await asyncio.sleep(0.5)
                await self.driver_setup_error(websocket)
        elif msg == uc.WsMessages.SET_DRIVER_USER_DATA:
            if not await self._set_driver_user_data(websocket, req_id, msg_data):
                await asyncio.sleep(0.5)
                await self.driver_setup_error(websocket)

    async def _handle_ws_event_msg(
        self, msg: str, msg_data: dict[str, Any] | None
    ) -> None:
        if msg == uc.WsMsgEvents.CONNECT:
            self._events.emit(uc.Events.CONNECT)
        elif msg == uc.WsMsgEvents.DISCONNECT:
            self._events.emit(uc.Events.DISCONNECT)
        elif msg == uc.WsMsgEvents.ENTER_STANDBY:
            self._events.emit(uc.Events.ENTER_STANDBY)
        elif msg == uc.WsMsgEvents.EXIT_STANDBY:
            self._events.emit(uc.Events.EXIT_STANDBY)
        elif msg == uc.WsMsgEvents.ABORT_DRIVER_SETUP:
            if not self._setup_handler:
                _LOG.warning(
                    "Received abort_driver_setup event, but no setup handler provided by the driver!"
                )  # noqa
                return

            if "error" in msg_data:
                try:
                    error = uc.IntegrationSetupError[msg_data["error"]]
                except KeyError:
                    error = uc.IntegrationSetupError.OTHER
                await self._setup_handler(uc.AbortDriverSetup(error))
            else:
                _LOG.warning(
                    "Unsupported abort_driver_setup payload received: %s", msg_data
                )

    async def _authenticate(self, websocket, success: bool) -> None:
        await self._send_ws_response(
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

    async def set_device_state(self, state: uc.DeviceStates) -> None:
        """
        Set new device state and notify all connected clients.

        Attention: clients are always notified, even if the current state is the same as
        the new state!
        """
        self._state = state

        await self._broadcast_ws_event(
            uc.WsMsgEvents.DEVICE_STATE,
            {"state": self.device_state},
            uc.EventCategory.DEVICE,
        )

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

    async def _entity_command(
        self, websocket, req_id: int, msg_data: dict[str, Any] | None
    ) -> None:
        if not msg_data:
            _LOG.warning("Ignoring entity command: called with empty msg_data")
            await self.acknowledge_command(
                websocket, req_id, uc.StatusCodes.BAD_REQUEST
            )
            return

        entity_id = msg_data["entity_id"] if "entity_id" in msg_data else None
        cmd_id = msg_data["cmd_id"] if "cmd_id" in msg_data else None
        if entity_id is None or cmd_id is None:
            _LOG.warning("Ignoring command: missing entity_id or cmd_id")
            await self.acknowledge_command(
                websocket, req_id, uc.StatusCodes.BAD_REQUEST
            )
            return

        entity = self.configured_entities.get(entity_id)
        if entity is None:
            _LOG.warning(
                "Cannot execute command '%s' for '%s': no configured entity found",
                cmd_id,
                entity_id,
            )
            await self.acknowledge_command(websocket, req_id, uc.StatusCodes.NOT_FOUND)
            return

        if (
            entity.entity_type == EntityTypes.VOICE_ASSISTANT
            and cmd_id == VaCommands.VOICE_START
            and "params" in msg_data
        ):
            params = msg_data["params"]
            session_id = int(params.get("session_id"))
            cfg = params.get("audio_cfg")
            audio_cfg = (
                AudioConfiguration(
                    channels=cfg.get("channels", DEFAULT_AUDIO_CHANNELS),
                    sample_rate=cfg.get("sample_rate", DEFAULT_SAMPLE_RATE),
                    sample_format=cfg.get("sample_format", DEFAULT_SAMPLE_FORMAT),
                )
                if cfg
                else AudioConfiguration()
            )

            # Enforce: only one active session per entity_id across all websockets
            existing_key = self._voice_session_by_entity.get(entity_id)
            if existing_key is not None:
                await self._cleanup_voice_session(existing_key, VoiceEndReason.LOCAL)

            key = self._voice_key(websocket, session_id)
            session = VoiceSession(
                session_id,
                entity_id,
                audio_cfg,
                api=self,
                websocket=websocket,
                loop=self._loop,
            )
            self._voice_sessions[key] = _VoiceSessionContext(session=session)
            self._voice_session_by_entity[entity_id] = key

            # Start timeout immediately on session creation
            self._schedule_voice_timeout(key)

        try:
            result = await entity.command(
                cmd_id,
                msg_data["params"] if "params" in msg_data else None,
                websocket=websocket,
            )
        except TypeError:
            # Entity command method likely doesn't accept 'websocket' kwarg -> legacy handler signature.
            _LOG.warning(
                "Old Entity.command signature detected for %s, trying old signature. Please update the command signature.",
                entity.id,
            )
            result = await entity.command(
                cmd_id, msg_data["params"] if "params" in msg_data else None
            )

        await self.acknowledge_command(websocket, req_id, result)

    async def _setup_driver(
        self, websocket, req_id: int, msg_data: dict[str, Any] | None
    ) -> bool:
        await self.acknowledge_command(websocket, req_id)

        if msg_data is None or "setup_data" not in msg_data:
            _LOG.warning("Aborting setup_driver: called with empty msg_data")
            # Returning False will show a setup error in the setup flow process
            return False

        # make sure integration driver installed a setup handler
        if not self._setup_handler:
            _LOG.error(
                "Received setup_driver request, but no setup handler provided by the driver!"
            )  # noqa
            return False

        result = False
        try:
            action = await self._setup_handler(
                uc.DriverSetupRequest(
                    msg_data.get("reconfigure") or False, msg_data["setup_data"]
                )
            )

            if isinstance(action, uc.RequestUserInput):
                await self.driver_setup_progress(websocket)
                await self.request_driver_setup_user_input(
                    websocket, action.title, action.settings
                )
                result = True
            elif isinstance(action, uc.RequestUserConfirmation):
                await self.driver_setup_progress(websocket)
                await self.request_driver_setup_user_confirmation(
                    websocket, action.title, action.header, action.image, action.footer
                )
                result = True
            elif isinstance(action, uc.SetupComplete):
                await self.driver_setup_complete(websocket)
                result = True
            elif isinstance(action, uc.SetupError):
                await self.driver_setup_error(websocket, action.error_type)
                result = True

        # TODO define custom exceptions?
        except Exception as ex:  # pylint: disable=W0718
            _LOG.error("Exception in setup handler, aborting setup! Exception: %s", ex)

        return result

    async def _set_driver_user_data(
        self, websocket, req_id: int, msg_data: dict[str, Any] | None
    ) -> bool:
        await self.acknowledge_command(websocket, req_id)

        if not self._setup_handler:
            _LOG.error(
                "Received set_driver_user_data request, but no setup handler provided by the driver!"
            )  # noqa
            return False

        if "input_values" in msg_data or "confirm" in msg_data:
            # please don't ask, there's some funky stuff in the web-configurator :-(
            await asyncio.sleep(0.5)
            await self.driver_setup_progress(websocket)
        else:
            _LOG.warning(
                "Unsupported set_driver_user_data payload received: %s", msg_data
            )
            return False

        result = False
        try:
            action = uc.SetupError()
            if "input_values" in msg_data:
                action = await self._setup_handler(
                    uc.UserDataResponse(msg_data["input_values"])
                )
            elif "confirm" in msg_data:
                action = await self._setup_handler(
                    uc.UserConfirmationResponse(msg_data["confirm"])
                )

            if isinstance(action, uc.RequestUserInput):
                await self.request_driver_setup_user_input(
                    websocket, action.title, action.settings
                )
                result = True
            elif isinstance(action, uc.RequestUserConfirmation):
                await self.request_driver_setup_user_confirmation(
                    websocket, action.title, action.header, action.image, action.footer
                )
                result = True
            elif isinstance(action, uc.SetupComplete):
                await self.driver_setup_complete(websocket)
                result = True
            elif isinstance(action, uc.SetupError):
                await self.driver_setup_error(websocket, action.error_type)
                result = True

        # TODO define custom exceptions?
        except Exception as ex:  # pylint: disable=W0718
            _LOG.error("Exception in setup handler, aborting setup! Exception: %s", ex)

        return result

    async def acknowledge_command(
        self, websocket, req_id: int, status_code: uc.StatusCodes = uc.StatusCodes.OK
    ) -> None:
        """
        Acknowledge a command from Remote Two/3.

        :param websocket: client connection
        :param req_id: request message identifier to acknowledge
        :param status_code: status code

        Raises:
            websockets.ConnectionClosed: When the connection is closed.
        """
        await self._send_ws_response(websocket, req_id, "result", {}, status_code)

    async def driver_setup_progress(self, websocket) -> None:
        """
        Send a driver setup progress event to Remote Two/3.

        :param websocket: client connection

        Raises:
            websockets.ConnectionClosed: When the connection is closed.
        """
        data = {"event_type": "SETUP", "state": "SETUP"}

        await self._send_ws_event(
            websocket, uc.WsMsgEvents.DRIVER_SETUP_CHANGE, data, uc.EventCategory.DEVICE
        )

    # pylint: disable=R0917
    async def request_driver_setup_user_confirmation(
        self,
        websocket,
        title: str | dict[str, str],
        msg1: str | dict[str, str] | None = None,
        image: str | None = None,
        msg2: str | dict[str, str] | None = None,
    ) -> None:
        """
        Request a user confirmation during the driver setup process.

        :param websocket: client connection
        :param title: page title
        :param msg1: optional header message
        :param image: optional image between header and footer
        :param msg2: optional footer message

        Raises:
            websockets.ConnectionClosed: When the connection is closed.
        """
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

        await self._send_ws_event(
            websocket, uc.WsMsgEvents.DRIVER_SETUP_CHANGE, data, uc.EventCategory.DEVICE
        )

    async def request_driver_setup_user_input(
        self, websocket, title: str | dict[str, str], settings: dict[str, Any] | list
    ) -> None:
        """Request a user input during the driver setup process."""
        data = {
            "event_type": "SETUP",
            "state": "WAIT_USER_ACTION",
            "require_user_action": {
                "input": {"title": _to_language_object(title), "settings": settings}
            },
        }

        await self._send_ws_event(
            websocket, uc.WsMsgEvents.DRIVER_SETUP_CHANGE, data, uc.EventCategory.DEVICE
        )

    async def driver_setup_complete(self, websocket) -> None:
        """Send a driver setup complete event to Remote Two/3."""
        data = {"event_type": "STOP", "state": "OK"}

        await self._send_ws_event(
            websocket, uc.WsMsgEvents.DRIVER_SETUP_CHANGE, data, uc.EventCategory.DEVICE
        )

    async def driver_setup_error(self, websocket, error="OTHER") -> None:
        """Send a driver setup error event to Remote Two/3."""
        data = {"event_type": "STOP", "state": "ERROR", "error": error}

        await self._send_ws_event(
            websocket, uc.WsMsgEvents.DRIVER_SETUP_CHANGE, data, uc.EventCategory.DEVICE
        )

    def add_listener(self, event: uc.Events, f: Callable) -> None:
        """
        Register a callback handler for the given event.

        :param event: the event
        :param f: callback handler
        """
        self._events.add_listener(event, f)

    def listens_to(self, event: uc.Events) -> Callable[[Callable], Callable]:
        """
        Register the given event.

        :return: a decorator which will register the decorated function to the specified
                 event.
        """

        def on(f: Callable) -> Callable:
            self._events.add_listener(event, f)
            return f

        return on

    def remove_listener(self, event: uc.Events, f: Callable) -> None:
        """
        Remove the callback handler for the given event.

        :param event: the event
        :param f: callback handler
        """
        self._events.remove_listener(event, f)

    def remove_all_listeners(self, event: uc.Events | None) -> None:
        """
        Remove all listeners attached to ``event``.

        If ``event`` is ``None``, remove all listeners on all events.

        :param event: the event
        """
        self._events.remove_all_listeners(event)

    ##############
    # Properties #
    ##############

    @property
    def client_count(self) -> int:
        """Return number of WebSocket clients."""
        return len(self._clients)

    @property
    def device_state(self) -> uc.DeviceStates:
        """
        Return device state.

        Use set_device_state to update the state and notify all clients.
        """
        return self._state

    @property
    def config_dir_path(self) -> str:
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


def _get_default_language_string(
    text: str | dict[str, str] | None, default_text="Undefined"
) -> str:
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


def _adjust_driver_url(driver_info: dict[str, Any], port: int) -> str | None:
    """
    Adjust the driver_url field in the driver metadata.

    By default, the ``driver_url`` is not set in the metadata file. It is used
    to overwrite the published URL by mDNS. UCR2 uses the driver URL from mDNS
    if ``driver_url`` in the metadata file is missing.

    Adjustment:
    - do nothing if driver url isn't set
    - leave driver url as-is if it is starting with ``ws://`` or ``wss://``
    - otherwise dynamically set from determined os hostname and port setting

    :param driver_info: driver metadata
    :param port: WebSocket server port
    :return: adjusted driver url or None
    """
    driver_url = driver_info["driver_url"] if "driver_url" in driver_info else None

    if driver_url is None:
        return None

    if driver_url.startswith("ws://") or driver_url.startswith("wss://"):
        return driver_url

    host = socket.gethostname()
    driver_info["driver_url"] = f"ws://{host}:{port}"
    return driver_info["driver_url"]


def local_hostname() -> str:
    """
    Get the local hostname for mDNS publishing.

    Overridable by environment variable ``UC_MDNS_LOCAL_HOSTNAME``.

    :return: the local hostname
    """
    # Override option for announced hostname.
    # Useful on macOS where it's broken for several years:
    # local hostname keeps on changing with a increasing number suffix!
    # https://apple.stackexchange.com/questions/189350/my-macs-hostname-keeps-adding-a-2-to-the-end

    return (
        os.getenv("UC_MDNS_LOCAL_HOSTNAME")
        or f'{socket.gethostname().split(".", 1)[0]}.local.'
    )


def filter_log_msg_data(data: dict[str, Any]) -> dict[str, Any]:
    """
    Filter attribute fields to exclude for log messages in the given msg data dict.

    - Attributes are filtered in `data["msg_data"]`:
      - dict object: key `attributes`
      - list object: every list item `attributes`
    - Filtered attributes: `MEDIA_IMAGE_URL`

    :param data: the message data dict
    :return: copy of the message data dict with filtered attributes
    """
    # do not modify the original dict
    log_upd = deepcopy(data)
    if not log_upd:
        return {}

    # filter out base64 encoded images in the media player's media_image_url attribute
    if "msg_data" in log_upd:
        if (
            "attributes" in log_upd["msg_data"]
            and MediaAttr.MEDIA_IMAGE_URL in log_upd["msg_data"]["attributes"]
            and (
                media_image_url := log_upd["msg_data"]["attributes"][
                    MediaAttr.MEDIA_IMAGE_URL
                ]
            )
            and media_image_url.startswith("data:")
        ):
            log_upd["msg_data"]["attributes"][MediaAttr.MEDIA_IMAGE_URL] = "data:***"
        elif isinstance(log_upd["msg_data"], list):
            for item in log_upd["msg_data"]:
                if (
                    "attributes" in item
                    and MediaAttr.MEDIA_IMAGE_URL in item["attributes"]
                    and (
                        media_image_url := item["attributes"][MediaAttr.MEDIA_IMAGE_URL]
                    )
                    and media_image_url.startswith("data:")
                ):
                    item["attributes"][MediaAttr.MEDIA_IMAGE_URL] = "data:***"

    return log_upd
