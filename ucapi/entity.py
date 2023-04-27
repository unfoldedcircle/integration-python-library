class TYPES:
    COVER = "cover"
    BUTTON = "button"
    CLIMATE = "climate"
    LIGHT = "light"
    MEDIA_PLAYER = "media_player"
    SENSOR = "sensor"
    SWITCH = "switch"


class Entity:
    def __init__(
        self,
        id,
        name,
        entityType: TYPES,
        features,
        attributes,
        deviceClass,
        options,
        area,
        type="default",
    ):
        self.id = id
        self.name = {"en": name} if isinstance(name, str) else name
        self.entityType = entityType
        self.deviceId = None
        self.features = features
        self.attributes = attributes
        self.deviceClass = deviceClass
        self.options = options
        self.area = area
