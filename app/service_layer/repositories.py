"""Repositories."""

from abc import ABC, abstractmethod

from app.domain.models import Entity


class AbstractRepository(ABC):
    """Abstract repository."""

    seen: set

    def __init__(self) -> None:
        super().__init__()
        self.seen = set()

    def get(self, entity_id):
        """Returns the aggregate by ID."""
        entity = self._get(entity_id)
        if entity:
            self.seen.add(entity)
        return entity

    @abstractmethod
    def _get(self, entity_id) -> Entity:
        """Implement by returning the entity"""

    def add(self, entity: Entity) -> None:
        """Adds aggregate to the store."""
        self._add(entity)
        self.seen.add(entity)

    @abstractmethod
    def _add(self, entity: Entity) -> None:
        """Implement by adding the entity to the store."""

    @abstractmethod
    def delete(self, entity: Entity) -> None:
        """Deletes aggregate from the store."""


class StoreImageRepository(AbstractRepository):
    """Store image repository."""

    ...
