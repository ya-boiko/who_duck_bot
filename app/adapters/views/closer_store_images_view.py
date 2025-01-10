"""View for the support message responses."""

from sqlalchemy import select

from app.domain.models import StoreImage, StoreImageVector

from .base_database_view import BaseDatabaseView


class CloserStoreImagesView(BaseDatabaseView):
    """Closer store images view.

    Sorted by distance [asc].
    """

    def __call__(self, vector, limit: int = 5) -> list[(float, StoreImage)]:
        """Finds the list of store images by vector."""
        with (self._session_factory() as session):
            query = select(
                StoreImageVector.id,
                StoreImageVector.vector.cosine_distance(vector).label("distance")
            )

            scope = session.execute(query)
            result = {distance: store_image_id for store_image_id, distance in scope.all()}
            vector_ids = [str(val[1]) for val in sorted(result.items())]

            if limit > 0:
                vector_ids = vector_ids[:limit]

            query = select(
                StoreImage,
            ).filter(
                StoreImage.vector_id.in_(vector_ids)
            )
            result = session.execute(query).all()

            return result
