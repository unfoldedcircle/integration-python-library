"""
Cover entity definitions.

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
    """Cover entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    OPENING = "OPENING"
    OPEN = "OPEN"
    CLOSING = "CLOSING"
    CLOSED = "CLOSED"


class FEATURES(Enum):
    """Cover entity features."""

    OPEN = "open"
    CLOSE = "close"
    STOP = "stop"
    POSITION = "position"
    TILT = "tilt"
    TILT_STOP = "tilt_stop"
    TILT_POSITION = "tilt_position"


class ATTRIBUTES(Enum):
    """Cover entity attributes."""

    STATE = "state"
    POSITION = "position"
    TILT_POSITION = "tilt_position"


class COMMANDS(Enum):
    """Cover entity commands."""

    OPEN = "open"
    CLOSE = "close"
    STOP = "stop"
    POSITION = "position"
    TILT = "tilt"
    TILT_UP = "tilt_up"
    TILT_DOWN = "tilt_down"
    TILT_STOP = "tilt_stop"


class DEVICECLASSES(Enum):
    """Cover entity device classes."""

    BLIND = "blind"
    CURTAIN = "curtain"
    GARAGE = "garage"
    SHADE = "shade"
    DOOR = "door"
    GATE = "gate"
    WINDOW = "window"


class OPTIONS(Enum):
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
        features: list[FEATURES],
        attributes: dict,
        deviceClass: DEVICECLASSES | None = None,
        options: dict | None = None,
        area: str | None = None,
    ):
        """
        Create cover-entity instance.

        :param identifier: entity identifier
        :param name: friendly name
        :param features: cover features
        :param attributes: cover attributes
        :param deviceClass: optional cover device class
        :param options: options
        :param area: optional area
        """
        super().__init__(
            identifier,
            name,
            TYPES.COVER,
            features,
            attributes,
            deviceClass,
            options,
            area,
        )

        LOG.debug("Cover entity created with id: %s", self.id)
