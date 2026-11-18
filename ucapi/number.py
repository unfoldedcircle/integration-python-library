"""
Number entity definitions.

:copyright: (c) 2026 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

from enum import StrEnum
from typing import Any

from .api_definitions import CommandHandler
from .entity import Entity, EntityTypes


class States(StrEnum):
    """Number entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    ON = "ON"
    """The entity is available. Default if the state attribute is omitted."""


class Features(StrEnum):
    """Number entity features."""

    VALUE = "value"
    """Read and set the value. Always present, even if not specified."""
    TRANSITION = "transition"
    """Support the optional duration parameter of the set_value command."""


class Attributes(StrEnum):
    """Number entity attributes."""

    STATE = "state"
    """Optional entity state."""
    VALUE = "value"
    """Current numeric value within the option bounds, or None if unknown."""


class Commands(StrEnum):
    """Number entity commands handled by the integration driver."""

    SET_VALUE = "set_value"
    """Set value, with an optional transition duration in milliseconds."""
    INCREMENT = "increment"
    """Increase by the optional step parameter or the step option, clamped at max."""
    DECREMENT = "decrement"
    """Decrease by the optional step parameter or the step option, clamped at min."""


class DeviceClasses(StrEnum):
    """Number entity device classes and their default units."""

    AUDIO_LEVEL = "audio_level"
    """Audio level in decibel (dB)."""
    BATTERY = "battery"
    """Battery charge level in percent (%)."""
    CURRENT = "current"
    """Electrical current in ampere (A)."""
    DURATION = "duration"
    """Time span in seconds (s); also supports ms, min, h and d."""
    ENERGY = "energy"
    """Energy in kilowatt-hour (kWh)."""
    HUMIDITY = "humidity"
    """Relative humidity in percent (%)."""
    ILLUMINANCE = "illuminance"
    """Illuminance in lux (lx)."""
    POWER = "power"
    """Power in watt (W)."""
    TEMPERATURE = "temperature"
    """Temperature in degrees Celsius, without automatic unit conversion."""
    VOLTAGE = "voltage"
    """Voltage in volt (V)."""


class Options(StrEnum):
    """Static number entity options, read when configured in the Remote."""

    MIN = "min"
    """Inclusive minimum, defaults to 0. None means no lower limit."""
    MAX = "max"
    """Inclusive maximum, defaults to 100. None means no upper limit."""
    STEP = "step"
    """Step size, at least 0.000001. Defaults to 1."""
    DECIMALS = "decimals"
    """Display precision from 0 to 6, otherwise derived from step and bounds."""
    UNIT = "unit"
    """Optional unit label, overriding the device class default unit."""
    DISPLAY_MODE = "display_mode"
    """Preferred UI representation, defaults to auto. See DisplayMode."""
    READABLE = "readable"
    """Whether the driver can read and report the current value. Defaults to True."""


class DisplayMode(StrEnum):
    """Preferred default representation of a number entity in the UI."""

    AUTO = "auto"
    """Let the UI choose based on the value range."""
    SLIDER = "slider"
    """Prefer a slider. Unbounded ranges are always shown as a stepper."""
    STEPPER = "stepper"
    """Prefer a value field with increment and decrement buttons."""


class Number(Entity):
    """
    Number entity class.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_number.md
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
        cmd_handler: CommandHandler = None,
    ):
        """
        Create a number-entity instance.

        :param identifier: entity identifier
        :param name: friendly name, either a string or a language dictionary
        :param features: number features; value is implicit even if omitted
        :param attributes: number attributes; state is optional, value may be None
        :param device_class: optional number device class
        :param options: static range, step, unit, display and readability options
        :param icon: optional icon
        :param description: optional description, either a string or a language dictionary
        :param area: optional area
        :param cmd_handler: handler for entity commands
        """
        super().__init__(
            identifier,
            name,
            EntityTypes.NUMBER,
            features,
            attributes,
            device_class=device_class,
            options=options,
            icon=icon,
            description=description,
            area=area,
            cmd_handler=cmd_handler,
        )
