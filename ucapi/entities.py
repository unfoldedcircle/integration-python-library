"""
Entity store.

:copyright: (c) 2023 by Unfolded Circle ApS.
:license: MPL 2.0, see LICENSE for more details.
"""

import logging
from asyncio import AbstractEventLoop

from pyee import AsyncIOEventEmitter

from ucapi.api_definitions import EVENTS
from ucapi.entity import Entity

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class Entities:
    """Simple entity storage."""

    def __init__(self, identifier: str, loop: AbstractEventLoop):
        """
        Create entity storage instance with the given identifier.

        :param identifier: storage identifier.
        :param loop: event loop
        """
        self.id = identifier
        self._loop = loop
        self._storage = {}
        self.events = AsyncIOEventEmitter(self._loop)

    def contains(self, entity_id: str) -> bool:
        """Check if storage contains an entity with given identifier."""
        return entity_id in self._storage

    def getEntity(self, entity_id: str) -> Entity | None:
        """Retrieve entity with given identifier."""
        if entity_id not in self._storage:
            LOG.debug("ENTITIES(%s): Entity does not exists with id: %s", self.id, entity_id)
            return None

        return self._storage[entity_id]

    def addEntity(self, entity: Entity) -> bool:
        """Add entity to storage."""
        if entity.id in self._storage:
            LOG.debug("ENTITIES(%s): Entity already exists with id: %s", self.id, entity.id)
            return False

        self._storage[entity.id] = entity
        LOG.debug("ENTITIES(%s): Entity added with id: %s", self.id, entity.id)
        return True

    def removeEntity(self, entity_id: str) -> bool:
        """Remove entity from storage."""
        if entity_id not in self._storage:
            LOG.debug("ENTITIES(%s): Entity does not exists with id: %s", self.id, entity_id)
            return True

        del self._storage[entity_id]
        LOG.debug("ENTITIES(%s): Entity deleted with id: %s", self.id, entity_id)
        return True

    def updateEntityAttributes(self, entity_id: str, attributes: dict) -> bool:
        """Update entity attributes."""
        if entity_id not in self._storage:
            LOG.debug("ENTITIES(%s): Entity does not exists with id: %s", self.id, entity_id)
            # TODO why return True here?
            return True

        for key in attributes:
            self._storage[entity_id].attributes[key] = attributes[key]

        self.events.emit(
            EVENTS.ENTITY_ATTRIBUTES_UPDATED,
            entity_id,
            self._storage[entity_id].entityType,
            attributes,
        )

        LOG.debug("ENTITIES(%s): Entity attributes updated with id: %s", self.id, entity_id)
        return True

    def getEntities(self) -> list[dict[str, any]]:
        """
        Get all entity information in storage.

        Attributes are not returned.
        """
        entities = []

        for entity in self._storage.items():
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

    async def getStates(self) -> list[dict[str, any]]:
        """Get all entity information with entity_id, entity_type, device_id, attributes."""
        entities = []

        for entity in self._storage.items():
            res = {
                "entity_id": self._storage[entity].id,
                "entity_type": self._storage[entity].entityType,
                "device_id": self._storage[entity].deviceId,
                "attributes": self._storage[entity].attributes,
            }

            entities.append(res)

        return entities

    def clear(self):
        """Remove all entities from storage."""
        self._storage = {}
