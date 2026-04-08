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
    """Select entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    ON = "ON"


class Features(StrEnum):
    """Select entity features."""


class Attributes(StrEnum):
    """Select entity attributes."""

    STATE = "state"
    CURRENT_OPTION = "current_option"
    OPTIONS = "options"


class Commands(StrEnum):
    """Select entity commands."""

    SELECT_OPTION = "select_option"
    SELECT_FIRST = "select_first"
    SELECT_LAST = "select_last"
    SELECT_NEXT = "select_next"
    SELECT_PREVIOUS = "select_previous"


class DeviceClasses(StrEnum):
    """Select entity device classes."""


class Options(StrEnum):
    """Select entity options."""


class Select(Entity):
    """
    Select entity class.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_select.md
    for more information.
    """

    # pylint: disable=R0917
    def __init__(
        self,
        identifier: str,
        name: str | dict[str, str],
        attributes: dict[str, Any],
        *,
        icon: str | None = None,
        description: str | dict[str, str] | None = None,
        area: str | None = None,
        cmd_handler: CommandHandler = None,
    ):
        """
        Create select-entity instance.

        :param identifier: entity identifier
        :param name: friendly name
        :param attributes: select attributes
        :param icon: optional icon
        :param description: optional description, either a string or a language dictionary
        :param area: optional area
        :param cmd_handler: handler for entity commands
        """
        super().__init__(
            identifier,
            name,
            EntityTypes.SELECT,
            [],
            attributes,
            icon=icon,
            description=description,
            area=area,
            cmd_handler=cmd_handler,
        )
