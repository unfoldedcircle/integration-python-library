"""
Button entity definitions.

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
    """Button entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    AVAILABLE = "AVAILABLE"


class ATTRIBUTES(Enum):
    """Button entity attributes."""

    STATE = "state"


class COMMANDS(Enum):
    """Button entity commands."""

    PUSH = "push"


class Button(Entity):
    """
    Button entity class.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_button.md
    for more information.
    """

    def __init__(self, id, name, area=None, type="default"):
        super().__init__(
            id,
            name,
            TYPES.BUTTON,
            ["press"],
            {ATTRIBUTES.STATE: STATES.AVAILABLE},
            None,
            None,
            area,
        )

        LOG.debug("Button entity created with id: %s", self.id)
