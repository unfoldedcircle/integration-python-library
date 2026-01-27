#!/usr/bin/env python3
"""Remote entity integration example. Bare minimum of an integration driver."""

import asyncio
import json
import logging
import sys
from typing import Any

import ucapi
from ucapi import remote
from ucapi.remote import *
from ucapi.remote import create_send_cmd, create_sequence_cmd
from ucapi.ui import (
    Buttons,
    DeviceButtonMapping,
    Size,
    UiPage,
    create_btn_mapping,
    create_ui_icon,
    create_ui_text,
)

loop = asyncio.new_event_loop()
api = ucapi.IntegrationAPI(loop)

# Simple commands which are supported by this example remote-entity
supported_commands = [
    "VOLUME_UP",
    "VOLUME_DOWN",
    "HOME",
    "GUIDE",
    "CONTEXT_MENU",
    "CURSOR_UP",
    "CURSOR_DOWN",
    "CURSOR_LEFT",
    "CURSOR_RIGHT",
    "CURSOR_ENTER",
    "MY_RECORDINGS",
    "MY_APPS",
    "REVERSE",
    "PLAY",
    "PAUSE",
    "FORWARD",
    "RECORD",
]


async def cmd_handler(
    entity: ucapi.Remote, cmd_id: str, params: dict[str, Any] | None, websocket: Any
) -> ucapi.StatusCodes:
    """
    Remote command handler.

    Called by the integration-API if a command is sent to a configured remote-entity.

    :param entity: remote entity
    :param cmd_id: command
    :param params: optional command parameters
    :param websocket: optional client connection for sending directed events
    :return: status of the command
    """
    print(f"Got {entity.id} command request: {cmd_id}")

    state = None
    match cmd_id:
        case remote.Commands.ON:
            state = remote.States.ON
        case remote.Commands.OFF:
            state = remote.States.OFF
        case remote.Commands.TOGGLE:
            if entity.attributes[remote.Attributes.STATE] == remote.States.OFF:
                state = remote.States.ON
            else:
                state = remote.States.OFF
        case remote.Commands.SEND_CMD:
            command = params.get("command")
            # It's up to the integration what to do with an unknown command.
            # If the supported commands are provided as simple_commands, then it's
            # easy to validate.
            if command not in supported_commands:
                print(f"Unknown command: {command}", file=sys.stderr)
                return ucapi.StatusCodes.BAD_REQUEST

            repeat = params.get("repeat", 1)
            delay = params.get("delay", 0)
            hold = params.get("hold", 0)
            print(f"Command: {command} (repeat={repeat}, delay={delay}, hold={hold})")
        case remote.Commands.SEND_CMD_SEQUENCE:
            sequence = params.get("sequence")
            repeat = params.get("repeat", 1)
            delay = params.get("delay", 0)
            hold = params.get("hold", 0)
            print(
                f"Command sequence: {sequence} (repeat={repeat}, delay={delay}, hold={hold})"
            )
        case _:
            print(f"Unsupported command: {cmd_id}", file=sys.stderr)
            return ucapi.StatusCodes.BAD_REQUEST

    if state:
        api.configured_entities.update_attributes(
            entity.id, {remote.Attributes.STATE: state}
        )

    return ucapi.StatusCodes.OK


@api.listens_to(ucapi.Events.CONNECT)
async def on_connect() -> None:
    """When the UCR2 connects, send the device state."""
    # This example is ready all the time!
    await api.set_device_state(ucapi.DeviceStates.CONNECTED)


def create_button_mappings() -> list[DeviceButtonMapping | dict[str, Any]]:
    """Create a demo button mapping showing different composition options."""
    return [
        # simple short- and long-press mapping
        create_btn_mapping(Buttons.HOME, "HOME", "GUIDE"),
        # use channel buttons for volume control
        create_btn_mapping(Buttons.CHANNEL_DOWN, "VOLUME_DOWN"),
        create_btn_mapping(Buttons.CHANNEL_UP, "VOLUME_UP"),
        create_btn_mapping(Buttons.DPAD_UP, "CURSOR_UP"),
        create_btn_mapping(Buttons.DPAD_DOWN, "CURSOR_DOWN"),
        create_btn_mapping(Buttons.DPAD_LEFT, "CURSOR_LEFT"),
        create_btn_mapping(Buttons.DPAD_RIGHT, "CURSOR_RIGHT"),
        # use a send command
        create_btn_mapping(
            Buttons.DPAD_MIDDLE, create_send_cmd("CONTEXT_MENU", hold=1000)
        ),
        # use a sequence command
        create_btn_mapping(
            Buttons.BLUE,
            create_sequence_cmd(
                [
                    "CURSOR_UP",
                    "CURSOR_RIGHT",
                    "CURSOR_DOWN",
                    "CURSOR_LEFT",
                ],
                delay=200,
            ),
        ),
        # Safety off: don't use a DeviceButtonMapping data class but a dictionary.
        # This is useful for directly reading a json configuration file.
        {"button": "POWER", "short_press": {"cmd_id": "remote.toggle"}},
    ]


def create_ui() -> list[UiPage | dict[str, Any]]:
    """Create a demo user interface showing different composition options."""
    # Safety off again: directly use json structure to read a configuration file
    with open("remote_ui_page.json", "r", encoding="utf-8") as file:
        main_page = json.load(file)

    # On-the-fly UI composition
    ui_page1 = UiPage("page1", "Main")
    ui_page1.add(create_ui_text("Hello remote entity", 0, 0, size=Size(4, 1)))
    ui_page1.add(create_ui_icon("uc:home", 0, 2, cmd="HOME"))
    ui_page1.add(create_ui_icon("uc:up-arrow-bold", 2, 2, cmd="CURSOR_UP"))
    ui_page1.add(create_ui_icon("uc:down-arrow-bold", 2, 4, cmd="CURSOR_DOWN"))
    ui_page1.add(create_ui_icon("uc:left-arrow", 1, 3, cmd="CURSOR_LEFT"))
    ui_page1.add(create_ui_icon("uc:right-arrow", 3, 3, cmd="CURSOR_RIGHT"))
    ui_page1.add(create_ui_text("Ok", 2, 3, cmd="CURSOR_ENTER"))

    ui_page2 = UiPage("page2", "Page 2")
    ui_page2.add(
        create_ui_text(
            "Pump up the volume!",
            0,
            0,
            size=Size(4, 2),
            cmd=create_send_cmd("VOLUME_UP", repeat=5),
        )
    )
    ui_page2.add(
        create_ui_text(
            "Test sequence",
            0,
            4,
            size=Size(4, 1),
            cmd=create_sequence_cmd(
                [
                    "CURSOR_UP",
                    "CURSOR_RIGHT",
                    "CURSOR_DOWN",
                    "CURSOR_LEFT",
                ],
                delay=200,
            ),
        )
    )
    ui_page2.add(create_ui_text("On", 0, 5, cmd="on"))
    ui_page2.add(create_ui_text("Off", 1, 5, cmd="off"))

    return [main_page, ui_page1, ui_page2]


if __name__ == "__main__":
    logging.basicConfig()

    entity = ucapi.Remote(
        "remote1",
        "Demo remote",
        [remote.Features.ON_OFF, remote.Features.TOGGLE],
        {remote.Attributes.STATE: remote.States.OFF},
        simple_commands=supported_commands,
        button_mapping=create_button_mappings(),
        ui_pages=create_ui(),
        cmd_handler=cmd_handler,
    )
    api.available_entities.add(entity)

    loop.run_until_complete(api.init("remote.json"))
    loop.run_forever()
