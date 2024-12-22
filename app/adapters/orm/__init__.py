"""ORM."""

from sqlalchemy.orm import registry, relationship

from app.adapters.orm import tables, instrumentation
from app.domain import models


mapper_registry = registry()
metadata = tables.metadata

instrumentation.instrument_entity()


def bind_mappers():
    """Binds ORM mappers."""

    mapper_registry.map_imperatively(models.StoreImageVector, tables.store_image_vectors_table)

    mapper_registry.map_imperatively(
        models.StoreImage,
        tables.store_images_table,
        properties={
            'vector': relationship(
                models.StoreImageVector,
                lazy='immediate',
                cascade='all',
            ),
        }
    )

    # mapper_registry.map_imperatively(
    #     models.Prompt,
    #     tables.prompts_table,
    #     properties={
    #         'ai_model': relationship(
    #             models.AIModel,
    #             lazy='immediate',
    #             cascade='all',
    #         ),
    #     }
    # )
    #
    # mapper_registry.map_imperatively(
    #     models.TicketThread,
    #     tables.ticket_threads_table,
    #     properties={
    #         'variable_values': relationship(
    #             models.ThreadVariableValue,
    #             lazy='immediate',
    #             cascade='all, delete-orphan',
    #             uselist=True,
    #         ),
    #     }
    # )
    #
    # mapper_registry.map_imperatively(
    #     models.Ticket,
    #     tables.tickets_table,
    #     properties={
    #         'prompt': relationship(
    #             models.TicketPrompt,
    #             lazy='immediate',
    #             cascade='all',
    #         ),
    #         'threads': relationship(
    #             models.TicketThread,
    #             lazy='immediate',
    #             cascade='all, delete-orphan',
    #             uselist=True,
    #         ),
    #     }
    # )
