"""Store image."""

import uuid
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, UTC

from .entity import Entity
from .store_image_vector import StoreImageVector, Vector


@dataclass
class StoreImage(Entity):
    """Store image model."""

    id: uuid.UUID
    filename: str
    dir: str
    vector_id: uuid.UUID
    description: str
    number_of_refs: int

    last_ref_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        super().__init__()

    def __eq__(self, o: object) -> bool:
        return isinstance(o, StoreImage) and self.id == o.id

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def create(cls, filename: str, dir_path: str, description: str, vector: Vector, **kwargs) -> 'StoreImage':
        """Creates the class object."""
        store_image_vector = StoreImageVector.create(
            vector=vector,
        )

        return StoreImage(
            id=kwargs.get('id', uuid.uuid4()),
            filename=filename,
            dir=dir_path,
            vector_id=store_image_vector.id,
            description=description,
            number_of_refs=kwargs.get('number_of_refs', 0),
            last_ref_at=kwargs.get('last_ref_at', None),
            created_at=kwargs.get('created_at', datetime.now(UTC)),
        )

    def update(self, changes: dict):
        """Updates the attributes."""
        for (field, value) in changes.items():
            setattr(self, field, value)

        return self
