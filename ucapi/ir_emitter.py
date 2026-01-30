"""
IR Emitter entity definitions.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

from enum import Enum
from typing import Any

from .api_definitions import CommandHandler
from .entity import Entity, EntityTypes


class States(str, Enum):
    """IR Emitter entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    ON = "ON"


class Features(str, Enum):
    """IR Emitter entity features."""

    SEND_IR = "send_ir"


class Attributes(str, Enum):
    """IR Emitter entity attributes."""

    STATE = "state"


class Commands(str, Enum):
    """IR Emitter entity commands."""

    SEND_IR = "send_ir"
    STOP_IR = "stop_ir"


class DeviceClasses(str, Enum):
    """IR Emitter entity device classes."""


class Options(str, Enum):
    """IR Emitter entity options."""

    PORTS = "ports"
    IR_FORMATS = "ir_formats"


class IREmitter(Entity):
    """
    IR Emitter entity class.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_ir_emitter.md
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
        options: dict[str, Any] | None = None,
        area: str | None = None,
        cmd_handler: CommandHandler = None,
    ):
        """
        Create IR Emitter instance.

        :param identifier: entity identifier
        :param name: friendly name
        :param features: IR Emitter features
        :param attributes: IR Emitter attributes
        :param options: IR Emitter options
        :param area: optional area
        :param cmd_handler: handler for entity commands
        """
        super().__init__(
            identifier,
            name,
            EntityTypes.IR_EMITTER,
            features,
            attributes,
            options=options,
            area=area,
            cmd_handler=cmd_handler,
        )
