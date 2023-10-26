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


class STATES(str, Enum):
    """Switch entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    ON = "ON"
    OFF = "OFF"


class FEATURES(str, Enum):
    """Switch entity features."""

    ON_OFF = "on_off"
    TOGGLE = "toggle"


class ATTRIBUTES(str, Enum):
    """Switch entity attributes."""

    STATE = "state"


class COMMANDS(str, Enum):
    """Switch entity commands."""

    ON = "on"
    OFF = "off"
    TOGGLE = "toggle"


class DEVICECLASSES(str, Enum):
    """Switch entity device classes."""

    OUTLET = "outlet"
    SWITCH = "switch"


class OPTIONS(str, Enum):
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
        identifier: str,
        name: str | dict,
        features: list[FEATURES],
        attributes: dict,
        deviceClass: DEVICECLASSES | None = None,
        options: dict | None = None,
        area: str | None = None,
    ):
        """
        Create switch-entity instance.

        :param identifier: entity identifier
        :param name: friendly name
        :param features: switch features
        :param attributes: switch attributes
        :param deviceClass: optional switch device class
        :param options: options
        :param area: optional area
        """
        super().__init__(
            identifier,
            name,
            TYPES.SWITCH,
            features,
            attributes,
            deviceClass,
            options,
            area,
        )

        LOG.debug("Switch entity created with id: %s", self.id)
