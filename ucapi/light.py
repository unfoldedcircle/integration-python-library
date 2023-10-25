"""
Light entity definitions.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL 2.0, see LICENSE for more details.
"""

import logging
from enum import Enum

from ucapi.entity import TYPES, Entity

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class STATES(Enum):
    """Light entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    ON = "ON"
    OFF = "OFF"


class FEATURES(Enum):
    """Light entity features."""

    ON_OFF = "on_off"
    TOGGLE = "toggle"
    DIM = "dim"
    COLOR = "color"
    COLOR_TEMPERATURE = "color_temperature"


class ATTRIBUTES(Enum):
    """Light entity attributes."""

    STATE = "state"
    HUE = "hue"
    SATURATION = "saturation"
    BRIGHTNESS = "brightness"
    COLOR_TEMPERATURE = "color_temperature"


class COMMANDS(Enum):
    """Light entity commands."""

    ON = "on"
    OFF = "off"
    TOGGLE = "toggle"


class DEVICECLASSES(Enum):
    """Light entity device classes."""


class OPTIONS(Enum):
    """Light entity options."""

    COLOR_TEMPERATURE_STEPS = "color_temperature_steps"


class Light(Entity):
    """
    Switch entity class.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_light.md
    for more information.
    """

    def __init__(
        self,
        id,
        name,
        features,
        attributes,
        deviceClass=None,
        options=None,
        area=None,
        type="default",
    ):
        super().__init__(
            id,
            name,
            TYPES.LIGHT,
            features,
            attributes,
            deviceClass,
            options,
            area,
        )

        LOG.debug("Light entity created with id: %s", self.id)
