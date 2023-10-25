"""
Media-player entity definitions.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL 2.0, see LICENSE for more details.
"""

import logging
from enum import Enum

from ucapi.entity import TYPES, Entity

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class STATES(Enum):
    """Media-player entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    ON = "ON"
    OFF = "OFF"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    STANDBY = "STANDBY"
    BUFFERING = "BUFFERING"


class FEATURES(Enum):
    """Media-player entity features."""

    ON_OFF = "on_off"
    TOGGLE = "toggle"
    VOLUME = "volume"
    VOLUME_UP_DOWN = "volume_up_down"
    MUTE_TOGGLE = "mute_toggle"
    MUTE = "mute"
    UNMUTE = "unmute"
    PLAY_PAUSE = "play_pause"
    STOP = "stop"
    NEXT = "next"
    PREVIOUS = "previous"
    FAST_FORWARD = "fast_forward"
    REWIND = "rewind"
    REPEAT = "repeat"
    SHUFFLE = "shuffle"
    SEEK = "seek"
    MEDIA_DURATION = "media_duration"
    MEDIA_POSITION = "media_position"
    MEDIA_TITLE = "media_title"
    MEDIA_ARTIST = "media_artist"
    MEDIA_ALBUM = "media_album"
    MEDIA_IMAGE_URL = "media_image_url"
    MEDIA_TYPE = "media_type"
    DPAD = "dpad"
    HOME = "home"
    MENU = "menu"
    COLOR_BUTTONS = "color_buttons"
    CHANNEL_SWITCHER = "channel_switcher"
    SELECT_SOURCE = "select_source"
    SELECT_SOUND_MODE = "select_sound_mode"


class ATTRIBUTES(Enum):
    """Media-player entity attributes."""

    STATE = "state"
    VOLUME = "volume"
    MUTED = "muted"
    MEDIA_DURATION = "media_duration"
    MEDIA_POSITION = "media_position"
    MEDIA_TYPE = "media_type"
    MEDIA_IMAGE_URL = "media_image_url"
    MEDIA_TITLE = "media_title"
    MEDIA_ARTIST = "media_artist"
    MEDIA_ALBUM = "media_album"
    REPEAT = "repeat"
    SHUFFLE = "shuffle"
    SOURCE = "source"
    SOURCE_LIST = "source_list"
    SOUND_MODE = "sound_mode"
    SOUND_MODE_LIST = "sound_mode_list"


class COMMANDS(Enum):
    """Media-player entity commands."""

    ON = "on"
    OFF = "off"
    TOGGLE = "toggle"
    PLAY_PAUSE = "play_pause"
    STOP = "stop"
    PREVIOUS = "previous"
    NEXT = "next"
    FAST_FORWARD = "fast_forward"
    REWIND = "rewind"
    SEEK = "seek"
    VOLUME = "volume"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    MUTE_TOGGLE = "mute_toggle"
    MUTE = "mute"
    UNMUTE = "unmute"
    REPEAT = "repeat"
    SHUFFLE = "shuffle"
    CHANNEL_UP = "channel_up"
    CHANNEL_DOWN = "channel_down"
    CURSOR_UP = "cursor_up"
    CURSOR_DOWN = "cursor_down"
    CURSOR_LEFT = "cursor_left"
    CURSOR_RIGHT = "cursor_right"
    CURSOR_ENTER = "cursor_enter"
    FUNCTION_RED = "function_red"
    FUNCTION_GREEN = "function_green"
    FUNCTION_YELLOW = "function_yellow"
    FUNCTION_BLUE = "function_blue"
    HOME = "home"
    MENU = "menu"
    BACK = "back"
    SELECT_SOURCE = "select_source"
    SELECT_SOUND_MODE = "select_sound_mode"
    SEARCH = "search"


class DEVICECLASSES(Enum):
    """Media-player entity device classes."""

    RECEIVER = "receiver"
    SET_TOP_BOX = "set_top_box"
    SPEAKER = "speaker"
    STREAMING_BOX = "streaming_box"
    TV = "tv"


class OPTIONS(Enum):
    """Media-player entity options."""

    VOLUME_STEPS = "volume_steps"


class MEDIA_TYPE(Enum):
    """Media types."""

    MUSIC = "MUSIC"
    RADIO = "RADIO"
    TVSHOW = "TVSHOW"
    MOVIE = "MOVIE"
    VIDEO = "VIDEO"


class MediaPlayer(Entity):
    """
    Media-player entity class.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_media_player.md
    for more information.
    """

    def __init__(self, id, name, features, attributes, deviceClass=None, options=None, area=None, type="default"):
        super().__init__(
            id,
            name,
            TYPES.MEDIA_PLAYER,
            features,
            attributes,
            deviceClass,
            options,
            area,
        )

        LOG.debug("MediaPlayer entity created with id: %s", self.id)
