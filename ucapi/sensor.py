import logging

from ucapi.entity import TYPES
from ucapi.entity import Entity

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class STATES:
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    ON = "ON"


class FEATURES:
    """"""


class ATTRIBUTES:
    STATE = "state"
    VALUE = "value"
    UNIT = "unit"


class COMMANDS:
    """"""


class DEVICECLASSES:
    CUSTOM = "custom"
    BATTERY = "battery"
    CURRENT = "current"
    ENERGY = "energy"
    HUMIDITY = "humidity"
    POWER = "power"
    TEMPERATURE = "temperature"
    VOLTAGE = "voltage"


class OPTIONS:
    CUSTOM_UNIT = "custom_unit"
    NATIVE_UNIT = "native_unit"
    DECIMALS = "decimals"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"


class Sensor(Entity):
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
            TYPES.SENSOR,
            features,
            attributes,
            deviceClass,
            options,
            area,
        )

        LOG.debug("Sensor entity created with id: %s", self.id)
