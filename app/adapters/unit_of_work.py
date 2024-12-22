"""Unit of work."""

from app.adapters import repo
from app.service_layer.unit_of_work import SqlAlchemyUnitOfWork
from app.service_layer.unit_of_work import UnitOfWork as IUnitOfWork
from app.service_layer.repositories import (
    StoreImageRepository,
)


class UnitOfWork(SqlAlchemyUnitOfWork, IUnitOfWork):
    """UoW."""

    store_images: StoreImageRepository = None

    def __init__(self, session_factory) -> None:
        super().__init__(session_factory)

    def _init_repositories(self, session) -> list[object]:
        self.store_images = repo.SqlAlchemyStoreImageRepository(session)

        return [
            self.store_images,
        ]
