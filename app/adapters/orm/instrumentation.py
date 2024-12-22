"""Instrumentation."""

from sqlalchemy import orm

from app.domain.models.entity import Entity


def instrument_entity():
    """Instruments an Entity base class."""

    @orm.reconstructor
    def entity_init_on_load(self):
        """Initializes events after loading entity from db."""
        self.events = []

    Entity.init_on_load = entity_init_on_load
