# API wrapper examples

This directory contains a few examples on how to use the Remote Two/3 Integration-API wrapper.

Each example uses a driver metadata definition file. It's a json file named after the example.
The most important fields are:

- `driver_id`: unique identifier of the driver. Make sure you create a new ID for every driver.
- `port` defines the listening port of the WebSocket server for the Remote Two to connect to.
  - This port is published in the mDNS service information.
- `name`: Friendly name of the driver to show.  

See the [WebSocket Integration API documentation](https://github.com/unfoldedcircle/core-api/tree/main/doc/integration-driver)

## hello_integration

The [hello_integration.py](hello_integration.py) example is a "hello world" example showing the bare minimum required
to start with an integration driver for the Remote Two.

It defines a single push button with a callback handler. When pushed, it just prints a message in the console.

## remote

The [remote.py](remote.py) example shows how to use the [remote-entity](https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_remote.md).

It defines some simple commands, a custom button mapping and user interface pages for the available commands. 

## setup_flow

The [setup_flow](setup_flow.py) example shows how to define a dynamic setup flow for the driver setup.

If the user selects the _expert_ option in the main setup screen:
1. An input screen is shown asking to select an item from a dropdown list.
2. The chosen option will be shown in the next input screen with another setting, on how many button entities to create.
3. The number of push buttons are created.

The available input settings are defined in the [Integration-API asyncapi.yaml definition](https://github.com/unfoldedcircle/core-api/tree/main/integration-api)
and are not yet available as typed Python objects.

See `Setting` object definition and the referenced SettingTypeNumber, SettingTypeText, SettingTypeTextArea,
SettingTypePassword, SettingTypeCheckbox, SettingTypeDropdown, SettingTypeLabel. 

## voice

The [voice ](voice.py) example shows how to use the voice-assistant entity and receiving a microphone audio stream.

Firmware version 2.8.2 or higher is required.
