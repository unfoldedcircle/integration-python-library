import logging

from ucapi.entity import TYPES, Entity

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class STATES:
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    ON = "ON"
    OFF = "OFF"


class FEATURES:
    ON_OFF = "on_off"
    TOGGLE = "toggle"


class ATTRIBUTES:
    STATE = "state"


class COMMANDS:
    ON = "on"
    OFF = "off"
    TOGGLE = "toggle"


class DEVICECLASSES:
    OUTLET = "outlet"
    SWITCH = "switch"


class OPTIONS:
    READABLE = "readable"


class Switch(Entity):
    def __init__(
        self,
        id,
        name,
        features,
        attributes,
        deviceClass=None,
        options=None,
        area=None,
        type="default",
    ):
        super().__init__(
            id,
            name,
            TYPES.SWITCH,
            features,
            attributes,
            deviceClass,
            options,
            area,
        )

        LOG.debug("Switch entity created with id: %s", self.id)
