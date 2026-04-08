"""
Switch entity definitions.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

from enum import StrEnum
from typing import Any

from .api_definitions import CommandHandler
from .entity import Entity, EntityTypes


class States(StrEnum):
    """Switch entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    ON = "ON"
    OFF = "OFF"


class Features(StrEnum):
    """Switch entity features."""

    ON_OFF = "on_off"
    TOGGLE = "toggle"


class Attributes(StrEnum):
    """Switch entity attributes."""

    STATE = "state"


class Commands(StrEnum):
    """Switch entity commands."""

    ON = "on"
    OFF = "off"
    TOGGLE = "toggle"


class DeviceClasses(StrEnum):
    """Switch entity device classes."""

    OUTLET = "outlet"
    SWITCH = "switch"


class Options(StrEnum):
    """Switch entity options."""

    READABLE = "readable"


class Switch(Entity):
    """
    Switch entity class.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_switch.md
    for more information.
    """

    # pylint: disable=R0917
    def __init__(
        self,
        identifier: str,
        name: str | dict[str, str],
        features: list[Features],
        attributes: dict[str, Any],
        *,
        device_class: DeviceClasses | None = None,
        options: dict[str, Any] | None = None,
        icon: str | None = None,
        description: str | dict[str, str] | None = None,
        area: str | None = None,
        cmd_handler: CommandHandler = None,
    ):
        """
        Create switch-entity instance.

        :param identifier: entity identifier
        :param name: friendly name
        :param features: switch features
        :param attributes: switch attributes
        :param device_class: optional switch device class
        :param options: options
        :param icon: optional icon
        :param description: optional description, either a string or a language dictionary
        :param area: optional area
        :param cmd_handler: handler for entity commands
        """
        super().__init__(
            identifier,
            name,
            EntityTypes.SWITCH,
            features,
            attributes,
            device_class=device_class,
            options=options,
            icon=icon,
            description=description,
            area=area,
            cmd_handler=cmd_handler,
        )
