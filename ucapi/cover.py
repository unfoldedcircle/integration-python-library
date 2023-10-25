import logging

from ucapi.entity import TYPES, Entity

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class STATES:
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    OPENING = "OPENING"
    OPEN = "OPEN"
    CLOSING = "CLOSING"
    CLOSED = "CLOSED"


class FEATURES:
    OPEN = "open"
    CLOSE = "close"
    STOP = "stop"
    POSITION = "position"
    TILT = "tilt"
    TILT_STOP = "tilt_stop"
    TILT_POSITION = "tilt_position"


class ATTRIBUTES:
    STATE = "state"
    POSITION = "position"
    TILT_POSITION = "tilt_position"


class COMMANDS:
    OPEN = "open"
    CLOSE = "close"
    STOP = "stop"
    POSITION = "position"
    TILT = "tilt"
    TILT_UP = "tilt_up"
    TILT_DOWN = "tilt_down"
    TILT_STOP = "tilt_stop"


class DEVICECLASSES:
    BLIND = "blind"
    CURTAIN = "curtain"
    GARAGE = "garage"
    SHADE = "shade"
    DOOR = "door"
    GATE = "gate"
    WINDOW = "window"


class OPTIONS:
    """"""


class Cover(Entity):
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
            TYPES.COVER,
            features,
            attributes,
            deviceClass,
            options,
            area,
        )

        LOG.debug("Cover entity created with id: %s", self.id)
