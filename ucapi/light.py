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
    DIM = "dim"
    COLOR = "color"
    COLOR_TEMPERATURE = "color_temperature"


class ATTRIBUTES:
    STATE = "state"
    HUE = "hue"
    SATURATION = "saturation"
    BRIGHTNESS = "brightness"
    COLOR_TEMPERATURE = "color_temperature"


class COMMANDS:
    ON = "on"
    OFF = "off"
    TOGGLE = "toggle"


class DEVICECLASSES:
    """"""


class OPTIONS:
    COLOR_TEMPERATURE_STEPS = "color_temperature_steps"


class Light(Entity):
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
            TYPES.LIGHT,
            features,
            attributes,
            deviceClass,
            options,
            area,
        )

        LOG.debug("Light entity created with id: %s", self.id)
