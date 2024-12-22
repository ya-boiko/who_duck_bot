"""Default SqlAlchemy repository."""

import abc

from sqlalchemy.orm import Session

from app.service_layer.repositories import AbstractRepository


class SqlAlchemyRepository(AbstractRepository, abc.ABC):
    """Default SqlAlchemy repository."""

    session: Session
    model_type: type = None

    def __init__(self, session) -> None:
        super().__init__()
        self.session = session

    def _get(self, entity_id):
        return self.session.get(self.model_type, entity_id)

    def _add(self, entity) -> None:
        return self.session.add(entity)

    def delete(self, entity) -> None:
        return self.session.delete(entity)
