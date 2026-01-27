"""
Switch entity definitions.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

from enum import Enum
from typing import Any

from .api_definitions import CommandHandler
from .entity import Entity, EntityTypes


class States(str, Enum):
    """Select entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    ON = "ON"


class Features(str, Enum):
    """Select entity features."""


class Attributes(str, Enum):
    """Select entity attributes."""

    STATE = "state"
    CURRENT_OPTION = "current_option"
    OPTIONS = "options"


class Commands(str, Enum):
    """Select entity commands."""

    SELECT_OPTION = "select_option"
    SELECT_FIRST = "select_first"
    SELECT_LAST = "select_last"
    SELECT_NEXT = "select_next"
    SELECT_PREVIOUS = "select_previous"


class DeviceClasses(str, Enum):
    """Select entity device classes."""


class Options(str, Enum):
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
        area: str | None = None,
        cmd_handler: CommandHandler = None,
    ):
        """
        Create select-entity instance.

        :param identifier: entity identifier
        :param name: friendly name
        :param attributes: select attributes
        :param area: optional area
        :param cmd_handler: handler for entity commands
        """
        super().__init__(
            identifier,
            name,
            EntityTypes.SELECT,
            [],
            attributes,
            area=area,
            cmd_handler=cmd_handler,
        )
