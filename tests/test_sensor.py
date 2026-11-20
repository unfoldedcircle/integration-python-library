"""
Tests for sensor entity support.

:copyright: (c) 2026 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import json
import unittest

from ucapi import Entities, EntityTypes, Events, Sensor
from ucapi.sensor import (
    Attributes,
    Commands,
    DeviceClasses,
    Features,
    Options,
    States,
)


class TestSensor(unittest.IsolatedAsyncioTestCase):
    """Test sensor entities through the public API and entity store."""

    def test_minimal_entity(self):
        """Allow minimal sensor entity with omitted state, device_class and options."""
        entity = Sensor("temp-1", "Temperature", [], {Attributes.VALUE: 21.5})

        self.assertEqual(entity.entity_type, EntityTypes.SENSOR)
        self.assertEqual(EntityTypes("sensor"), EntityTypes.SENSOR)
        self.assertEqual(entity.name, {"en": "Temperature"})
        self.assertEqual(entity.features, [])
        self.assertEqual(entity.attributes, {"value": 21.5})
        self.assertIsNone(entity.options)
        self.assertIsNone(entity.device_class)

    def test_features_and_commands_empty(self):
        """Verify sensor features and commands enums are defined."""
        self.assertEqual(list(Features), [])
        self.assertEqual(list(Commands), [])

    def test_device_classes_values(self):
        """Verify all sensor device class enum values match the specification."""
        expected = {
            DeviceClasses.CUSTOM: "custom",
            DeviceClasses.BATTERY: "battery",
            DeviceClasses.CURRENT: "current",
            DeviceClasses.DATE: "date",
            DeviceClasses.DURATION: "duration",
            DeviceClasses.ENERGY: "energy",
            DeviceClasses.HUMIDITY: "humidity",
            DeviceClasses.POWER: "power",
            DeviceClasses.TEMPERATURE: "temperature",
            DeviceClasses.TIMESTAMP: "timestamp",
            DeviceClasses.VOLTAGE: "voltage",
            DeviceClasses.BINARY: "binary",
        }
        for device_class, expected_value in expected.items():
            self.assertEqual(device_class.value, expected_value)
            self.assertEqual(DeviceClasses(expected_value), device_class)

    def test_options_values(self):
        """Verify all sensor options enum values match the specification."""
        expected = {
            Options.CUSTOM_LABEL: "custom_label",
            Options.CUSTOM_UNIT: "custom_unit",
            Options.NATIVE_UNIT: "native_unit",
            Options.DECIMALS: "decimals",
            Options.MIN_VALUE: "min_value",
            Options.MAX_VALUE: "max_value",
        }
        for option, expected_value in expected.items():
            self.assertEqual(option.value, expected_value)
            self.assertEqual(Options(expected_value), option)

    def test_states_values(self):
        """Verify sensor states enum values."""
        self.assertEqual(States.UNAVAILABLE.value, "UNAVAILABLE")
        self.assertEqual(States.UNKNOWN.value, "UNKNOWN")
        self.assertEqual(States.ON.value, "ON")

    def test_attributes_values(self):
        """Verify sensor attributes enum values."""
        self.assertEqual(Attributes.STATE.value, "state")
        self.assertEqual(Attributes.VALUE.value, "value")
        self.assertEqual(Attributes.UNIT.value, "unit")

    async def test_entity_definition_serialization(self):
        """Serialize all metadata and options using protocol field names."""
        entity = Sensor(
            "backup-timestamp",
            {"en": "Next Backup", "de": "Nächstes Backup"},
            [],
            {
                Attributes.STATE: States.ON,
                Attributes.VALUE: "2026-11-15T04:23:31+00:00",
            },
            device_class=DeviceClasses.TIMESTAMP,
            options={
                Options.CUSTOM_LABEL: "Scheduled",
                Options.CUSTOM_UNIT: "UTC",
                Options.NATIVE_UNIT: "ISO",
                Options.DECIMALS: 0,
            },
            icon="uc:calendar",
            description="Next scheduled system backup",
            area="Server room",
        )
        entity.device_id = "server-1"
        entities = Entities("available", asyncio.get_running_loop())
        self.assertTrue(entities.add(entity))

        self.assertEqual(
            json.loads(json.dumps(entities.get_all())),
            [
                {
                    "entity_id": "backup-timestamp",
                    "entity_type": "sensor",
                    "device_id": "server-1",
                    "features": [],
                    "name": {"en": "Next Backup", "de": "Nächstes Backup"},
                    "device_class": "timestamp",
                    "options": {
                        "custom_label": "Scheduled",
                        "custom_unit": "UTC",
                        "native_unit": "ISO",
                        "decimals": 0,
                    },
                    "icon": "uc:calendar",
                    "description": {"en": "Next scheduled system backup"},
                    "area": "Server room",
                }
            ],
        )

    async def test_date_and_duration_entities_serialization(self):
        """Serialize date and duration sensor entities."""
        date_sensor = Sensor(
            "release-date",
            "Release Date",
            [],
            {Attributes.VALUE: "2026-11-15"},
            device_class=DeviceClasses.DATE,
        )
        duration_sensor = Sensor(
            "uptime",
            "Uptime",
            [],
            {Attributes.VALUE: 3600, Attributes.UNIT: "s"},
            device_class=DeviceClasses.DURATION,
            options={Options.DECIMALS: 1},
        )
        entities = Entities("available", asyncio.get_running_loop())
        self.assertTrue(entities.add(date_sensor))
        self.assertTrue(entities.add(duration_sensor))

        serialized = json.loads(json.dumps(entities.get_all()))
        self.assertEqual(
            serialized,
            [
                {
                    "entity_id": "release-date",
                    "entity_type": "sensor",
                    "device_id": None,
                    "features": [],
                    "name": {"en": "Release Date"},
                    "device_class": "date",
                },
                {
                    "entity_id": "uptime",
                    "entity_type": "sensor",
                    "device_id": None,
                    "features": [],
                    "name": {"en": "Uptime"},
                    "device_class": "duration",
                    "options": {"decimals": 1},
                },
            ],
        )

    async def test_attribute_updates_and_unavailable_value(self):
        """Emit null values and updated attributes on state changes."""
        entity = Sensor(
            "temp-1",
            "Living Room Temp",
            [],
            {Attributes.VALUE: 21.5, Attributes.UNIT: "°C"},
            device_class=DeviceClasses.TEMPERATURE,
            options={Options.NATIVE_UNIT: "°C"},
        )
        entities = Entities("configured", asyncio.get_running_loop())
        entities.add(entity)
        updates = []
        entities.add_listener(
            Events.ENTITY_ATTRIBUTES_UPDATED,
            lambda *args: updates.append(args),
        )
        attributes = {
            Attributes.STATE: States.UNAVAILABLE,
            Attributes.VALUE: None,
            Attributes.UNIT: "°C",
        }

        self.assertTrue(entities.update_attributes(entity.id, attributes))
        self.assertEqual(updates, [("temp-1", EntityTypes.SENSOR, attributes)])
        self.assertEqual(
            json.loads(json.dumps(await entities.get_states()))[0]["attributes"],
            {"state": "UNAVAILABLE", "value": None, "unit": "°C"},
        )


if __name__ == "__main__":
    unittest.main()
