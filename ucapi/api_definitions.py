"""
API definitions.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL-2.0, see LICENSE for more details.
"""

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Any, Awaitable, Callable, TypeAlias


class DeviceStates(str, Enum):
    """Device states."""

    CONNECTED = "CONNECTED"
    CONNECTING = "CONNECTING"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"


class StatusCodes(IntEnum):
    """Response status codes."""

    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    TIMEOUT = 408
    CONFLICT = 409
    SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503


class IntegrationSetupError(str, Enum):
    """More detailed error reason for ``state: ERROR`` condition."""

    NONE = "NONE"
    NOT_FOUND = "NOT_FOUND"
    CONNECTION_REFUSED = "CONNECTION_REFUSED"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    TIMEOUT = "TIMEOUT"
    OTHER = "OTHER"


# Does WsMessages need to be public?
class WsMessages(str, Enum):
    """WebSocket request messages from Remote Two/3."""

    AUTHENTICATION = "authentication"
    GET_DRIVER_VERSION = "get_driver_version"
    GET_DEVICE_STATE = "get_device_state"
    GET_AVAILABLE_ENTITIES = "get_available_entities"
    GET_ENTITY_STATES = "get_entity_states"
    SUBSCRIBE_EVENTS = "subscribe_events"
    UNSUBSCRIBE_EVENTS = "unsubscribe_events"
    ENTITY_COMMAND = "entity_command"
    GET_DRIVER_METADATA = "get_driver_metadata"
    SETUP_DRIVER = "setup_driver"
    SET_DRIVER_USER_DATA = "set_driver_user_data"


# Does WsMsgEvents need to be public?
class WsMsgEvents(str, Enum):
    """WebSocket event messages from Remote Two/3."""

    CONNECT = "connect"
    DISCONNECT = "disconnect"
    ENTER_STANDBY = "enter_standby"
    EXIT_STANDBY = "exit_standby"
    DRIVER_VERSION = "driver_version"
    DEVICE_STATE = "device_state"
    AVAILABLE_ENTITIES = "available_entities"
    ENTITY_STATES = "entity_states"
    ENTITY_CHANGE = "entity_change"
    DRIVER_METADATA = "driver_metadata"
    DRIVER_SETUP_CHANGE = "driver_setup_change"
    ABORT_DRIVER_SETUP = "abort_driver_setup"
    ASSISTANT_EVENT = "assistant_event"


class Events(str, Enum):
    """Internal library events."""

    CLIENT_CONNECTED = "client_connected"
    """WebSocket client connected."""
    CLIENT_DISCONNECTED = "client_disconnected"
    """WebSocket client disconnected."""
    ENTITY_ATTRIBUTES_UPDATED = "entity_attributes_updated"
    SUBSCRIBE_ENTITIES = "subscribe_entities"
    """Integration API `subscribe_events` message."""
    UNSUBSCRIBE_ENTITIES = "unsubscribe_entities"
    """Integration API `unsubscribe_events` message."""
    CONNECT = "connect"
    """Integration-API `connect` event message."""
    DISCONNECT = "disconnect"
    """Integration-API `disconnect` event message."""
    ENTER_STANDBY = "enter_standby"
    """Integration-API `enter_standby` event message."""
    EXIT_STANDBY = "exit_standby"
    """Integration-API `exit_standby` event message."""


# Does EventCategory need to be public?
class EventCategory(str, Enum):
    """Event categories."""

    DEVICE = "DEVICE"
    ENTITY = "ENTITY"


class SetupDriver:
    """Driver setup request base class."""


@dataclass
class DriverSetupRequest(SetupDriver):
    """
    Start driver setup.

    If a driver includes a ``setup_data_schema`` object in its driver metadata, it
    enables the dynamic driver setup process. The setup process can be a simple
    "start-confirm-done" between the Remote Two/3 and the integration driver, or a fully
    dynamic, multistep process with user interactions, where the user has to provide
    additional data or select different options.

    If the initial setup page contains input fields and not just text, the input values
    are returned in the ``setup_data`` dictionary. The key is the input field
    identifier, value contains the input value.
    """

    reconfigure: bool
    setup_data: dict[str, str]


@dataclass
class UserDataResponse(SetupDriver):
    """
    Provide requested driver setup data to the integration driver in a setup process.

    The ``input_values`` dictionary contains the user input data. The key is the input
    field identifier, value contains the input value.
    """

    input_values: dict[str, str]


@dataclass
class UserConfirmationResponse(SetupDriver):
    """
    Provide user confirmation response to the integration driver in a setup process.

    The ``confirm`` field is set to ``true`` if the user had to perform an action like
    pressing a button on a device and then confirms the action with continuing the
    setup process.
    """

    confirm: bool


@dataclass
class AbortDriverSetup(SetupDriver):
    """
    Abort notification.

    - ``error == OTHER``: the user cancelled the setup flow.
    - ``error == TIMEOUT``: timeout occurred, most likely because of no user input.
    """

    error: IntegrationSetupError


class SetupAction:
    """Setup action response base class."""


@dataclass
class RequestUserInput(SetupAction):
    """Setup action to request user input."""

    title: str | dict[str, str]
    settings: list[dict[str, Any]]


@dataclass
class RequestUserConfirmation(SetupAction):
    """Setup action to request a user confirmation."""

    title: str | dict[str, str]
    header: str | dict[str, str] | None = None
    image: str | None = None
    footer: str | dict[str, str] | None = None


@dataclass
class SetupError(SetupAction):
    """Setup action to abort setup process due to an error."""

    error_type: IntegrationSetupError = IntegrationSetupError.OTHER


class SetupComplete(SetupAction):
    """Setup action to complete a successful setup process."""


CommandHandler: TypeAlias = Callable[
    [Any, str, dict[str, Any] | None, Any | None], Awaitable[StatusCodes]
]
"""Entity command handler signature.

Parameters:

- entity: entity instance
- cmd_id: command identifier
- params: optional command parameters
- websocket: optional client connection for sending directed events

Returns: status code
"""


SetupHandler: TypeAlias = Callable[[SetupDriver], Awaitable[SetupAction]]


# ---------------------------------------------------------------------------
# Assistant event message definitions
# ---------------------------------------------------------------------------


class AssistantEventType(str, Enum):
    """Type discriminator for assistant event messages."""

    READY = "ready"
    STT_RESPONSE = "stt_response"
    TEXT_RESPONSE = "text_response"
    SPEECH_RESPONSE = "speech_response"
    FINISHED = "finished"
    ERROR = "error"


class AssistantErrorCode(str, Enum):
    """Error codes for assistant processing."""

    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INVALID_AUDIO = "INVALID_AUDIO"
    NO_TEXT_RECOGNIZED = "NO_TEXT_RECOGNIZED"
    INTENT_FAILED = "INTENT_FAILED"
    TTS_FAILED = "TTS_FAILED"
    TIMEOUT = "TIMEOUT"
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"


@dataclass
class AssistantSttResponse:
    """Transcription result of the user's speech input."""

    text: str


@dataclass
class AssistantTextResponse:
    """Textual response and success flag for the processed command."""

    success: bool
    text: str


@dataclass
class AssistantSpeechResponse:
    """Reference to a TTS audio response provided by the integration driver."""

    url: str
    mime_type: str


@dataclass
class AssistantError:
    """Error detail for a failed assistant processing attempt."""

    code: AssistantErrorCode
    message: str


AssistantEventData: TypeAlias = (
    AssistantSttResponse
    | AssistantTextResponse
    | AssistantSpeechResponse
    | AssistantError
)


@dataclass
class AssistantEvent:
    """Assistant event payload sent via the ``assistant_event`` message.

    This payload is emitted by the integration driver to start the audio stream and
    to provide optional feedback about voice command processing and outcome.
    """

    type: AssistantEventType
    entity_id: str
    session_id: int
    data: AssistantEventData | None = None
