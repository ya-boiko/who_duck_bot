"""Table definitions."""

from datetime import datetime, UTC

from sqlalchemy import (
    DateTime,
    MetaData,
    Table,
    String,
    Integer,
    Column,
    ForeignKey,
    CheckConstraint,
    Boolean,
)
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector


UUID = String().with_variant(postgresql.UUID(as_uuid=True), 'postgresql')
metadata = MetaData()


store_images_table = Table(
    'store_images',
    metadata,
    Column('id', UUID, primary_key=True),
    Column('filename', String, nullable=False),
    Column('dir', String, nullable=False),
    Column('description', String, nullable=False),
    Column('vector_id', UUID, ForeignKey('store_image_vectors.id'), nullable=False),
    Column('number_of_refs', Integer, nullable=False, default=0),
    Column('last_ref_at', DateTime, nullable=True, default=None),

    Column('created_at', DateTime, nullable=False, default=lambda: datetime.now(UTC)),
    Column(
        'updated_at', DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    ),
)

store_image_vectors_table = Table(
    'store_image_vectors',
    metadata,
    Column('id', UUID, primary_key=True),
    Column('vector', Vector, nullable=False),
    Column('created_at', DateTime, nullable=False, default=lambda: datetime.now(UTC)),
    Column(
        'updated_at', DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    ),
)


# ticket_threads_table = Table(
#     'ticket_threads',
#     metadata,
#     Column('id', UUID, primary_key=True),
#     Column('ticket_id', UUID, ForeignKey('tickets.id'), nullable=False, index=True),
#     Column('sender_id', UUID, nullable=False),
#     Column('sender_type', String, nullable=False),
#     Column('body', String, nullable=False),
#     Column('created_at', DateTime, nullable=False, default=lambda: datetime.now(UTC)),
#     Column(
#         'updated_at', DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
#     ),
#
#     # constraints
#     CheckConstraint("sender_type IN ('support', 'customer')"),
# )
#
#
# support_messages_table = Table(
#     'support_messages',
#     metadata,
#     Column('id', UUID, primary_key=True),
#     Column('query_vector', Vector, nullable=False),
#     Column('query', String, nullable=False),
#     Column('message', String, nullable=False),
#     Column('created_at', DateTime, nullable=False, default=lambda: datetime.now(UTC)),
#     Column(
#         'updated_at', DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
#     ),
# )
#
#
# ai_models_table = Table(
#     'ai_models',
#     metadata,
#     Column('key', String, primary_key=True),
#     Column('name', String, nullable=False),
#     Column('type', String, nullable=False),
#
#     # constraints
#     CheckConstraint("type IN ('openai')"),
# )
#
#
# prompts_table = Table(
#     'prompts',
#     metadata,
#     Column('id', UUID, primary_key=True),
#     Column('ai_model_key', String, ForeignKey('ai_models.key'), nullable=False),
#     Column('title', String, nullable=False),
#     Column('system_body', String, nullable=False),
#     Column('user_body', String, nullable=False),
#     Column('is_default', Boolean, nullable=False, default=False),
#     Column('is_active', Boolean, nullable=False, default=True),
#     Column('created_at', DateTime, nullable=False, default=lambda: datetime.now(UTC)),
#     Column(
#         'updated_at', DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
#     ),
# )
#
#
# variables_table = Table(
#     'variables',
#     metadata,
#     Column('key', String, primary_key=True),
#     Column('title', String, nullable=False),
#     Column('description', String, nullable=False),
# )
#
#
# ticket_prompts_table = Table(
#     'ticket_prompts',
#     metadata,
#     Column('id', UUID, primary_key=True),
#     Column('ticket_id', UUID, ForeignKey('tickets.id'), nullable=False),
#     Column('system_body', String, nullable=False),
#     Column('user_body', String, nullable=False),
# )
#
#
# thread_variable_values_table = Table(
#     'thread_variable_values',
#     metadata,
#     Column('thread_id', UUID, ForeignKey('ticket_threads.id'), primary_key=True),
#     Column('key', String, primary_key=True),
#     Column('value', String, nullable=False),
# )
