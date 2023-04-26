import asyncio
import websockets
import json
import logging
import os
import socket

from zeroconf import IPVersion
from zeroconf.asyncio import AsyncServiceInfo, AsyncZeroconf

from pyee.base import EventEmitter

import uc_integration_api.api_definitions as uc

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class IntegrationAPI:
    def __init__(self, type="default"):
        self.loop = None
        self.events = EventEmitter()
        self.driverInfo = {}
        self.driverPath = None
        self.state = uc.DEVICE_STATES.DISCONNECTED
        self.server = None
        self.serverTask = None
        self.clients = set()

    async def init(self, loop, driverPath):
        self.loop = loop
        self.driverPath = driverPath

        # Setup event loop
        asyncio.set_event_loop(self.loop)

        # Load driver config
        file = open(self.driverPath)
        self.driverInfo = json.load(file)
        file.close()

        # Set driver URL
        self.driverInfo["driver_url"] = self.getDriverUrl(
            self.driverInfo["driver_url"] if "driver_url" in self.driverInfo else None,
            self.driverInfo["port"],
        )

        # Set driver name
        name = self.getDefaultLanguageString(self.driverInfo["name"], "Unknown driver")

        # Setup zeroconf service info
        info = AsyncServiceInfo(
            "_uc-integration._tcp.local.",
            f"{name}._uc-integration._tcp.local.",
            addresses=[socket.inet_aton("127.0.0.1")],
            port=int(self.driverInfo["port"]),
            properties={
                "name": name,
                "ver": self.driverInfo["version"],
                "developer": self.driverInfo["developer"]["name"],
            },
        )
        zeroconf = AsyncZeroconf(ip_version=IPVersion.All)
        await zeroconf.async_register_service(info)

        LOG.info(
            "Driver is up: %s, version: %s, listening on: %s : %s",
            self.driverInfo["driver_id"],
            self.driverInfo["version"],
            self.driverInfo["driver_url"],
            self.driverInfo["port"],
        )

        self.loop.create_task(self.startWebSocketServer())

        # Start websocket server
        # self.serverTask = loop.create_task(self.startWebSocketServer())

    async def startWebSocketServer(self):
        async with websockets.serve(self.messageReceived, "localhost", int(self.driverInfo["port"])):
                await asyncio.Future()

    def getDriverUrl(self, driverUrl, port):
        if driverUrl is not None:
            if driverUrl.startswith("ws://") or driverUrl.startswith("wss://"):
                return driverUrl

            return "ws://" + os.uname().nodename + ":" + port

        return None

    def getDefaultLanguageString(self, text, defaultText="Undefined"):
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

    async def messageReceived(self, websocket):
        try:
            self.clients.add(websocket)
            LOG.info('WS: Client added')
            # await websocket.wait_closed()
            async for message in websocket:
                # process message
                await self.processWsMessage(websocket, message) 
                await self.sendWsMessage(websocket, "Resp:" + message)
        
        except websockets.ConnectionClosedOK:
            LOG.info("WS: Connection Closed")
        
        except websockets.exceptions.ConnectionClosedError:
            LOG.info("WS: Connection Closed")

        finally:
            self.clients.remove(websocket)
            LOG.info('WS: Client removed')

    async def sendWsMessage(self, websocket, message):
        await websocket.send(message)

    async def processWsMessage(self, websocket, message):
        LOG.info(message)