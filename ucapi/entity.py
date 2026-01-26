"""
Entity definitions.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

import inspect
import logging
from enum import Enum
from typing import Any

from .api_definitions import CommandHandler, StatusCodes

_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.DEBUG)


class EntityTypes(str, Enum):
    """Entity types."""

    COVER = "cover"
    BUTTON = "button"
    CLIMATE = "climate"
    LIGHT = "light"
    MEDIA_PLAYER = "media_player"
    REMOTE = "remote"
    SELECT = "select"
    SENSOR = "sensor"
    SWITCH = "switch"
    IR_EMITTER = "ir_emitter"
    VOICE_ASSISTANT = "voice_assistant"


class CommonStates(str, Enum):
    """Common entity states available in all entities."""

    UNAVAILABLE = "UNAVAILABLE"
    """The entity is currently not available.
    The UI will render the entity as inactive until the entity becomes active again."""
    UNKNOWN = "UNKNOWN"
    """The entity is available but the current state is unknown."""


class Entity:
    """
    Entity base class.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/
    for more information.

    A client can either use a ``CommandHandler`` callback or extend a concrete Entity
    class and override the ``command()`` method.
    """

    # pylint: disable=R0917
    def __init__(
        self,
        identifier: str,
        name: str | dict[str, str],
        entity_type: EntityTypes,
        features: list[str],
        attributes: dict[str, Any],
        *,
        device_class: str | None = None,
        options: dict[str, Any] | None = None,
        area: str | None = None,
        cmd_handler: CommandHandler = None,
    ):
        """
        Initialize entity.

        :param identifier: entity identifier
        :param name: friendly name, either a string or a language dictionary
        :param entity_type: entity type
        :param features: entity feature array
        :param attributes: entity attributes
        :param device_class: entity device class
        :param options: entity options
        :param area: optional area name
        :param cmd_handler: optional handler for entity commands
        """
        self.id = identifier
        self.name = {"en": name} if isinstance(name, str) else name
        self.entity_type = entity_type
        self.device_id = None
        self.features = features
        self.attributes = attributes
        self.device_class = device_class
        self.options = options
        self.area = area
        self._cmd_handler = cmd_handler
        self._ext_cmd_handler = False

        # check if we got an extended command handler with the websocket kwarg
        if cmd_handler:
            try:
                sig = inspect.signature(cmd_handler)
                params_map = sig.parameters
                self._ext_cmd_handler = "websocket" in params_map or any(
                    p.kind is inspect.Parameter.VAR_KEYWORD for p in params_map.values()
                )
            except (TypeError, ValueError):
                # Some callables (builtins, C-extensions, functools.partial edge cases)
                # may not have an introspectable signature. Fall back to safe call.
                _LOG.warning(
                    "Old CommandHandler signature detected for %s, using old signature. Please update the command handler.",
                    self.id,
                )

        _LOG.debug("Created %s entity: %s", self.entity_type.value, self.id)

    async def command(
        self,
        cmd_id: str,
        params: dict[str, Any] | None = None,
        *,
        websocket: Any,
    ) -> StatusCodes:
        """
        Execute entity command with the installed command handler.

        Backward compatible:
        - Existing handlers usually accept (entity, cmd_id, params)
        - New handlers may optionally accept websocket as kw-only / kwarg

        Returns NOT_IMPLEMENTED if no command handler is installed.

        :param cmd_id: the command
        :param params: optional command parameters
        :param websocket: optional websocket connection. Allows for directed event
                          callbacks instead of broadcasts.
        :return: command status code to acknowledge to UCR2
        """
        handler = self._cmd_handler
        if not handler:
            _LOG.warning(
                "No command handler for %s: cannot execute command '%s' %s",
                self.id,
                cmd_id,
                params if params else "",
            )
            return StatusCodes.NOT_IMPLEMENTED

        # Decide if we can pass websocket as a keyword argument
        if self._ext_cmd_handler:
            return await handler(self, cmd_id, params, websocket=websocket)

        return await handler(self, cmd_id, params)
