"""
Sensor entity definitions.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

from enum import StrEnum
from typing import Any

from .entity import Entity, EntityTypes


class States(StrEnum):
    """Sensor entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    """The sensor is currently not available.
    The UI will render the sensor as inactive until the sensor becomes active again."""
    UNKNOWN = "UNKNOWN"
    """The sensor is available but the current state is unknown."""
    ON = "ON"
    """The sensor is available and providing measurements."""


class Features(StrEnum):
    """Sensor entity features."""


class Attributes(StrEnum):
    """Sensor entity attributes."""

    STATE = "state"
    """Optional state of the sensor."""
    VALUE = "value"
    """The native measurement value of the sensor."""
    UNIT = "unit"
    """Optional unit of the ``value`` if no default unit is set."""


class Commands(StrEnum):
    """Sensor entity commands."""


class DeviceClasses(StrEnum):
    """Sensor entity device classes.

    The ``timestamp``, ``date`` and ``duration`` device classes are formatted by the
    UI as a date, time or time span, with the localization settings of the Remote. The
    value must be sent in the specified machine-readable format and must not be
    formatted for display.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_sensor.md
    for more information.
    """

    CUSTOM = "custom"
    """Generic sensor with custom unit"""
    BATTERY = "battery"
    """Battery charge in %"""
    CURRENT = "current"
    """Electrical current in ampere"""
    DATE = "date"
    """Calendar date without a time. Value: text in ISO 8601 format ``YYYY-MM-DD``,
    e.g. ``2026-11-15``."""
    DURATION = "duration"
    """Time span, default unit: s. Supported units: ``ms``, ``s``, ``min``, ``h``, ``d``.
    Value: number in the unit of the sensor.

    A value in ``min``, ``h`` or ``d`` is shown as a time span in the unit of the sensor
    and the next smaller unit, e.g. ``1.5`` hours as ``1h 30m``. A value in ``ms`` or
    ``s`` is shown as a number with the unit."""
    ENERGY = "energy"
    """Energy in kilowatt-hour"""
    HUMIDITY = "humidity"
    """Humidity in %"""
    POWER = "power"
    """Power in watt or kilowatt"""
    TEMPERATURE = "temperature"
    """Temperature with automatic °C, °F conversion, depending on remote settings.
    Use native_unit option if the temperature is measured in °F."""
    TIMESTAMP = "timestamp"
    """Point in time. Value: text in RFC 3339 format, including the UTC offset, e.g.
    ``2026-11-15T04:23:31+00:00``."""
    VOLTAGE = "voltage"
    """Voltage in volt"""
    BINARY = "binary"
    """Binary sensor.
    The binary specific device class is stored in the ``unit`` attribute."""


class Options(StrEnum):
    """Sensor entity options."""

    CUSTOM_LABEL = "custom_label"
    """Label for a custom sensor if device_class is not specified or to override a
    default unit."""
    CUSTOM_UNIT = "custom_unit"
    """Unit label for a custom sensor if device_class is not specified or to override
    a default unit."""
    NATIVE_UNIT = "native_unit"
    """The sensor's native unit of measurement to perform automatic conversion.
    Applicable to device classes: ``temperature``."""
    DECIMALS = "decimals"
    """Number of decimal places to show in the UI if the sensor provides the
    measurement as a number. Not applicable to string values and the ``timestamp`` and
    ``date`` device classes. A ``duration`` value is rounded to this number of decimal
    places before it is formatted as a time span."""
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

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_sensor.md
    for more information.
    """

    # pylint: disable=R0917
    def __init__(
        self,
        identifier: str,
        name: str | dict[str, str],
        features: list[Features],
        attributes: dict[str, Any],
        *,
        device_class: DeviceClasses | None = None,
        options: dict[str, Any] | None = None,
        icon: str | None = None,
        description: str | dict[str, str] | None = None,
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
        :param icon: optional icon
        :param description: optional description, either a string or a language dictionary
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
            icon=icon,
            description=description,
            area=area,
        )
