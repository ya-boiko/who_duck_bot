"""Unit of work."""

from app.service_layer.unit_of_work import SqlAlchemyUnitOfWork
from app.service_layer.unit_of_work import UnitOfWork as IUnitOfWork


class UnitOfWork(SqlAlchemyUnitOfWork, IUnitOfWork):
    """UoW."""

    def __init__(self, session_factory) -> None:
        super().__init__(session_factory)

    def _init_repositories(self, session) -> list[object]:
        return []
