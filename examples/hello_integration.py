#!/usr/bin/env python3
"""Hello world integration example. Bare minimum of an integration driver."""

import asyncio
import logging
from typing import Any

import ucapi

loop = asyncio.new_event_loop()
api = ucapi.IntegrationAPI(loop)


async def cmd_handler(
    entity: ucapi.Button, cmd_id: str, _params: dict[str, Any] | None, websocket: Any
) -> ucapi.StatusCodes:
    """
    Push button command handler.

    Called by the integration-API if a command is sent to a configured button-entity.

    :param entity: button entity
    :param cmd_id: command
    :param _params: optional command parameters
    :param websocket: optional client connection for sending directed events
    :return: status of the command
    """
    print(f"Got {entity.id} command request: {cmd_id}")

    return ucapi.StatusCodes.OK


@api.listens_to(ucapi.Events.CONNECT)
async def on_connect() -> None:
    # When the remote connects, we just set the device state. We are ready all the time!
    await api.set_device_state(ucapi.DeviceStates.CONNECTED)


if __name__ == "__main__":
    logging.basicConfig()

    button = ucapi.Button(
        "button1",
        "Push the button",
        cmd_handler=cmd_handler,
    )
    api.available_entities.add(button)

    loop.run_until_complete(api.init("hello_integration.json"))
    loop.run_forever()
