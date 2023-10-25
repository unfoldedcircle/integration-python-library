"""
Entity definitions.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL 2.0, see LICENSE for more details.
"""

from enum import Enum


class TYPES(Enum):
    """Entity types."""

    COVER = "cover"
    BUTTON = "button"
    CLIMATE = "climate"
    LIGHT = "light"
    MEDIA_PLAYER = "media_player"
    SENSOR = "sensor"
    SWITCH = "switch"


class Entity:
    """
    Entity base class.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/
    for more information.
    """

    def __init__(
        self,
        id,
        name,
        entityType: TYPES,
        features,
        attributes,
        deviceClass,
        options,
        area,
        type="default",
    ):
        self.id = id
        self.name = {"en": name} if isinstance(name, str) else name
        self.entityType = entityType
        self.deviceId = None
        self.features = features
        self.attributes = attributes
        self.deviceClass = deviceClass
        self.options = options
        self.area = area
