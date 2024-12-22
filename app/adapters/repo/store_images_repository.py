"""Store image repository."""

from app.adapters.repo import SqlAlchemyRepository
from app.service_layer.repositories import StoreImageRepository
from app.domain import models


class SqlAlchemyStoreImageRepository(SqlAlchemyRepository, StoreImageRepository):
    """Sqlalchemy store image repository."""

    model_type = models.StoreImage
