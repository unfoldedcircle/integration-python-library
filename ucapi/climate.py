"""
Climate entity definitions.

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
    """Climate entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    OFF = "OFF"
    HEAT = "HEAT"
    COOL = "COOL"
    HEAT_COOL = "HEAT_COOL"
    FAN = "FAN"
    AUTO = "AUTO"


class FEATURES(str, Enum):
    """Climate entity features."""

    ON_OFF = "on_off"
    HEAT = "heat"
    COOL = "cool"
    CURRENT_TEMPERATURE = "current_temperature"
    TARGET_TEMPERATURE = "target_temperature"
    TARGET_TEMPERATURE_RANGE = "target_temperature_range"
    FAN = "fan"


class ATTRIBUTES(str, Enum):
    """Climate entity attributes."""

    STATE = "state"
    CURRENT_TEMPERATURE = "current_temperature"
    TARGET_TEMPERATURE = "target_temperature"
    TARGET_TEMPERATURE_HIGH = "target_temperature_high"
    TARGET_TEMPERATURE_LOW = "target_temperature_low"
    FAN_MODE = "fan_mode"


class COMMANDS(str, Enum):
    """Climate entity commands."""

    ON = "on"
    OFF = "off"
    HVAC_MODE = "hvac_mode"
    TARGET_TEMPERATURE = "target_temperature"
    TARGET_TEMPERATURE_RANGE = "target_temperature_range"
    FAN_MODE = "fan_mode"


class DEVICECLASSES(str, Enum):
    """Climate entity device classes."""


class OPTIONS(str, Enum):
    """Climate entity options."""

    TEMPERATURE_UNIT = "temperature_unit"
    TARGET_TEMPERATURE_STEP = "target_temperature_step"
    MAX_TEMPERATURE = "max_temperature"
    MIN_TEMPERATURE = "min_temperature"
    FAN_MODES = "fan_modes"


class Climate(Entity):
    """
    Climate entity class.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_climate.md
    for more information.
    """

    def __init__(
        self,
        identifier: str,
        name: str | dict,
        features: list[FEATURES],
        attributes: dict,
        deviceClass: str | None = None,
        options: dict | None = None,
        area: str | None = None,
    ):
        """
        Create a climate-entity instance.

        :param identifier: entity identifier
        :param name: friendly name
        :param features: climate features
        :param attributes: climate attributes
        :param deviceClass: optional climate device class
        :param options: options
        :param area: optional area
        """
        super().__init__(
            identifier,
            name,
            TYPES.CLIMATE,
            features,
            attributes,
            deviceClass,
            options,
            area,
        )

        LOG.debug("Climate entity created with id: %s", self.id)
