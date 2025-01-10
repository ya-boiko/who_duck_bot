"""Store image vector."""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import TypeAlias, Optional

from .entity import Entity


VectorType: TypeAlias = list[float]


@dataclass
class StoreImageVector(Entity):
    """Store image vector model."""

    id: uuid.UUID
    vector: VectorType

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        super().__init__()

    def __eq__(self, o: object) -> bool:
        return isinstance(o, StoreImageVector) and self.id == o.id

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def create(cls, vector: VectorType, **kwargs) -> 'StoreImageVector':
        """Creates the class object."""
        return StoreImageVector(
            id=kwargs.get('id', uuid.uuid4()),
            vector=vector,
        )

    def update(self, changes: dict):
        """Updates the attributes."""
        for (field, value) in changes.items():
            setattr(self, field, value)

        return self
