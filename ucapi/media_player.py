"""
Media-player entity definitions.

See https://unfoldedcircle.github.io/core-api/entities/entity_media_player.html
for the media-player entity documentation.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

import logging
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from .api_definitions import (
    CommandHandler,
    Pagination,
    Paging,
    StatusCodes,
)
from .entity import Entity, EntityTypes, validate_str

_LOG = logging.getLogger(__name__)


class States(StrEnum):
    """Media-player entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    """The entity is currently not available. The UI will render the entity as inactive until the entity becomes active again."""
    UNKNOWN = "UNKNOWN"
    """The entity is available but the current state is unknown."""
    ON = "ON"
    """The media player is switched on"""
    OFF = "OFF"
    """The media player is switched off"""
    PLAYING = "PLAYING"
    """The media player is playing something"""
    PAUSED = "PAUSED"
    """The media player is paused"""
    STANDBY = "STANDBY"
    """The device is in low power state and accepting commands"""
    BUFFERING = "BUFFERING"
    """The media player is buffering to start playback"""


class Features(StrEnum):
    """Media-player entity features."""

    ON_OFF = "on_off"
    """The media player can be switched on and off."""
    TOGGLE = "toggle"
    """The media player's power state can be toggled."""
    VOLUME = "volume"
    """The volume level can be set to a specific level."""
    VOLUME_UP_DOWN = "volume_up_down"
    """The volume can be adjusted up (louder) and down."""
    MUTE_TOGGLE = "mute_toggle"
    """The mute state can be toggled."""
    MUTE = "mute"
    """The volume can be muted."""
    UNMUTE = "unmute"
    """The volume can be un-muted."""
    PLAY_PAUSE = "play_pause"
    """The player supports starting and pausing media playback."""
    STOP = "stop"
    """The player supports stopping media playback."""
    NEXT = "next"
    """The player supports skipping to the next track."""
    PREVIOUS = "previous"
    """The player supports returning to the previous track."""
    FAST_FORWARD = "fast_forward"
    """The player supports fast-forwarding the current track."""
    REWIND = "rewind"
    """The player supports rewinding the current track."""
    REPEAT = "repeat"
    """The current track or playlist can be repeated."""
    SHUFFLE = "shuffle"
    """The player supports random playback / shuffling the current playlist."""
    SEEK = "seek"
    """The player supports seeking the playback position."""
    MEDIA_DURATION = "media_duration"
    """The player announces the duration of the current media being played."""
    MEDIA_POSITION = "media_position"
    """The player announces the current position of the media being played."""
    MEDIA_TITLE = "media_title"
    """The player announces the media title."""
    MEDIA_ARTIST = "media_artist"
    """The player announces the media artist."""
    MEDIA_ALBUM = "media_album"
    """The player announces the media album if music is being played."""
    MEDIA_IMAGE_URL = "media_image_url"
    """The player provides an image url of the media being played."""
    MEDIA_TYPE = "media_type"
    """The player announces the content type of media being played."""
    DPAD = "dpad"
    """Directional pad navigation provides cursor_up, _down, _left, _right, _enter commands."""
    NUMPAD = "numpad"
    """Number pad, provides digit_0 .. digit_9 commands."""
    HOME = "home"
    """Home navigation support with home and back commands."""
    MENU = "menu"
    """Menu navigation support with menu and back commands."""
    CONTEXT_MENU = "context_menu"
    """Context menu (for example, right-clicking or long pressing an item)."""
    GUIDE = "guide"
    """Program guide support with guide and back commands."""
    INFO = "info"
    """Information popup / menu support with info and back commands."""
    COLOR_BUTTONS = "color_buttons"
    """Color button support for function_red, _green, _yellow, _blue commands."""
    CHANNEL_SWITCHER = "channel_switcher"
    """Channel zapping support with channel_up and _down commands."""
    SELECT_SOURCE = "select_source"
    """Media playback sources or inputs can be selected."""
    SELECT_SOUND_MODE = "select_sound_mode"
    """Sound modes can be selected, e.g., stereo or surround."""
    EJECT = "eject"
    """The media can be ejected, e.g., a slot-in CD or USB stick."""
    OPEN_CLOSE = "open_close"
    """The player supports opening and closing, e.g., a disc tray."""
    AUDIO_TRACK = "audio_track"
    """The player supports selecting or switching the audio track."""
    SUBTITLE = "subtitle"
    """The player supports selecting or switching subtitles."""
    RECORD = "record"
    """The player has recording capabilities with record, my_recordings, live commands."""
    SETTINGS = "settings"
    """The player supports a settings menu."""
    PLAY_MEDIA = "play_media"
    """The player supports playing a specific media item."""
    PLAY_MEDIA_ACTION = "play_media_action"
    """The player supports the play_media action parameter to either play or enqueue."""
    CLEAR_PLAYLIST = "clear_playlist"
    """The player allows clearing the active playlist."""
    BROWSE_MEDIA = "browse_media"
    """The player supports browsing media containers."""
    SEARCH_MEDIA = "search_media"
    """The player supports searching for media items."""
    SEARCH_MEDIA_CLASSES = "search_media_classes"
    """The player provides a list of media classes as filter for searches."""


class Attributes(StrEnum):
    """Media-player entity attributes."""

    STATE = "state"
    """State of the media player, influenced by the play and power commands."""
    VOLUME = "volume"
    """Current volume level."""
    MUTED = "muted"
    """Flag if the volume is muted."""
    MEDIA_DURATION = "media_duration"
    """Media duration in seconds."""
    MEDIA_POSITION = "media_position"
    """Current media position in seconds."""
    MEDIA_POSITION_UPDATED_AT = "media_position_updated_at"
    """Optional timestamp when `media_position` was last updated."""
    MEDIA_TYPE = "media_type"
    """The content type of media being played. Either a ``MediaContentType`` or a custom value."""
    MEDIA_IMAGE_URL = "media_image_url"
    """URL to retrieve the album art or an image representing what's being played."""
    MEDIA_TITLE = "media_title"
    """Currently playing media information."""
    MEDIA_ARTIST = "media_artist"
    """Currently playing media information."""
    MEDIA_ALBUM = "media_album"
    """Currently playing media information."""
    REPEAT = "repeat"
    """Current repeat mode."""
    SHUFFLE = "shuffle"
    """Shuffle mode on or off."""
    SOURCE = "source"
    """Currently selected media or input source."""
    SOURCE_LIST = "source_list"
    """Available media or input sources."""
    SOUND_MODE = "sound_mode"
    """Currently selected sound mode."""
    SOUND_MODE_LIST = "sound_mode_list"
    """Available sound modes."""
    MEDIA_ID = "media_id"
    """The content ID of media being played."""
    MEDIA_PLAYLIST = "media_playlist"
    """Title of Playlist currently playing."""
    PLAY_MEDIA_ACTION = "play_media_action"
    """List of supported media play actions in ``MediaPlayAction``."""
    SEARCH_MEDIA_CLASSES = "search_media_classes"
    """List of ``MediaClass`` values to use as a filter for ``search_media``.

     Custom classes should be avoided.
     """


class Commands(StrEnum):
    """Media-player entity commands."""

    ON = "on"
    """Switch on media player."""
    OFF = "off"
    """Switch off media player."""
    TOGGLE = "toggle"
    """Toggle the current power state, either from on -> off or from off -> on."""
    PLAY_PAUSE = "play_pause"
    """Toggle play / pause."""
    STOP = "stop"
    """Stop playback."""
    PREVIOUS = "previous"
    """Go back to previous track."""
    NEXT = "next"
    """Skip to next track."""
    FAST_FORWARD = "fast_forward"
    """Fast forward current track."""
    REWIND = "rewind"
    """Rewind current track."""
    SEEK = "seek"
    """Seek to given position in current track. Position is given in seconds."""
    VOLUME = "volume"
    """Set volume to given level."""
    VOLUME_UP = "volume_up"
    """Increase volume."""
    VOLUME_DOWN = "volume_down"
    """Decrease volume."""
    MUTE_TOGGLE = "mute_toggle"
    """Toggle mute state."""
    MUTE = "mute"
    """Mute volume."""
    UNMUTE = "unmute"
    """Unmute volume."""
    REPEAT = "repeat"
    """Repeat track or playlist."""
    SHUFFLE = "shuffle"
    """Shuffle playlist or start random playback."""
    CHANNEL_UP = "channel_up"
    """Channel up."""
    CHANNEL_DOWN = "channel_down"
    """Channel down."""
    CURSOR_UP = "cursor_up"
    """Directional pad up"""
    CURSOR_DOWN = "cursor_down"
    """Directional pad down"""
    CURSOR_LEFT = "cursor_left"
    """Directional pad left"""
    CURSOR_RIGHT = "cursor_right"
    """Directional pad right"""
    CURSOR_ENTER = "cursor_enter"
    """Directional pad enter"""
    DIGIT_0 = "digit_0"
    """Number pad digit 0."""
    DIGIT_1 = "digit_1"
    """Number pad digit 1."""
    DIGIT_2 = "digit_2"
    """Number pad digit 2."""
    DIGIT_3 = "digit_3"
    """Number pad digit 3."""
    DIGIT_4 = "digit_4"
    """Number pad digit 4."""
    DIGIT_5 = "digit_5"
    """Number pad digit 5."""
    DIGIT_6 = "digit_6"
    """Number pad digit 6."""
    DIGIT_7 = "digit_7"
    """Number pad digit 7."""
    DIGIT_8 = "digit_8"
    """Number pad digit 8."""
    DIGIT_9 = "digit_9"
    """Number pad digit 9."""
    FUNCTION_RED = "function_red"
    """Function red."""
    FUNCTION_GREEN = "function_green"
    """Function green."""
    FUNCTION_YELLOW = "function_yellow"
    """Function yellow."""
    FUNCTION_BLUE = "function_blue"
    """Function blue."""
    HOME = "home"
    """Home menu"""
    MENU = "menu"
    """General menu"""
    CONTEXT_MENU = "context_menu"
    """Context menu"""
    GUIDE = "guide"
    """Program guide menu."""
    INFO = "info"
    """Information menu / what's playing."""
    BACK = "back"
    """Back / exit function for menu navigation."""
    SELECT_SOURCE = "select_source"
    """Select media playback source or input from the available sources."""
    SELECT_SOUND_MODE = "select_sound_mode"
    """Select a sound mode from the available modes."""
    RECORD = "record"
    """Start, stop or open recording menu (device dependant)."""
    MY_RECORDINGS = "my_recordings"
    """Open recordings."""
    LIVE = "live"
    """Switch to live view."""
    EJECT = "eject"
    """Eject media."""
    OPEN_CLOSE = "open_close"
    """Open or close."""
    AUDIO_TRACK = "audio_track"
    """Switch or select audio track."""
    SUBTITLE = "subtitle"
    """Switch or select subtitle."""
    SETTINGS = "settings"
    """Settings menu"""
    SEARCH = "search"
    """Search for media."""
    PLAY_MEDIA = "play_media"
    """Play or enqueue a media item."""
    CLEAR_PLAYLIST = "clear_playlist"
    """Remove all items from the playback queue. Current playback behavior is integration-dependent (keep playing the current item or clearing everything)."""


class DeviceClasses(StrEnum):
    """Media-player entity device classes."""

    RECEIVER = "receiver"
    """Audio-video receiver."""
    SET_TOP_BOX = "set_top_box"
    """Set-top box for multichannel video and media playback."""
    SPEAKER = "speaker"
    """Smart speakers or stereo device."""
    STREAMING_BOX = "streaming_box"
    """Device for media streaming services."""
    TV = "tv"
    """Television device."""


class Options(StrEnum):
    """Media-player entity options."""

    SIMPLE_COMMANDS = "simple_commands"
    """Additional commands the media-player supports, which are not covered in the feature list.

    Example: ``["EXIT", "THUMBS_UP", "THUMBS_DOWN"]``
    """
    VOLUME_STEPS = "volume_steps"
    """Number of available volume steps for the set volume command and UI controls.

    Examples: 100 = any value between 0..100, 50 = only odd numbers, 3 = [33, 67, 100] etc. Value 0 = mute.

    Note: if the integration receives an "unexpected" number it is required to round up or down to the next matching value.
    """


class MediaContentType(StrEnum):
    """Pre-defined media content types.

    The media content type is for playback/content semantics.
    It represents the type of the media content to play or that is currently playing.

    An integration may return other values, but the UI will most likely handle them as
    an "unknown media."
    """

    ALBUM = "album"
    APP = "app"
    APPS = "apps"
    ARTIST = "artist"
    CHANNEL = "channel"
    CHANNELS = "channels"
    COMPOSER = "composer"
    EPISODE = "episode"
    GAME = "game"
    GENRE = "genre"
    IMAGE = "image"
    MOVIE = "movie"
    MUSIC = "music"
    PLAYLIST = "playlist"
    PODCAST = "podcast"
    RADIO = "radio"
    SEASON = "season"
    TRACK = "track"
    TV_SHOW = "tv_show"
    URL = "url"
    VIDEO = "video"


class MediaClass(StrEnum):
    """Pre-defined media classes for media browsing.

    The media class is for browser/structure semantics.
    It represents how a media item should be presented and organized in the
    media browser hierarchy.

    An integration may return other values, but the UI will most likely treat them as
    generic media without custom icons.
    """

    ALBUM = "album"
    APP = "app"
    ARTIST = "artist"
    CHANNEL = "channel"
    COMPOSER = "composer"
    DIRECTORY = "directory"
    EPISODE = "episode"
    GAME = "game"
    GENRE = "genre"
    IMAGE = "image"
    MOVIE = "movie"
    MUSIC = "music"
    PLAYLIST = "playlist"
    PODCAST = "podcast"
    RADIO = "radio"
    SEASON = "season"
    TRACK = "track"
    TV_SHOW = "tv_show"
    URL = "url"
    VIDEO = "video"


@dataclass
class BrowseOptions:
    """
    Browsing media options.

    Attributes:
        media_id (str | None):
            Optional media content ID to restrict browsing.
        media_type (str | None):
            Optional media content type to restrict browsing.
        stable_ids (bool | None):
            Hint to the integration to return stable media IDs.
        paging (Paging):
            Paging object to limit returned items. Defaults to a default Paging instance.
    """

    media_id: str | None = None
    media_type: str | None = None
    stable_ids: bool | None = None
    paging: Paging = field(default_factory=Paging)

    @classmethod
    def from_dict(cls, data: dict) -> "BrowseOptions":
        """Construct from a raw dictionary (e.g., from JSON)."""
        paging_data = data.get("paging")
        paging = (
            Paging.from_dict(paging_data)
            if isinstance(paging_data, dict)
            else paging_data
        )

        return cls(
            media_id=data.get("media_id"),
            media_type=data.get("media_type"),
            stable_ids=data.get("stable_ids"),
            paging=paging if paging is not None else Paging(),
        )


@dataclass
class SearchMediaFilter:
    """
    Search media filter options.

    Attributes:
        media_classes (list[MediaClass | str] | None):
            Optional list of media classes to filter the results.
        artist (str | None):
            Optional artist name.
        album (str | None):
            Optional album name.
    """

    media_classes: list[MediaClass | str] | None = None
    artist: str | None = None
    album: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "SearchMediaFilter":
        """Construct from a raw dictionary (e.g., from JSON)."""
        return cls(
            media_classes=data.get("media_classes"),
            artist=data.get("artist"),
            album=data.get("album"),
        )

    def __post_init__(self):
        """Encode custom fields."""
        if self.media_classes:
            self.media_classes = [
                (
                    # pylint: disable=protected-access
                    MediaClass(media_class)
                    if media_class in MediaClass._value2member_map_
                    else media_class
                )
                for media_class in self.media_classes
            ]


@dataclass(kw_only=True)
class SearchOptions:
    """
    Searching media options.

    Attributes:
        query (str):
            Free text search query.
        media_id (str | None):
            Optional media content ID to restrict searching.
        media_type (str | None):
            Optional media content type to restrict searching.
        stable_ids (bool | None):
            Hint to the integration to return stable media IDs.
        filter (SearchMediaFilter | None):
            Optional media filter to restrict searching.
        paging (Paging):
            Paging object to limit returned items. Defaults to a default Paging instance.
    """

    query: str
    media_id: str | None = None
    media_type: str | None = None
    stable_ids: bool | None = None
    filter: SearchMediaFilter | None = None
    paging: Paging = field(default_factory=Paging)

    @classmethod
    def from_dict(cls, data: dict) -> "SearchOptions":
        """Construct from a raw dictionary (e.g., from JSON)."""
        paging_data = data.get("paging")
        paging = (
            Paging.from_dict(paging_data)
            if isinstance(paging_data, dict)
            else paging_data
        )

        filter_data = data.get("filter")
        search_filter = (
            SearchMediaFilter.from_dict(filter_data)
            if isinstance(filter_data, dict)
            else filter_data
        )

        return cls(
            query=data.get("query", ""),
            media_id=data.get("media_id"),
            media_type=data.get("media_type"),
            stable_ids=data.get("stable_ids"),
            filter=search_filter,
            paging=paging if paging is not None else Paging(),
        )


@dataclass
class BrowseMediaItem:
    """Browse Media Item object."""

    media_id: str
    """Unique identifier of the media item."""
    title: str
    """Display name. Max 255 characters."""
    subtitle: str | None = None
    """Optional subtitle. Max 255 characters."""
    artist: str | None = None
    """Optional artist name. Max 255 characters."""
    album: str | None = None
    """Optional album name. Max 255 characters."""
    media_class: MediaClass | str | None = None
    """The media class for browsing."""
    media_type: MediaContentType | str | None = None
    """The media content type."""
    can_browse: bool | None = None
    """If `true`, the item can be browsed (is a container) by using ``media_id`` and ``media_type``."""
    can_play: bool | None = None
    """If ``true``, the item can be played directly using the ``play_media`` command with ``media_id`` and ``media_type``."""
    can_search: bool | None = None
    """If ``true``, a search can be performed on the item using ``search_media`` with ``media_id`` and ``media_type``."""
    thumbnail: str | None = None
    """URL to download the media artwork, or a base64 encoded PNG or JPG image.
    The preferred size is 480x480 pixels.
    Use the following URI prefix to use a provided icon: ``icon://uc:``, for example, ``icon://uc:music``.
    Please use a URL whenever possible. Encoded images should be as small as possible.
    """
    duration: int | None = None
    """Duration in seconds."""
    items: list["BrowseMediaItem"] | None = None
    """Child items if this item is a container. Child items may not contain further child items (only one level
    of nesting is supported). A new browse request must be sent for deeper levels.
    """

    def __post_init__(self) -> None:
        """Validate the object."""
        # mandatory fields
        validate_str("media_id", self.media_id)
        validate_str("title", self.title)

        # optional fields
        if self.subtitle is not None:
            validate_str("subtitle", self.subtitle)
        if self.artist is not None:
            validate_str("artist", self.artist)
        if self.album is not None:
            validate_str("album", self.album)
        if isinstance(self.media_class, str):
            validate_str("media_class", self.media_class, 0)
        if isinstance(self.media_type, str):
            validate_str("media_type", self.media_type, 0)
        if self.thumbnail is not None:
            validate_str("thumbnail", self.thumbnail, 1, 32768)


@dataclass(kw_only=True)
class BrowseResults:
    """
    Browsing media results.

    Attributes:
        media (BrowseMediaItem | None):
            The browsed media item, or `undefined` if not found.
        pagination (Pagination):
            Pagination metadata for this result page.
    """

    media: BrowseMediaItem | None = None
    pagination: Pagination


SearchMediaItem = BrowseMediaItem


@dataclass
class SearchResults:
    """
    Searching media results.

    Attributes:
        media (list[BrowseMediaItem]):
            Array of matching media items. Pass an empty array if no results were found.
        pagination (Pagination):
            Pagination metadata for this result page.
    """

    media: list[SearchMediaItem]
    pagination: Pagination


class RepeatMode(StrEnum):
    """Repeat modes."""

    OFF = "OFF"
    ALL = "ALL"
    ONE = "ONE"


class MediaPlayAction(StrEnum):
    """Media Play actions."""

    PLAY_NOW = "PLAY_NOW"
    PLAY_NEXT = "PLAY_NEXT"
    ADD_TO_QUEUE = "ADD_TO_QUEUE"


class MediaPlayer(Entity):
    """
    Media-player entity class.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_media_player.md
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
        cmd_handler: CommandHandler = None,
    ):
        """
        Create a media-player entity instance.

        :param identifier: entity identifier
        :param name: friendly name
        :param features: media-player features
        :param attributes: media-player attributes
        :param device_class: optional media-player device class
        :param options: options
        :param area: optional area
        :param cmd_handler: handler for entity commands
        """
        super().__init__(
            identifier,
            name,
            EntityTypes.MEDIA_PLAYER,
            features,
            attributes,
            device_class=device_class,
            options=options,
            area=area,
            cmd_handler=cmd_handler,
        )

    async def browse(self, options: BrowseOptions) -> BrowseResults | StatusCodes:
        """
        Execute entity browsing request.

        Returns NOT_IMPLEMENTED if no handler is installed.

        :param options: browsing parameters
        :return: browsing response or status code if any error occurs
        """
        _LOG.warning(
            "Media browsing not supported for %s. Request: %s",
            self.id,
            options,
        )
        return StatusCodes.NOT_IMPLEMENTED

    async def search(self, options: SearchOptions) -> SearchResults | StatusCodes:
        """
        Execute a media search request.

        Returns NOT_IMPLEMENTED if no handler is installed.

        :param options: search parameters
        :return: search response or status code if any error occurs
        """
        _LOG.warning(
            "Media searching not supported for %s. Request: %s",
            self.id,
            options,
        )
        return StatusCodes.NOT_IMPLEMENTED
