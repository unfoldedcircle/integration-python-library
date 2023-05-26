import asyncio
import websockets
import json
import logging
import os
import socket

from zeroconf import IPVersion
from zeroconf.asyncio import AsyncServiceInfo, AsyncZeroconf

from pyee import AsyncIOEventEmitter

import ucapi.api_definitions as uc
import ucapi.entities as entities

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class IntegrationAPI:
    def __init__(self, loop, type="default"):
        self._loop = loop
        self.events = AsyncIOEventEmitter(self._loop)
        self.driverInfo = {}
        self._driverPath = None
        self.state = uc.DEVICE_STATES.DISCONNECTED
        self._serverTask = None
        self._clients = set()
        
        self._interface = os.getenv('UC_INTEGRATION_INTERFACE')
        self._port = os.getenv('UC_INTEGRATION_HTTP_PORT')

        self.availableEntities = entities.Entities("available", self._loop)
        self.configuredEntities = entities.Entities("configured", self._loop)

        # Setup event loop
        asyncio.set_event_loop(self._loop)

    async def init(self, driverPath):
        self._driverPath = driverPath
        self._port = self.driverInfo["port"] if "port" in self.driverInfo else self._port

        @self.configuredEntities.events.on(uc.EVENTS.ENTITY_ATTRIBUTES_UPDATED)
        async def event_handler(id, entityType, attributes):
            data = {
                "entity_id": id,
                "entity_type": entityType,
                "attributes": attributes,
            }

            await self._broadcastEvent(
                uc.MSG_EVENTS.ENTITY_CHANGE, data, uc.EVENT_CATEGORY.ENTITY
            )

        # Load driver config
        file = open(self._driverPath)
        self.driverInfo = json.load(file)
        file.close()

        # Set driver URL
        self.driverInfo["driver_url"] = self.getDriverUrl(
            self.driverInfo["driver_url"] if "driver_url" in self.driverInfo else self._interface,
            self._port
        )

        # Set driver name
        name = self._getDefaultLanguageString(self.driverInfo["name"], "Unknown driver")
        url = self._interface

        addr = socket.gethostbyname(socket.gethostname()) if self.driverInfo["driver_url"] is None else self._interface

        print(self._port)

        # Setup zeroconf service info
        info = AsyncServiceInfo(
            "_uc-integration._tcp.local.",
            f"{url}._uc-integration._tcp.local.",
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

        self._serverTask = self._loop.create_task(self._startWebSocketServer())

        LOG.info(
            "Driver is up: %s, version: %s, listening on: %s : %s",
            self.driverInfo["driver_id"],
            self.driverInfo["version"],
            self.driverInfo["driver_url"],
            self._port,
        )

    def getDriverUrl(self, driverUrl, port):
        if driverUrl is not None:
            if driverUrl.startswith("ws://") or driverUrl.startswith("wss://"):
                return driverUrl

            return "ws://" + self._interface + ":" + port

        return None

    def _getDefaultLanguageString(self, text, defaultText="Undefined"):
        if text is None:
            return defaultText

        if "en" in text:
            return text["en"]

        for index, key, value in text.items():
            if index is 0:
                defaultText = value

            if key.startswith("en-"):
                return text[key]

        return defaultText

    def _toLanguageObject(self, text):
        if text is None:
            return None
        elif isinstance(text, str):
            return {"en": text}
        else:
            return text

    async def _startWebSocketServer(self):
        async with websockets.serve(self._handleWs, self._interface, int(self._port)):
            await asyncio.Future()

    async def _handleWs(self, websocket):
        try:
            self._clients.add(websocket)
            LOG.info("WS: Client added")

            # authenticate on connection
            await self._authenticate(websocket, True)

            async for message in websocket:
                # process message
                await self._processWsMessage(websocket, message)

        except websockets.ConnectionClosedOK:
            LOG.info("WS: Connection Closed")

        except websockets.exceptions.ConnectionClosedError:
            LOG.info("WS: Connection Closed")

        finally:
            self._clients.remove(websocket)
            LOG.info("WS: Client removed")

    async def _sendOkResult(self, websocket, id, msgData={}):
        await self._sendResponse(websocket, id, "result", msgData, 200)

    async def _sendErrorResult(self, websocket, id, statusCode=500, msgData={}):
        await self._sendResponse(websocket, id, "result", msgData, statusCode)

    async def _sendResponse(
        self, websocket, id, msg, msgData, statusCode=uc.STATUS_CODES.OK
    ):
        data = {
            "kind": "resp",
            "req_id": id,
            "code": int(statusCode),
            "msg": msg,
            "msg_data": msgData,
        }

        if websocket in self._clients:
            dataDump = json.dumps(data)
            LOG.debug("->: " + dataDump)
            await websocket.send(dataDump)
        else:
            LOG.error("Error sending response: connection no longer established")

    async def _broadcastEvent(self, msg, msgData, category):
        data = {"kind": "event", "msg": msg, "msg_data": msgData, "cat": category}

        for websocket in self._clients:
            dataDump = json.dumps(data)
            LOG.debug("->: " + dataDump)
            await websocket.send(dataDump)

    async def _sendEvent(self, websocket, msg, msgData, category):
        data = {"kind": "event", "msg": msg, "msg_data": msgData, "cat": category}

        if websocket in self._clients:
            dataDump = json.dumps(data)
            LOG.debug("->: " + dataDump)
            await websocket.send(dataDump)
        else:
            LOG.error("Error sending event: connection no longer established")

    async def _processWsMessage(self, websocket, message):
        LOG.debug("<-: " + message)

        data = json.loads(message)
        kind = data["kind"]
        id = data["id"] if "id" in data else None
        msg = data["msg"]
        msgData = data["msg_data"] if "msg_data" in data else None

        if kind == "req":
            if msg == uc.MESSAGES.GET_DRIVER_VERSION:
                await self._sendResponse(
                    websocket, id, uc.MSG_EVENTS.DRIVER_VERSION, self.getDriverVersion()
                )
            elif msg == uc.MESSAGES.GET_DEVICE_STATE:
                await self._sendResponse(
                    websocket, id, uc.MSG_EVENTS.DEVICE_STATE, self.state
                )
            elif msg == uc.MESSAGES.GET_AVAILABLE_ENTITIES:
                availableEntities = self.availableEntities.getEntities()
                await self._sendResponse(
                    websocket,
                    id,
                    uc.MSG_EVENTS.AVAILABLE_ENTITIES,
                    {"available_entities": availableEntities},
                )
            elif msg == uc.MESSAGES.GET_ENTITY_STATES:
                entityStates = await self.configuredEntities.getStates()
                await self._sendResponse(
                    websocket,
                    id,
                    uc.MSG_EVENTS.ENTITY_STATES,
                    entityStates,
                )
            elif msg == uc.MESSAGES.ENTITY_COMMAND:
                await self._entityCommand(websocket, id, msgData)
            elif msg == uc.MESSAGES.SUBSCRIBE_EVENTS:
                await self._subscribeEvents(msgData)
                await self._sendOkResult(websocket, id)
            elif msg == uc.MESSAGES.UNSUBSCRIBE_EVENTS:
                await self._unsubscribeEvents(msgData)
                await self._sendOkResult(websocket, id)
            elif msg == uc.MESSAGES.GET_DRIVER_METADATA:
                await self._sendResponse(
                    websocket, id, uc.MSG_EVENTS.DRIVER_METADATA, self.driverInfo
                )
            elif msg == uc.MESSAGES.SETUP_DRIVER:
                await self._setupDriver(websocket, id, msgData)
            elif msg == uc.MESSAGES.SET_DRIVER_USER_DATA:
                await self._setDriverUserData(websocket, id, msgData)

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
        await self._sendResponse(
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

        await self._broadcastEvent(
            uc.MSG_EVENTS.DEVICE_STATE, {"state": self.state}, uc.EVENT_CATEGORY.DEVICE
        )

    async def _subscribeEvents(self, entities):
        for entityId in entities["entity_ids"]:
            entity = self.availableEntities.getEntity(entityId)
            if entity is not None:
                self.configuredEntities.addEntity(entity)
            else:
                LOG.warning(
                    "WARN: cannot subscribe entity %s: entity is not available",
                    entityId,
                )

        self.events.emit(uc.EVENTS.SUBSCRIBE_ENTITIES, entities["entity_ids"])

    async def _unsubscribeEvents(self, entities):
        res = True

        for entityId in entities["entity_ids"]:
            if self.configuredEntities.removeEntity(entityId) is False:
                res = False

        self.events.emit(uc.EVENTS.UNSUBSCRIBE_ENTITIES, entities["entity_ids"])

        return res

    async def _entityCommand(self, websocket, id, msgData):
        self.events.emit(
            uc.EVENTS.ENTITY_COMMAND,
            websocket,
            id,
            msgData["entity_id"],
            msgData["entity_type"],
            msgData["cmd_id"],
            msgData["params"] if "params" in msgData else None,
        )

    async def _setupDriver(self, websocket, id, data):
        self.events.emit(uc.EVENTS.SETUP_DRIVER, websocket, id, data["setup_data"])

    async def _setDriverUserData(self, websocket, id, data):
        if "input_values" in data:
            self.events.emit(
                uc.EVENTS.SETUP_DRIVER_USER_DATA, websocket, id, data["input_values"]
            )
        elif "confirm" in data:
            self.events.emit(
                uc.EVENTS.SETUP_DRIVER_USER_CONFIRMATION, websocket, id, data=None
            )
        else:
            LOG.warning("Unsupported set_driver_user_data payload received")

    async def acknowledgeCommand(self, websocket, id, statusCode=uc.STATUS_CODES.OK):
        await self._sendResponse(websocket, id, "result", {}, statusCode)

    async def driverSetupProgress(self, websocket):
        data = {"event_type": "SETUP", "state": "SETUP"}

        await self._sendEvent(
            websocket, uc.MSG_EVENTS.DRIVER_SETUP_CHANGE, data, uc.EVENT_CATEGORY.DEVICE
        )

    async def requestDriverSetupUserConfirmation(
        self, websocket, title, msg1=None, image=None, msg2=None
    ):
        data = {
            "event_type": "SETUP",
            "state": "WAIT_USER_ACTION",
            "require_user_action": {
                "confirmation": {
                    "title": self._toLanguageObject(title),
                    "message1": self._toLanguageObject(msg1),
                    "image": image,
                    "message2": self._toLanguageObject(msg2),
                }
            },
        }

        await self._sendEvent(
            websocket, uc.MSG_EVENTS.DRIVER_SETUP_CHANGE, data, uc.EVENT_CATEGORY.DEVICE
        )

    async def requestDriverSetupUserInput(self, websocket, title, settings):
        data = {
            "event_type": "SETUP",
            "state": "WAIT_USER_ACTION",
            "require_user_action": {
                "input": {"title": self._toLanguageObject(title), "settings": settings}
            },
        }

        await self._sendEvent(
            websocket, uc.MSG_EVENTS.DRIVER_SETUP_CHANGE, data, uc.EVENT_CATEGORY.DEVICE
        )

    async def driverSetupComplete(self, websocket):
        data = {"event_type": "STOP", "state": "OK"}

        await self._sendEvent(
            websocket, uc.MSG_EVENTS.DRIVER_SETUP_CHANGE, data, uc.EVENT_CATEGORY.DEVICE
        )

    async def driverSetupError(self, websocket, error="OTHER"):
        data = {"event_type": "STOP", "state": "ERROR", "error": error}

        await self._sendEvent(
            websocket, uc.MSG_EVENTS.DRIVER_SETUP_CHANGE, data, uc.EVENT_CATEGORY.DEVICE
        )
