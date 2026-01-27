#!/usr/bin/env python3
"""Integration setup flow example."""

import asyncio
import logging
from typing import Any

import ucapi

loop = asyncio.new_event_loop()
api = ucapi.IntegrationAPI(loop)


async def driver_setup_handler(msg: ucapi.SetupDriver) -> ucapi.SetupAction:
    """
    Dispatch driver setup requests to corresponding handlers.

    Either start the setup process or handle the provided user input data.

    :param msg: the setup driver request object, either DriverSetupRequest,
                UserDataResponse or UserConfirmationResponse
    :return: the setup action on how to continue
    """
    if isinstance(msg, ucapi.DriverSetupRequest):
        return await handle_driver_setup(msg)
    if isinstance(msg, ucapi.UserDataResponse):
        return await handle_user_data_response(msg)

    # user confirmation not used in our demo setup process
    # if isinstance(msg, UserConfirmationResponse):
    #     return handle_user_confirmation(msg)

    return ucapi.SetupError()


async def handle_driver_setup(
    msg: ucapi.DriverSetupRequest,
) -> ucapi.SetupAction:
    """
    Start driver setup.

    Initiated by Remote Two/3 to set up the driver.

    :param msg: value(s) of input fields in the first setup screen.
    :return: the setup action on how to continue
    """
    # No support for reconfiguration :-)
    if msg.reconfigure:
        print("Ignoring driver reconfiguration request")

    # For our demo we simply clear everything!
    # A real driver might have to handle this differently
    api.available_entities.clear()
    api.configured_entities.clear()

    # check if user selected the expert option in the initial setup screen
    # please note that all values are returned as strings!
    if "expert" not in msg.setup_data or msg.setup_data["expert"] != "true":
        # add a single button as default action
        button = ucapi.Button(
            "button",
            "Button",
            cmd_handler=cmd_handler,
        )
        api.available_entities.add(button)
        return ucapi.SetupComplete()

    # Dropdown selections are usually set dynamically, e.g. with found devices etc.
    dropdown_items = [
        {"id": "red", "label": {"en": "Red", "de": "Rot"}},
        {"id": "green", "label": {"en": "Green", "de": "Grün"}},
        {"id": "blue", "label": {"en": "Blue", "de": "Blau"}},
    ]

    return ucapi.RequestUserInput(
        {"en": "Please choose", "de": "Bitte auswählen"},
        [
            {
                "id": "info",
                "label": {"en": "Setup flow example", "de": "Setup Flow Beispiel"},
                "field": {
                    "label": {
                        "value": {
                            "en": "This is just some informational text.\n"
                            + "Simple **Markdown** is supported!\n"
                            + "For example _some italic text_.\n"
                            + "## Or a header text\n~~strikethrough txt~~",
                        }
                    }
                },
            },
            {
                "field": {"dropdown": {"value": "", "items": dropdown_items}},
                "id": "step1.choice",
                "label": {
                    "en": "Choose color",
                    "de": "Wähle Farbe",
                },
            },
        ],
    )


async def handle_user_data_response(msg: ucapi.UserDataResponse) -> ucapi.SetupAction:
    """
    Process user data response in a setup process.

    Driver setup callback to provide requested user data during the setup process.

    :param msg: response data from the requested user data
    :return: the setup action on how to continue: SetupComplete if finished.
    """
    # values from all screens are returned: check in reverse order
    if "step2.count" in msg.input_values:
        for x in range(int(msg.input_values["step2.count"])):
            button = ucapi.Button(
                f"button{x}",
                f"Button {x + 1}",
                cmd_handler=cmd_handler,
            )
            api.available_entities.add(button)

        return ucapi.SetupComplete()

    if "step1.choice" in msg.input_values:
        choice = msg.input_values["step1.choice"]
        print(f"Chosen color: {choice}")
        return ucapi.RequestUserInput(
            {"en": "Step 2"},
            [
                {
                    "id": "info",
                    "label": {
                        "en": "Selected value from previous step:",
                        "de": "Selektierter Wert vom vorherigen Schritt:",
                    },
                    "field": {
                        "label": {
                            "value": {
                                "en": choice,
                            }
                        }
                    },
                },
                {
                    "field": {"number": {"value": 1, "min": 1, "max": 100, "steps": 2}},
                    "id": "step2.count",
                    "label": {
                        "en": "Button instance count",
                        "de": "Anzahl Button Instanzen",
                    },
                },
            ],
        )

    print("No choice was received")
    return ucapi.SetupError()


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

    loop.run_until_complete(api.init("setup_flow.json", driver_setup_handler))
    loop.run_forever()
