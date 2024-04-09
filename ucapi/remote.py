"""
Remote entity definitions.

:copyright: (c) 2024 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

from dataclasses import KW_ONLY, dataclass
from enum import Enum
from typing import Any

from ucapi.api_definitions import CommandHandler
from ucapi.entity import Entity, EntityTypes


class States(str, Enum):
    """Remote entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    ON = "ON"
    OFF = "OFF"


class Features(str, Enum):
    """Remote entity features."""

    ON_OFF = "on_off"
    TOGGLE = "toggle"
    SEND_CMD = "send_cmd"


class Attributes(str, Enum):
    """Remote entity attributes."""

    STATE = "state"


class Commands(str, Enum):
    """Remote entity commands."""

    ON = "on"
    OFF = "off"
    TOGGLE = "toggle"
    SEND_CMD = "send_cmd"
    SEND_CMD_SEQUENCE = "send_cmd_sequence"


class Options(str, Enum):
    """Remote entity options."""

    SIMPLE_COMMANDS = "simple_commands"
    BUTTON_MAPPING = "button_mapping"
    USER_INTERFACE = "user_interface"


@dataclass
class EntityCommand:
    """Remote command definition for a button mapping or UI page definition."""

    cmd_id: str
    params: dict[str, str | int | list[str]] | None = None


def create_send_cmd(
    command: str,
    delay: int | None = None,
    repeat: int | None = None,
    hold: int | None = None,
) -> EntityCommand:
    """
    Create a send command.

    :param command: command to send.
    :param delay: optional delay in milliseconds after the command or between repeats.
    :param repeat: optional repeat count of the command.
    :param hold: optional hold time in milliseconds.
    :return: the created EntityCommand.
    """
    params = {"command": command}
    if delay:
        params["delay"] = delay
    if repeat:
        params["repeat"] = repeat
    if hold:
        params["hold"] = hold
    return EntityCommand(Commands.SEND_CMD.value, params)


def create_sequence_cmd(
    sequence: list[str],
    delay: int | None = None,
    repeat: int | None = None,
) -> EntityCommand:
    """
    Create a sequence command.

    :param sequence: list of simple commands.
    :param delay: optional delay in milliseconds between the commands in the sequence.
    :param repeat: optional repeat count of the sequence.
    :return: the created EntityCommand.
    """
    params = {"sequence": sequence}
    if delay:
        params["delay"] = delay
    if repeat:
        params["repeat"] = repeat
    return EntityCommand(Commands.SEND_CMD_SEQUENCE.value, params)


class Buttons(str, Enum):
    """Physical buttons."""

    BACK = "BACK"
    HOME = "HOME"
    VOICE = "VOICE"
    VOLUME_UP = "VOLUME_UP"
    VOLUME_DOWN = "VOLUME_DOWN"
    MUTE = "MUTE"
    DPAD_UP = "DPAD_UP"
    DPAD_DOWN = "DPAD_DOWN"
    DPAD_LEFT = "DPAD_LEFT"
    DPAD_RIGHT = "DPAD_RIGHT"
    DPAD_MIDDLE = "DPAD_MIDDLE"
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    BLUE = "BLUE"
    CHANNEL_UP = "CHANNEL_UP"
    CHANNEL_DOWN = "CHANNEL_DOWN"
    PREV = "PREV"
    PLAY = "PLAY"
    NEXT = "NEXT"
    POWER = "POWER"


@dataclass
class DeviceButtonMapping:
    """Physical button mapping."""

    button: str
    short_press: EntityCommand | None = None
    long_press: EntityCommand | None = None


def create_btn_mapping(
    button: Buttons,
    short: str | EntityCommand | None = None,
    long: str | EntityCommand | None = None,
) -> DeviceButtonMapping:
    """
    Create a physical button command mapping.

    :param button: physical button identifier.
    :param short: associated short-press command to the physical button.
                  A string parameter corresponds to a simple command, whereas an
                  ``EntityCommand`` allows to customize the command.
    :param long: associated long-press command to the physical button
    :return: the created DeviceButtonMapping
    """
    if isinstance(short, str):
        short = EntityCommand(short)
    if isinstance(long, str):
        long = EntityCommand(long)
    return DeviceButtonMapping(button.value, short_press=short, long_press=long)


@dataclass
class Size:
    """Item size in the button grid. Default size if not specified: 1x1."""

    width: int = 1
    height: int = 1


@dataclass
class Location:
    """Button placement in the grid with 0-based coordinates."""

    x: int
    y: int


@dataclass
class UiItem:
    """
    A user interface item is either an icon or text.

    - Icon and text items can be static or linked to a command specified in the
      `command` field.
    - Default size is 1x1 if not specified.
    """

    type: str
    location: Location
    size: Size | None = None
    icon: str | None = None
    text: str | None = None
    command: EntityCommand | None = None


def create_ui_text(
    text: str,
    x: int,
    y: int,
    size: Size | None = None,
    cmd: str | EntityCommand | None = None,
) -> UiItem:
    """
    Create a text UI item.

    :param text: the text to show in the UI item.
    :param x: x-position, 0-based.
    :param y: y-position, 0-based.
    :param size: item size, defaults to 1 x 1 if not specified.
    :param cmd: associated command to the text item. A string parameter corresponds to
                a simple command, whereas an ``EntityCommand`` allows to customize the
                command for example with number of repeats.
    :return: the created UiItem
    """
    if isinstance(cmd, str):
        cmd = EntityCommand(cmd)
    return UiItem("text", Location(x, y), size=size, text=text, command=cmd)


def create_ui_icon(
    icon: str,
    x: int,
    y: int,
    size: Size | None = None,
    cmd: str | EntityCommand | None = None,
) -> UiItem:
    """
    Create an icon UI item.

    The icon identifier consists of a prefix and a resource identifier,
    separated by `:`. Available prefixes:
      - `uc:` - integrated icon font
      - `custom:` - custom resource

    :param icon: the icon identifier of the icon to show in the UI item.
    :param x: x-position, 0-based.
    :param y: y-position, 0-based.
    :param size: item size, defaults to 1 x 1 if not specified.
    :param cmd: associated command to the text item. A string parameter corresponds to
                a simple command, whereas an ``EntityCommand`` allows to customize the
                command for example with number of repeats.
    :return: the created UiItem
    """
    if isinstance(cmd, str):
        cmd = EntityCommand(cmd)
    return UiItem("icon", Location(x, y), size=size, icon=icon, command=cmd)


@dataclass
class UiPage:
    """
    Definition of a complete user interface page.

    Default grid size is 4x6 if not specified.
    """

    page_id: str
    name: str
    _: KW_ONLY
    grid: Size = None
    items: list[UiItem] = None

    def __post_init__(self):
        """Post initialization to set required fields."""
        # grid and items are required Integration-API fields
        if self.grid is None:
            self.grid = Size(4, 6)
        if self.items is None:
            self.items = []

    def add(self, item: UiItem):
        """Append the given UiItem to the page items."""
        self.items.append(item)


class Remote(Entity):
    """
    Remote entity class.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_remote.md
    for more information.
    """  # noqa

    def __init__(
        self,
        identifier: str,
        name: str | dict[str, str],
        features: list[Features],
        attributes: dict[str, Any],
        simple_commands: list[str] | None = None,
        button_mapping: list[DeviceButtonMapping] | None = None,
        ui_pages: list[UiPage] | None = None,
        area: str | None = None,
        cmd_handler: CommandHandler = None,
    ):
        """
        Create remote entity instance.

        :param identifier: entity identifier
        :param name: friendly name
        :param features: remote features
        :param attributes: remote attributes
        :param simple_commands: optional list of supported remote command identifiers
        :param button_mapping: optional command mapping of physical buttons
        :param ui_pages: optional user interface page definitions
        :param area: optional area
        :param cmd_handler: handler for entity commands
        """
        options: dict[str, Any] = {}
        if simple_commands:
            options["simple_commands"] = simple_commands
        if button_mapping:
            options["button_mapping"] = button_mapping
        if ui_pages:
            options["user_interface"] = {"pages": ui_pages}
        super().__init__(
            identifier,
            name,
            EntityTypes.REMOTE,
            features,
            attributes,
            options=options,
            area=area,
            cmd_handler=cmd_handler,
        )
