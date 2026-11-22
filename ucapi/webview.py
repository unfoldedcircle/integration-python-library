"""
Webview entity definitions.

See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_webview.md
for more information.

:copyright: (c) 2026 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

from enum import StrEnum
from typing import Any, Literal, NotRequired, Required, TypeAlias, TypedDict

from .entity import Entity, EntityTypes


class States(StrEnum):
    """Web view entity states."""

    UNAVAILABLE = "UNAVAILABLE"
    """The entity is currently not available."""
    UNKNOWN = "UNKNOWN"
    """The entity is available, but the current state is unknown."""
    ON = "ON"
    """The web view can be shown."""


class Features(StrEnum):
    """Web view entity features. This entity has no features."""


class Attributes(StrEnum):
    """Web view entity attributes."""

    STATE = "state"
    """Optional state of the web view."""


class Commands(StrEnum):
    """
    Web view entity commands.

    The commands are executed by the user interface of the Remote and are never sent to an
    integration driver. In the Core-API, the command identifier has the entity type prefix,
    e.g. ``webview.open``.
    """

    OPEN = "open"
    """Wake the display and show the web view fullscreen with its start page."""
    RELOAD = "reload"
    """Reload the shown page, in the fullscreen web view or in the widget. No effect if not shown."""
    CLEAR_CACHE = "clear_cache"
    """Clear the HTTP cache of all web views and reload the shown page."""
    CLEAR_DATA = "clear_data"
    """Clear all website data of all web views, then reload the shown page.
    Credentials entered in a login dialog are kept until the user interface restarts."""


class Options(StrEnum):
    """Web view entity option fields."""

    URL = "url"
    """Start page of the web view: absolute ``http://`` or ``https://`` URL. Required."""
    AUTH = "auth"
    """Credentials sent to the origin of the ``url`` option."""
    TLS = "tls"
    """Exception for an invalid TLS certificate of the host of the ``url`` option."""
    COOKIES = "cookies"
    """Cookies set before the start page is loaded."""
    USER_AGENT = "user_agent"
    """User agent of the web view."""
    ZOOM = "zoom"
    """Page zoom in percent: 25..400. Default: 100. Can be overridden by the user."""
    BACKGROUND_COLOR = "background_color"
    """Background color while loading and behind transparent pages, as ``#RRGGBB``. Default: ``#FFFFFF``."""
    SHOW_NAVIGATION = "show_navigation"
    """Show back, forward, reload and close controls in the fullscreen web view. Default: False.
    Can be overridden by the user."""
    RELOAD_INTERVAL = "reload_interval"
    """Reload the page every n seconds while shown: 0 = off, otherwise 10..86400. Default: 0.
    Can be overridden by the user."""
    BUTTONS = "buttons"
    """Function of single physical buttons in the fullscreen web view. Can be overridden by the user."""
    DEVICE_API = "device_api"
    """Device state API for the pages of the web view: battery state, display state, power source,
    power profile and standby events. Default: False. Can be overridden by the user."""


class AuthType(StrEnum):
    """Web view authentication method."""

    NONE = "none"
    """No credentials."""
    BASIC = "basic"
    """``username`` and ``password``, sent as answer to an HTTP authentication request (status 401)
    of the origin. Not sent preemptively."""
    BEARER = "bearer"
    """``token``, sent as ``Authorization: Bearer <token>`` header with every request to the origin."""
    HEADER = "header"
    """``header_name`` and ``header_value``, sent as header with every request to the origin,
    e.g. an API key."""


class UserAgent(StrEnum):
    """Predefined user agents of a web view.

    Sent in the ``User-Agent`` header and returned in ``navigator.userAgent``.
    A custom user agent string (at most 256 characters) may also be used.
    """

    DEFAULT = "default"
    """The user agent of the Remote, which identifies the Remote and its firmware version."""
    MOBILE = "mobile"
    """The user agent of a common mobile browser, e.g. to get the mobile layout of a page."""
    DESKTOP = "desktop"
    """The user agent of a common desktop browser, e.g. to get the desktop layout of a page."""


class Button(StrEnum):
    """Physical button of the Remote customizable in the fullscreen web view.

    Uses the same identifier as in the button mapping of an activity.
    Not every Remote model has all buttons: ``RED``, ``GREEN``, ``YELLOW`` and ``BLUE`` are only
    on the Remote Two, ``RECORD``, ``STOP`` and ``MENU`` only on the Remote 3.
    The buttons in ``FIXED_BUTTONS`` can't be changed.
    """

    BACK = "BACK"
    DPAD_UP = "DPAD_UP"
    DPAD_DOWN = "DPAD_DOWN"
    DPAD_LEFT = "DPAD_LEFT"
    DPAD_RIGHT = "DPAD_RIGHT"
    DPAD_MIDDLE = "DPAD_MIDDLE"
    VOLUME_UP = "VOLUME_UP"
    VOLUME_DOWN = "VOLUME_DOWN"
    CHANNEL_UP = "CHANNEL_UP"
    CHANNEL_DOWN = "CHANNEL_DOWN"
    MUTE = "MUTE"
    PREV = "PREV"
    PLAY = "PLAY"
    NEXT = "NEXT"
    STOP = "STOP"
    RECORD = "RECORD"
    MENU = "MENU"
    RED = "RED"
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    BLUE = "BLUE"


FIXED_BUTTONS: tuple[str, ...] = ("HOME", "POWER", "VOICE")
"""Physical buttons with a fixed function in the web view, which can't be changed:
``HOME`` always closes the web view, ``POWER`` and ``VOICE`` keep their normal function."""


class ButtonFunction(StrEnum):
    """Web view function of a physical button."""

    ZOOM_IN = "zoom_in"
    """Zoom the page in by one step. The changed zoom isn't saved to the entity."""
    ZOOM_OUT = "zoom_out"
    """Zoom the page out by one step. The changed zoom isn't saved to the entity."""
    ZOOM_RESET = "zoom_reset"
    """Zoom back to the effective ``zoom`` option of the web view."""
    SCROLL_UP = "scroll_up"
    """Scroll the page up by a small step."""
    SCROLL_DOWN = "scroll_down"
    """Scroll the page down by a small step."""
    PAGE_UP = "page_up"
    """Scroll the page up by one screen."""
    PAGE_DOWN = "page_down"
    """Scroll the page down by one screen."""
    TOP = "top"
    """Scroll to the top of the page."""
    BOTTOM = "bottom"
    """Scroll to the bottom of the page."""
    BACK = "back"
    """Go back in the history of the web view."""
    FORWARD = "forward"
    """Go forward in the history of the web view."""
    BACK_OR_CLOSE = "back_or_close"
    """Go back in the history, or close the web view on its first page."""
    RELOAD = "reload"
    """Reload the page."""
    STOP = "stop"
    """Stop loading the page."""
    CLOSE = "close"
    """Close the web view and return to the previous screen."""
    TOGGLE_NAVIGATION = "toggle_navigation"
    """Show or hide the navigation controls. The change isn't saved to the entity."""
    FOCUS_NEXT = "focus_next"
    """Move the focus to the next element of the page, like ``Tab`` on a keyboard."""
    FOCUS_PREVIOUS = "focus_previous"
    """Move the focus to the previous element of the page, like ``Shift+Tab`` on a keyboard."""
    NONE = "none"
    """The button does nothing."""


class ButtonKey(StrEnum):
    """
    Key event of a physical button, sent to the page.

    Values match ``KeyboardEvent.key`` of the UI Events key values specification.
    """

    ARROW_UP = "ArrowUp"
    ARROW_DOWN = "ArrowDown"
    ARROW_LEFT = "ArrowLeft"
    ARROW_RIGHT = "ArrowRight"
    ENTER = "Enter"
    ESCAPE = "Escape"
    BACKSPACE = "Backspace"
    TAB = "Tab"
    PAGE_UP = "PageUp"
    PAGE_DOWN = "PageDown"
    HOME = "Home"
    END = "End"
    CONTEXT_MENU = "ContextMenu"
    BROWSER_BACK = "BrowserBack"
    BROWSER_FORWARD = "BrowserForward"
    BROWSER_REFRESH = "BrowserRefresh"
    BROWSER_STOP = "BrowserStop"
    EXIT = "Exit"
    AUDIO_VOLUME_UP = "AudioVolumeUp"
    AUDIO_VOLUME_DOWN = "AudioVolumeDown"
    AUDIO_VOLUME_MUTE = "AudioVolumeMute"
    CHANNEL_UP = "ChannelUp"
    CHANNEL_DOWN = "ChannelDown"
    MEDIA_PLAY_PAUSE = "MediaPlayPause"
    MEDIA_PLAY = "MediaPlay"
    MEDIA_PAUSE = "MediaPause"
    MEDIA_STOP = "MediaStop"
    MEDIA_RECORD = "MediaRecord"
    MEDIA_REWIND = "MediaRewind"
    MEDIA_FAST_FORWARD = "MediaFastForward"
    MEDIA_TRACK_PREVIOUS = "MediaTrackPrevious"
    MEDIA_TRACK_NEXT = "MediaTrackNext"
    COLOR_F0_RED = "ColorF0Red"
    COLOR_F1_GREEN = "ColorF1Green"
    COLOR_F2_YELLOW = "ColorF2Yellow"
    COLOR_F3_BLUE = "ColorF3Blue"


class ButtonActionType(StrEnum):
    """Action type discriminator for a physical button in the fullscreen web view."""

    PASS = "pass"
    """Keep the normal function of the button (e.g. volume control of the current activity)."""
    FUNCTION = "function"
    """Run a web view function defined by ``ButtonFunction``."""
    KEY = "key"
    """Send a DOM key event defined by ``ButtonKey`` to the page."""


class WebviewAuth(TypedDict, total=False):
    """
    Web view credentials, only sent to the origin of the ``url`` option.

    ``password``, ``token`` and ``header_value`` are secrets.
    """

    type: Required[AuthType | str]
    username: NotRequired[str]
    password: NotRequired[str]
    token: NotRequired[str]
    header_name: NotRequired[str]
    header_value: NotRequired[str]


class WebviewTls(TypedDict, total=False):
    """Exception for an invalid TLS certificate of the host of the ``url`` option."""

    certificate_sha256: NotRequired[str]
    allow_invalid_certificate: NotRequired[bool]


class WebviewCookie(TypedDict, total=False):
    """Cookie of a web view, set before the start page is loaded each time the web view is opened."""

    name: Required[str]
    value: Required[str]
    domain: NotRequired[str]
    path: NotRequired[str]
    secure: NotRequired[bool]
    http_only: NotRequired[bool]
    expires: NotRequired[str]


class WebviewButtonActionPass(TypedDict):
    """Pass-through button action."""

    action: Literal["pass"]


class WebviewButtonActionFunction(TypedDict):
    """Web view function button action."""

    action: Literal["function"]
    function: ButtonFunction | str


class WebviewButtonActionKey(TypedDict):
    """DOM key event button action."""

    action: Literal["key"]
    key: ButtonKey | str


WebviewButtonAction: TypeAlias = (
    WebviewButtonActionPass | WebviewButtonActionFunction | WebviewButtonActionKey
)


class WebviewEntityOptions(TypedDict, total=False):
    """
    Web view entity options.

    The origin (scheme, host and port) of the ``url`` option is the scope of ``auth``,
    ``cookies`` and ``tls``: they are never applied to another origin.
    """

    url: Required[str]
    auth: NotRequired[WebviewAuth]
    tls: NotRequired[WebviewTls]
    cookies: NotRequired[list[WebviewCookie]]
    user_agent: NotRequired[UserAgent | str]
    zoom: NotRequired[int]
    background_color: NotRequired[str]
    show_navigation: NotRequired[bool]
    reload_interval: NotRequired[int]
    buttons: NotRequired[dict[Button | str, WebviewButtonAction]]
    device_api: NotRequired[bool]


class Webview(Entity):
    """
    Web view entity class.

    A web view entity shows a web page on the Remote, fullscreen or in an activity widget.
    The web page is rendered by the user interface of the Remote. The integration driver only
    provides the entity definition and never receives commands for a web view entity.

    See https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_webview.md
    for more information.
    """

    # pylint: disable=R0917
    def __init__(
        self,
        identifier: str,
        name: str | dict[str, str],
        options: WebviewEntityOptions | dict[str, Any],
        *,
        attributes: dict[str, Any] | None = None,
        icon: str | None = None,
        description: str | dict[str, str] | None = None,
        area: str | None = None,
    ):
        """
        Create a webview-entity instance.

        :param identifier: entity identifier
        :param name: friendly name, either a string or a language dictionary
        :param options: web view options; must contain a non-empty ``url``
        :param attributes: optional web view attributes (e.g. ``state``)
        :param icon: optional icon
        :param description: optional description, either a string or a language dictionary
        :param area: optional area
        :raises TypeError: if ``options`` is not a dictionary
        :raises ValueError: if ``options`` does not contain a non-empty ``url`` string
        """
        if not isinstance(options, dict):
            raise TypeError(f"options must be dict, got {type(options).__name__}")
        url = options.get(Options.URL)
        if not isinstance(url, str) or not url.strip():
            raise ValueError("options must contain a non-empty 'url' string")

        super().__init__(
            identifier,
            name,
            EntityTypes.WEBVIEW,
            [],
            attributes if attributes is not None else {},
            options=options,
            icon=icon,
            description=description,
            area=area,
        )
