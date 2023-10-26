"""
Switch entity definitions.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

import logging
from enum import Enum

from ucapi.entity import Entity, Types

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class States(str, Enum):
    """Switch entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    ON = "ON"
    OFF = "OFF"


class Features(str, Enum):
    """Switch entity features."""

    ON_OFF = "on_off"
    TOGGLE = "toggle"


class Attributes(str, Enum):
    """Switch entity attributes."""

    STATE = "state"


class Commands(str, Enum):
    """Switch entity commands."""

    ON = "on"
    OFF = "off"
    TOGGLE = "toggle"


class DeviceClasses(str, Enum):
    """Switch entity device classes."""

    OUTLET = "outlet"
    SWITCH = "switch"


class Options(str, Enum):
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
        features: list[Features],
        attributes: dict,
        device_class: DeviceClasses | None = None,
        options: dict | None = None,
        area: str | None = None,
    ):
        """
        Create switch-entity instance.

        :param identifier: entity identifier
        :param name: friendly name
        :param features: switch features
        :param attributes: switch attributes
        :param device_class: optional switch device class
        :param options: options
        :param area: optional area
        """
        super().__init__(
            identifier,
            name,
            Types.SWITCH,
            features,
            attributes,
            device_class,
            options,
            area,
        )

        LOG.debug("Switch entity created with id: %s", self.id)
