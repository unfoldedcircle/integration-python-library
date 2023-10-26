"""
Button entity definitions.

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
    """Button entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    AVAILABLE = "AVAILABLE"


class Attributes(str, Enum):
    """Button entity attributes."""

    STATE = "state"


class Commands(str, Enum):
    """Button entity commands."""

    PUSH = "push"


class Button(Entity):
    """
    Button entity class.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_button.md
    for more information.
    """

    def __init__(self, identifier: str, name: str | dict, area: str | None = None):
        """
        Create button-entity instance.

        :param identifier: entity identifier
        :param name: friendly name, either a string or a language dictionary
        :param area: optional area name
        """
        super().__init__(
            identifier,
            name,
            Types.BUTTON,
            ["press"],
            {Attributes.STATE: States.AVAILABLE},
            None,
            None,
            area,
        )

        LOG.debug("Button entity created with id: %s", self.id)
