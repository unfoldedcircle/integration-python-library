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
    OFF = "OFF"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"


class FEATURES:
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
    SOURCE = "source"
    SOUND_MODE = "sound_mode"


class ATTRIBUTES:
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


class COMMANDS:
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
    SOURCE = "source"
    SOUND_MODE = "sound_mode"
    SEARCH = "search"


class DEVICECLASSES:
    RECEIVER = "receiver"
    SPEAKER = "speaker"


class OPTIONS:
    VOLUME_STEPS = "volume_steps"


class MediaPlayer(Entity):
    def __init__(self, id, name, features, attributes, deviceClass = None, options = None, area=None, type="default"):
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
