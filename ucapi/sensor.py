"""
Sensor entity definitions.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

from enum import Enum
from typing import Any

from .entity import Entity, EntityTypes


class States(str, Enum):
    """Sensor entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    """The sensor is currently not available.
    The UI will render the sensor as inactive until the sensor becomes active again."""
    UNKNOWN = "UNKNOWN"
    """The sensor is available but the current state is unknown."""
    ON = "ON"
    """The sensor is available and providing measurements."""


class Features(str, Enum):
    """Sensor entity features."""


class Attributes(str, Enum):
    """Sensor entity attributes."""

    STATE = "state"
    """Optional state of the sensor."""
    VALUE = "value"
    """The native measurement value of the sensor."""
    UNIT = "unit"
    """Optional unit of the ``value`` if no default unit is set."""


class Commands(str, Enum):
    """Sensor entity commands."""


class DeviceClasses(str, Enum):
    """Sensor entity device classes.

    See https://unfoldedcircle.github.io/core-api/entities/entity_sensor.html
    for more information about binary sensors.
    """

    CUSTOM = "custom"
    """Generic sensor with custom unit"""
    BATTERY = "battery"
    """Battery charge in %"""
    CURRENT = "current"
    """Electrical current in ampere"""
    ENERGY = "energy"
    """Energy in kilowatt-hour"""
    HUMIDITY = "humidity"
    """Humidity in %"""
    POWER = "power"
    """Power in watt or kilowatt"""
    TEMPERATURE = "temperature"
    VOLTAGE = "voltage"
    """Voltage in volt"""
    BINARY = "binary"
    """Binary sensor.
     The binary specific device class is stored in the ``unit`` attribute."""


class Options(str, Enum):
    """Sensor entity options."""

    CUSTOM_UNIT = "custom_unit"
    """Unit label for a custom sensor if device_class is not specified or to override
     a default unit."""
    NATIVE_UNIT = "native_unit"
    """The sensor's native unit of measurement to perform automatic conversion.
     Applicable to device classes: ``temperature``."""
    DECIMALS = "decimals"
    """Number of decimal places to show in the UI if the sensor provides the measurement
     as a number. Not applicable to string values."""
    MIN_VALUE = "min_value"
    """Not yet supported.

    Optional minimum value of the sensor output. This can be used in the UI for graphs
    or gauges."""
    MAX_VALUE = "max_value"
    """Not yet supported.

    Optional maximum value of the sensor output. This can be used in the UI for graphs
    or gauges."""


class Sensor(Entity):
    """
    Sensor entity class.

    See https://unfoldedcircle.github.io/core-api/entities/entity_sensor.html
    for more information.
    """

    # pylint: disable=R0917
    def __init__(
        self,
        identifier: str,
        name: str | dict[str, str],
        features: list[Features],
        attributes: dict[str, Any],
        device_class: DeviceClasses | None = None,
        options: dict[str, Any] | None = None,
        area: str | None = None,
    ):
        """
        Create a sensor-entity instance.

        :param identifier: entity identifier
        :param name: friendly name
        :param features: sensor features
        :param attributes: sensor attributes
        :param device_class: optional sensor device class
        :param options: options
        :param area: optional area
        """
        super().__init__(
            identifier,
            name,
            EntityTypes.SENSOR,
            features,
            attributes,
            device_class=device_class,
            options=options,
            area=area,
        )
