"""
Cover entity definitions.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

from enum import Enum

from ucapi.entity import Entity, EntityTypes


class States(str, Enum):
    """Cover entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    OPENING = "OPENING"
    OPEN = "OPEN"
    CLOSING = "CLOSING"
    CLOSED = "CLOSED"


class Features(str, Enum):
    """Cover entity features."""

    OPEN = "open"
    CLOSE = "close"
    STOP = "stop"
    POSITION = "position"
    TILT = "tilt"
    TILT_STOP = "tilt_stop"
    TILT_POSITION = "tilt_position"


class Attributes(str, Enum):
    """Cover entity attributes."""

    STATE = "state"
    POSITION = "position"
    TILT_POSITION = "tilt_position"


class Commands(str, Enum):
    """Cover entity commands."""

    OPEN = "open"
    CLOSE = "close"
    STOP = "stop"
    POSITION = "position"
    TILT = "tilt"
    TILT_UP = "tilt_up"
    TILT_DOWN = "tilt_down"
    TILT_STOP = "tilt_stop"


class DeviceClasses(str, Enum):
    """Cover entity device classes."""

    BLIND = "blind"
    CURTAIN = "curtain"
    GARAGE = "garage"
    SHADE = "shade"
    DOOR = "door"
    GATE = "gate"
    WINDOW = "window"


class Options(str, Enum):
    """Cover entity options."""


class Cover(Entity):
    """
    Cover entity class.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_cover.md
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
        Create cover-entity instance.

        :param identifier: entity identifier
        :param name: friendly name
        :param features: cover features
        :param attributes: cover attributes
        :param device_class: optional cover device class
        :param options: options
        :param area: optional area
        """
        super().__init__(
            identifier,
            name,
            EntityTypes.COVER,
            features,
            attributes,
            device_class,
            options,
            area,
        )
