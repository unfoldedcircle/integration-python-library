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
        identifier: str,
        name: str | dict,
        entity_type: TYPES,
        features: list[str],
        attributes: dict,
        device_class: str | None,
        options: dict | None,
        area: str | None = None,
    ):
        """
        Initialize entity.

        :param identifier: entity identifier
        :param name: friendly name, either a string or a language dictionary
        :param entity_type: entity type
        :param features: entity feature array
        :param attributes: entity attributes
        :param device_class: entity device class
        :param options: entity options
        :param area: optional area name
        """
        self.id = identifier
        self.name = {"en": name} if isinstance(name, str) else name
        self.entityType = entity_type
        self.deviceId = None
        self.features = features
        self.attributes = attributes
        self.deviceClass = device_class
        self.options = options
        self.area = area
