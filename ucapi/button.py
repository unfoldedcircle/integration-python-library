import logging

from ucapi.entity import TYPES
from ucapi.entity import Entity

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class STATES:
    UNAVAILABLE = "UNAVAILABLE"
    AVAILABLE = "AVAILABLE"


class ATTRIBUTES:
    STATE = "state"


class COMMANDS:
    PUSH = "push"


class Button(Entity):
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
