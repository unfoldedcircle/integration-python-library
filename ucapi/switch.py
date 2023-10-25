"""
Switch entity definitions.

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
    """Switch entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    ON = "ON"
    OFF = "OFF"


class FEATURES(Enum):
    """Switch entity features."""

    ON_OFF = "on_off"
    TOGGLE = "toggle"


class ATTRIBUTES(Enum):
    """Switch entity attributes."""

    STATE = "state"


class COMMANDS(Enum):
    """Switch entity commands."""

    ON = "on"
    OFF = "off"
    TOGGLE = "toggle"


class DEVICECLASSES(Enum):
    """Switch entity device classes."""

    OUTLET = "outlet"
    SWITCH = "switch"


class OPTIONS(Enum):
    """Switch entity options."""

    READABLE = "readable"


class Switch(Entity):
    """
    Switch entity class.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_switch.md
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
            TYPES.SWITCH,
            features,
            attributes,
            deviceClass,
            options,
            area,
        )

        LOG.debug("Switch entity created with id: %s", self.id)
