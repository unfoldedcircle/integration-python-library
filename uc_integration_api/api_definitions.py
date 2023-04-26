from enum import IntEnum

class DEVICE_STATES():
    CONNECTED = 'CONNECTED'
    CONNECTING = 'CONNECTING'
    DISCONNECTED = 'DISCONNECTED'
    ERROR = 'ERROR'

class STATUS_CODES(IntEnum):
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503

class MESSAGES():
    AUTHENTICATION = 'authentication'
    GET_DRIVER_VERSION = 'get_driver_version'
    GET_DEVICE_STATE = 'get_device_state'
    GET_AVAILABLE_ENTITIES = 'get_available_entities'
    GET_ENTITY_STATES = 'get_entity_states'
    SUBSCRIBE_EVENTS = 'subscribe_events'
    UNSUBSCRIBE_EVENTS = 'unsubscribe_events'
    ENTITY_COMMAND = 'entity_command'
    GET_DRIVER_METADATA = 'get_driver_metadata'
    SETUP_DRIVER = 'setup_driver'
    SET_DRIVER_USER_DATA = 'set_driver_user_data'

class MSG_EVENTS():
    CONNECT = 'connect'
    DISCONNECT = 'disconnect'
    DRIVER_VERSION = 'driver_version'
    DEVICE_STATE = 'device_state'
    AVAILABLE_ENTITIES = 'available_entities'
    ENTITY_STATES = 'entity_states'
    ENTITY_CHANGE = 'entity_change'
    DRIVER_METADATA = 'driver_metadata'
    DRIVER_SETUP_CHANGE = 'driver_setup_change'
    ABORT_DRIVER_SETUP = 'abort_driver_setup'

class EVENTS():
    ENTITY_COMMAND = 'entity_command'
    ENTITY_ATTRIBUTES_UPDATED = 'entity_attributes_updated'
    SUBSCRIBE_ENTITIES = 'subscribe_entities'
    UNSUBSCRIBE_ENTITIES = 'unsubscribe_entities'
    SETUP_DRIVER = 'setup_driver'
    SETUP_DRIVER_USER_DATA = 'setup_driver_user_data'
    SETUP_DRIVER_USER_CONFIRMATION = 'setup_driver_user_confirmation'
    SETUP_DRIVER_ABORT = 'setup_driver_abort'
    CONNECT = 'connect'
    DISCONNECT = 'disconnect'

class EVENT_CATEGORY():
    DEVICE = 'DEVICE'
    ENTITY = 'ENTITY'