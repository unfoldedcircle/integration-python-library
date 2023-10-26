"""
Sensor entity definitions.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL 2.0, see LICENSE for more details.
"""

import logging
from enum import Enum

from ucapi.entity import TYPES, Entity

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class STATES(str, Enum):
    """Sensor entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    ON = "ON"


class FEATURES(str, Enum):
    """Sensor entity features."""


class ATTRIBUTES(str, Enum):
    """Sensor entity attributes."""

    STATE = "state"
    VALUE = "value"
    UNIT = "unit"


class COMMANDS(str, Enum):
    """Sensor entity commands."""


class DEVICECLASSES(str, Enum):
    """Sensor entity device classes."""

    CUSTOM = "custom"
    BATTERY = "battery"
    CURRENT = "current"
    ENERGY = "energy"
    HUMIDITY = "humidity"
    POWER = "power"
    TEMPERATURE = "temperature"
    VOLTAGE = "voltage"


class OPTIONS(str, Enum):
    """Sensor entity options."""

    CUSTOM_UNIT = "custom_unit"
    NATIVE_UNIT = "native_unit"
    DECIMALS = "decimals"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"


class Sensor(Entity):
    """
    Sensor entity class.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_sensor.md
    for more information.
    """

    def __init__(
        self,
        identifier: str,
        name: str | dict,
        features: list[FEATURES],
        attributes: dict,
        deviceClass: DEVICECLASSES | None = None,
        options: dict | None = None,
        area: str | None = None,
    ):
        """
        Create sensor-entity instance.

        :param identifier: entity identifier
        :param name: friendly name
        :param features: sensor features
        :param attributes: sensor attributes
        :param deviceClass: optional sensor device class
        :param options: options
        :param area: optional area
        """
        super().__init__(
            identifier,
            name,
            TYPES.SENSOR,
            features,
            attributes,
            deviceClass,
            options,
            area,
        )

        LOG.debug("Sensor entity created with id: %s", self.id)
