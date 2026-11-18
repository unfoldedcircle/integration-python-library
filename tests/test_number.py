"""
Tests for number entity support.

:copyright: (c) 2026 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import json
import unittest
from unittest.mock import AsyncMock, Mock, patch

from ucapi import Entities, EntityTypes, Events, IntegrationAPI, Number, StatusCodes
from ucapi.number import (
    Attributes,
    Commands,
    DeviceClasses,
    DisplayMode,
    Features,
    Options,
    States,
)


class TestNumber(unittest.IsolatedAsyncioTestCase):
    """Test number entities through the public API and entity store."""

    def test_minimal_entity(self):
        """Allow implicit value support and omitted state and options."""
        entity = Number("bass", "Bass", [], {Attributes.VALUE: 2.5})

        self.assertEqual(entity.entity_type, EntityTypes.NUMBER)
        self.assertEqual(EntityTypes("number"), EntityTypes.NUMBER)
        self.assertEqual(entity.name, {"en": "Bass"})
        self.assertEqual(entity.features, [])
        self.assertEqual(entity.attributes, {"value": 2.5})
        self.assertIsNone(entity.options)
        self.assertIsNone(entity.device_class)

    async def test_entity_definition_serialization(self):
        """Serialize all metadata and options using the protocol field names."""
        entity = Number(
            "bass",
            {"en": "Bass", "de": "Bass"},
            [Features.VALUE, Features.TRANSITION],
            {Attributes.STATE: States.ON, Attributes.VALUE: 2.5},
            device_class=DeviceClasses.AUDIO_LEVEL,
            options={
                Options.MIN: -10,
                Options.MAX: 10,
                Options.STEP: 0.5,
                Options.DECIMALS: 1,
                Options.UNIT: "dB",
                Options.DISPLAY_MODE: DisplayMode.STEPPER,
                Options.READABLE: False,
            },
            icon="uc:music",
            description="Amplifier bass level",
            area="Living room",
        )
        entity.device_id = "amp-1"
        entities = Entities("available", asyncio.get_running_loop())
        self.assertTrue(entities.add(entity))

        self.assertEqual(
            json.loads(json.dumps(entities.get_all())),
            [
                {
                    "entity_id": "bass",
                    "entity_type": "number",
                    "device_id": "amp-1",
                    "features": ["value", "transition"],
                    "name": {"en": "Bass", "de": "Bass"},
                    "device_class": "audio_level",
                    "options": {
                        "min": -10,
                        "max": 10,
                        "step": 0.5,
                        "decimals": 1,
                        "unit": "dB",
                        "display_mode": "stepper",
                        "readable": False,
                    },
                    "icon": "uc:music",
                    "description": {"en": "Amplifier bass level"},
                    "area": "Living room",
                }
            ],
        )

    async def test_unbounded_range_and_unavailable_value(self):
        """Preserve explicit null bounds and emit null values on state changes."""
        entity = Number(
            "counter",
            "Counter",
            [],
            {Attributes.VALUE: 42},
            options={Options.MIN: None, Options.MAX: None},
        )
        entities = Entities("configured", asyncio.get_running_loop())
        entities.add(entity)
        updates = []
        entities.add_listener(
            Events.ENTITY_ATTRIBUTES_UPDATED,
            lambda *args: updates.append(args),
        )
        attributes = {Attributes.STATE: States.UNAVAILABLE, Attributes.VALUE: None}

        self.assertTrue(entities.update_attributes(entity.id, attributes))
        self.assertEqual(updates, [("counter", EntityTypes.NUMBER, attributes)])
        self.assertEqual(
            json.loads(json.dumps(entities.get_all()))[0]["options"],
            {"min": None, "max": None},
        )
        self.assertEqual(
            json.loads(json.dumps(await entities.get_states()))[0]["attributes"],
            {"state": "UNAVAILABLE", "value": None},
        )

    async def test_commands_forward_parameters_and_websocket(self):
        """Route number requests to the driver and acknowledge each command."""
        handler = AsyncMock(return_value=StatusCodes.OK)
        websocket = Mock()
        entity = Number("bass", "Bass", [Features.TRANSITION], {}, cmd_handler=handler)
        api = IntegrationAPI(asyncio.get_running_loop())
        api.available_entities.add(entity)

        with patch.object(api, "_enqueue_ws_payload", new_callable=AsyncMock) as send:
            await api._process_ws_message(
                websocket,
                {
                    "kind": "req",
                    "id": 1,
                    "msg": "subscribe_events",
                    "msg_data": {"entity_ids": ["bass"]},
                },
            )
            self.assertIs(api.configured_entities.get("bass"), entity)

            for command, params in (
                (Commands.SET_VALUE, {"value": 2.5, "duration": 2000}),
                (Commands.INCREMENT, None),
                (Commands.DECREMENT, {"step": 0.5}),
            ):
                with self.subTest(command=command):
                    msg_data = {
                        "entity_type": "number",
                        "entity_id": "bass",
                        "cmd_id": command.value,
                    }
                    if params is not None:
                        msg_data["params"] = params
                    await api._process_ws_message(
                        websocket,
                        {
                            "kind": "req",
                            "id": 2,
                            "msg": "entity_command",
                            "msg_data": msg_data,
                        },
                    )
                    handler.assert_awaited_with(
                        entity, command.value, params, websocket=websocket
                    )
                    send.assert_awaited_with(
                        websocket,
                        {
                            "kind": "resp",
                            "req_id": 2,
                            "code": 200,
                            "msg": "result",
                            "msg_data": {},
                        },
                    )

    async def test_discovery_respects_supported_entity_types(self):
        """Advertise number entities only when supported or capabilities are unknown."""
        websocket = Mock()
        entity = Number("bass", "Bass", [], {})

        for supported, expected_ids in (
            (["number"], ["bass"]),
            (["switch"], []),
            ([], ["bass"]),
        ):
            with self.subTest(supported=supported):
                api = IntegrationAPI(asyncio.get_running_loop())
                api.available_entities.add(entity)
                with (
                    patch.object(
                        api,
                        "get_supported_entity_types",
                        new_callable=AsyncMock,
                        return_value=supported,
                    ),
                    patch.object(
                        api, "_enqueue_ws_payload", new_callable=AsyncMock
                    ) as send,
                ):
                    await api._process_ws_message(
                        websocket,
                        {"kind": "req", "id": 1, "msg": "get_available_entities"},
                    )

                response = json.loads(json.dumps(send.await_args.args[1]))
                self.assertEqual(response["msg"], "available_entities")
                self.assertEqual(response["code"], 200)
                self.assertEqual(
                    [
                        item["entity_id"]
                        for item in response["msg_data"]["available_entities"]
                    ],
                    expected_ids,
                )

    async def test_command_without_handler(self):
        """Leave device command implementation to the integration driver."""
        entity = Number("bass", "Bass", [], {Attributes.VALUE: 0})

        result = await entity.command(
            Commands.SET_VALUE, {"value": 2.5}, websocket=None
        )

        self.assertEqual(result, StatusCodes.NOT_IMPLEMENTED)


if __name__ == "__main__":
    unittest.main()
