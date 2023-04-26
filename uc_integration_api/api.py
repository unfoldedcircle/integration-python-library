import asyncio
import websockets
import json
import logging
import os
import socket

from zeroconf import IPVersion
from zeroconf.asyncio import AsyncServiceInfo, AsyncZeroconf

from pyee import AsyncIOEventEmitter

import uc_integration_api.api_definitions as uc

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

class IntegrationAPI:
    def __init__(self, type="default"):
        self._loop = None
        self.events = None
        self.driverInfo = {}
        self._driverPath = None
        self.state = uc.DEVICE_STATES.DISCONNECTED
        self._serverTask = None
        self._clients = set()

        self.availableEntities = None
        self.configuredEntities = None

    async def init(self, loop, driverPath):
        self._loop = loop
        self._driverPath = driverPath

        # Setup event loop
        asyncio.set_event_loop(self._loop)

        self.events = AsyncIOEventEmitter(self._loop)

        # Load driver config
        file = open(self._driverPath)
        self.driverInfo = json.load(file)
        file.close()

        # Set driver URL
        self.driverInfo["driver_url"] = self.getDriverUrl(
            self.driverInfo["driver_url"] if "driver_url" in self.driverInfo else None,
            self.driverInfo["port"],
        )

        # Set driver name
        name = self._getDefaultLanguageString(self.driverInfo["name"], "Unknown driver")
        url = self.driverInfo["driver_id"]

        # Setup zeroconf service info
        info = AsyncServiceInfo(
            "_uc-integration._tcp.local.",
            f"{url}._uc-integration._tcp.local.",
            addresses=[socket.gethostbyname(socket.gethostname())],
            port=int(self.driverInfo["port"]),
            properties={
                "name": name,
                "ver": self.driverInfo["version"],
                "developer": self.driverInfo["developer"]["name"],
            },
        )
        zeroconf = AsyncZeroconf(ip_version=IPVersion.V4Only)
        await zeroconf.async_register_service(info)

        self._serverTask = self._loop.create_task(self._startWebSocketServer())

        # TODO connect to update events for entity attributes

        LOG.info(
            "Driver is up: %s, version: %s, listening on: %s : %s",
            self.driverInfo["driver_id"],
            self.driverInfo["version"],
            self.driverInfo["driver_url"],
            self.driverInfo["port"],
        )

    def getDriverUrl(self, driverUrl, port):
        if driverUrl is not None:
            if driverUrl.startswith("ws://") or driverUrl.startswith("wss://"):
                return driverUrl

            return "ws://" + os.uname().nodename + ":" + port

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
        if text is not None:
            return {
                'en': text
            }
        else:
            return None        
    
    async def _startWebSocketServer(self):
        addr = socket.gethostbyname(socket.gethostname())
        async with websockets.serve(self._handleWs, addr, int(self.driverInfo["port"])):
                await asyncio.Future()

    async def _handleWs(self, websocket):
        try:
            self._clients.add(websocket)
            LOG.info('WS: Client added')

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
            LOG.info('WS: Client removed')

    async def _sendOkResult(self, websocket, id, msgData = {}):
        await self._sendResponse(websocket, id, 'result', msgData, 200)

    async def _sendErrorResult(self, websocket, id, statusCode = 500, msgData = {}):
        await self._sendResponse(websocket, id, 'result', msgData, statusCode)

    async def _sendResponse(self, websocket, id, msg, msgData, statusCode = uc.STATUS_CODES.OK):
        data = {
            'kind': 'resp',
            'req_id': id,
            'code': int(statusCode),
            'msg': msg,
            'msg_data': msgData
        }
        
        if websocket in self._clients:
            dataDump = json.dumps(data)
            LOG.debug('->: ' + dataDump)
            await websocket.send(dataDump)
        else:
            LOG.error('Error sending response: connection no longer established')

    async def _broadcastEvent(self, msg, msgData, category):
        data = {
            'kind': 'event',
            'msg': msg,
            'msg_data': msgData,
            'cat': category
        }

        for websocket in self._clients:
            dataDump = json.dumps(data)
            LOG.debug('->: ' + dataDump)
            await websocket.send(dataDump)

    async def _sendEvent(self, websocket, msg, msgData, category):
        data = {
            'kind': 'event',
            'msg': msg,
            'msg_data': msgData,
            'cat': category
        }

        if websocket in self._clients:
            dataDump = json.dumps(data)
            LOG.debug('->: ' + dataDump)
            await websocket.send(dataDump)
        else:
            LOG.error('Error sending event: connection no longer established')

    async def _processWsMessage(self, websocket, message):
        LOG.debug('<-: ' + message)

        data = json.loads(message)
        kind = data['kind']
        id = data['id'] if 'id' in data else None
        msg = data['msg']
        msgData = data['msg_data'] if 'msg_data' in data else None

        if kind == 'req':
            if msg == uc.MESSAGES.GET_DRIVER_VERSION:
                await self._sendResponse(websocket, id, uc.MSG_EVENTS.DRIVER_VERSION, self.getDriverVersion())
            elif msg == uc.MESSAGES.GET_DEVICE_STATE:
                await self._sendResponse(websocket, id, uc.MSG_EVENTS.DEVICE_STATE, self.state)
            elif msg == uc.MESSAGES.GET_AVAILABLE_ENTITIES:
                print('')
            elif msg == uc.MESSAGES.GET_ENTITY_STATES:
                print('')
            elif msg == uc.MESSAGES.ENTITY_COMMAND:
                print('')
            elif msg == uc.MESSAGES.SUBSCRIBE_EVENTS:
                print('')
                await self._sendOkResult(websocket, id)
            elif msg == uc.MESSAGES.UNSUBSCRIBE_EVENTS:
                print('')
                await self._sendOkResult(websocket, id)
            elif msg == uc.MESSAGES.GET_DRIVER_METADATA:
                await self._sendResponse(websocket, id, uc.MSG_EVENTS.DRIVER_METADATA, self.driverInfo)
            elif msg == uc.MESSAGES.SETUP_DRIVER:
                await self._setupDriver(websocket, id, msgData)
            elif msg == uc.MESSAGES.SET_DRIVER_USER_DATA:
                await self._setDriverUserData(websocket, id, msgData)

        elif kind == 'event':
            if msg == uc.MSG_EVENTS.CONNECT:
                self.events.emit(uc.EVENTS.CONNECT)
            elif msg == uc.MSG_EVENTS.DISCONNECT:
                self.events.emit(uc.EVENTS.DISCONNECT)
            elif msg == uc.MSG_EVENTS.ABORT_DRIVER_SETUP:
                self.events.emit(uc.EVENTS.SETUP_DRIVER_ABORT)

    async def _authenticate(self, websocket, success):
        await self._sendResponse(websocket, 0, uc.MESSAGES.AUTHENTICATION, {}, uc.STATUS_CODES.OK if success else uc.STATUS_CODES.UNAUTHORIZED)

    def getDriverVersion(self):
        return {
            'name': self.driverInfo['name']['en'],
            'version': {
                'api': self.driverInfo['min_core_api'],
                'driver': self.driverInfo['version']
            }
        }
    
    async def setDeviceState(self, state):
        self.state = state

        await self._broadcastEvent(uc.MSG_EVENTS.DEVICE_STATE, {'state': self.state}, uc.EVENT_CATEGORY.DEVICE)
    
    async def _setupDriver(self, websocket, id, data):
        self.events.emit(uc.EVENTS.SETUP_DRIVER, websocket, id, data['setup_data'])

    async def _setDriverUserData(self, websocket, id, data):
        if 'input_values' in data:
            self.events.emit(uc.EVENTS.SETUP_DRIVER_USER_DATA, websocket, id, data['input_values'])
        elif 'confirm' in data:
            self.events.emit(uc.EVENTS.SETUP_DRIVER_USER_CONFIRMATION, websocket, id, data = None)
        else:
            LOG.warning('Unsupported set_driver_user_data payload received')

    async def acknowledgeCommand(self, websocket, id, statusCode = uc.STATUS_CODES.OK):
        await self._sendResponse(websocket, id, 'result', {}, statusCode)

    async def driverSetupProgress(self, websocket):
        data = {
            'event_type': 'SETUP',
            'state': 'SETUP'
        }

        await self._sendEvent(websocket, uc.MSG_EVENTS.DRIVER_SETUP_CHANGE, data, uc.EVENT_CATEGORY.DEVICE)

    async def requestDriverSetupUserConfirmation(self, websocket, title, msg1 = None, image = None, msg2 = None):
        data = {
            'event_type': 'SETUP',
            'state': 'WAIT_USER_ACTION',
            'require_user_action': {
                'confirmation': {
                    'title': self._toLanguageObject(title),
                    'message1': self._toLanguageObject(msg1),
                    'image': image,
                    'message2': self._toLanguageObject(msg2)
                }
            }
        }

        await self._sendEvent(websocket, uc.MSG_EVENTS.DRIVER_SETUP_CHANGE, data, uc.EVENT_CATEGORY.DEVICE)

    async def requestDriverSetupUserInput(self, websocket, title, settings):
        data = {
            'event_type': 'SETUP',
            'state': 'WAIT_USER_ACTION',
            'require_user_action': {
                'input': {
                    'title': self._toLanguageObject(title),
                    'settings': settings
                }
            }
        }

        await self._sendEvent(websocket, uc.MSG_EVENTS.DRIVER_SETUP_CHANGE, data, uc.EVENT_CATEGORY.DEVICE)

    async def driverSetupComplete(self, websocket):
        data = {
            'event_type': 'STOP',
            'state': 'OK'
        }

        await self._sendEvent(websocket, uc.MSG_EVENTS.DRIVER_SETUP_CHANGE, data, uc.EVENT_CATEGORY.DEVICE)

    async def driverSetupError(self, websocket, error = 'OTHER'):
        data = {
            'event_type': 'STOP',
            'state': 'ERROR',
            'error': error
        }

        await self._sendEvent(websocket, uc.MSG_EVENTS.DRIVER_SETUP_CHANGE, data, uc.EVENT_CATEGORY.DEVICE)