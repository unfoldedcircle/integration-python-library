"""
API definitions.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL 2.0, see LICENSE for more details.
"""

from enum import Enum, IntEnum


class DEVICE_STATES(str, Enum):
    """Device states."""

    CONNECTED = "CONNECTED"
    CONNECTING = "CONNECTING"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"


class STATUS_CODES(IntEnum):
    """Response status codes."""

    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503


class MESSAGES(str, Enum):
    """Request messages from Remote Two."""

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


class MSG_EVENTS(str, Enum):
    """Event messages from Remote Two."""

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


class EVENTS(str, Enum):
    """Internal events."""

    ENTITY_COMMAND = "entity_command"
    ENTITY_ATTRIBUTES_UPDATED = "entity_attributes_updated"
    SUBSCRIBE_ENTITIES = "subscribe_entities"
    UNSUBSCRIBE_ENTITIES = "unsubscribe_entities"
    SETUP_DRIVER = "setup_driver"
    SETUP_DRIVER_USER_DATA = "setup_driver_user_data"
    SETUP_DRIVER_USER_CONFIRMATION = "setup_driver_user_confirmation"
    SETUP_DRIVER_ABORT = "setup_driver_abort"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    ENTER_STANDBY = "enter_standby"
    EXIT_STANDBY = "exit_standby"


class EVENT_CATEGORY(str, Enum):
    """Event categories."""

    DEVICE = "DEVICE"
    ENTITY = "ENTITY"
