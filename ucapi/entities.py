import logging

from pyee import AsyncIOEventEmitter

from ucapi.api_definitions import EVENTS
from ucapi.entity import Entity

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class Entities:
    def __init__(self, id, loop, type="default"):
        self.id = id
        self._loop = loop
        self._storage = {}
        self.events = AsyncIOEventEmitter(self._loop)

    def contains(self, id):
        return id in self._storage

    def getEntity(self, id):
        if id not in self._storage:
            LOG.debug("ENTITIES(%s): Entity does not exists with id: %s", self.id, id)
            return None

        return self._storage[id]

    def addEntity(self, entity: Entity):
        if entity.id in self._storage:
            LOG.debug("ENTITIES(%s): Entity already exists with id: %s", self.id, entity.id)
            return False

        self._storage[entity.id] = entity
        LOG.debug("ENTITIES(%s): Entity added with id: %s", self.id, entity.id)
        return True

    def removeEntity(self, id):
        if id not in self._storage:
            LOG.debug("ENTITIES(%s): Entity does not exists with id: %s", self.id, id)
            return True

        del self._storage[id]
        LOG.debug("ENTITIES(%s): Entity deleted with id: %s", self.id, id)
        return True

    def updateEntityAttributes(self, id, attributes):
        if id not in self._storage:
            LOG.debug("ENTITIES(%s): Entity does not exists with id: %s", self.id, id)
            return True

        for key in attributes:
            self._storage[id].attributes[key] = attributes[key]

        self.events.emit(
            EVENTS.ENTITY_ATTRIBUTES_UPDATED,
            id,
            self._storage[id].entityType,
            attributes,
        )

        LOG.debug("ENTITIES(%s): Entity attributes updated with id: %s", self.id, id)
        return True

    def getEntities(self):
        entities = []

        for entity in self._storage:
            res = {
                "entity_id": self._storage[entity].id,
                "entity_type": self._storage[entity].entityType,
                "device_id": self._storage[entity].deviceId,
                "features": self._storage[entity].features,
                "name": self._storage[entity].name,
                "area": self._storage[entity].area,
                "device_class": self._storage[entity].deviceClass,
            }

            entities.append(res)

        return entities

    async def getStates(self):
        entities = []

        for entity in self._storage:
            res = {
                "entity_id": self._storage[entity].id,
                "entity_type": self._storage[entity].entityType,
                "device_id": self._storage[entity].deviceId,
                "attributes": self._storage[entity].attributes,
            }

            entities.append(res)

        return entities

    def clear(self):
        self._storage = {}
