"""Entity model."""

from app.domain import Event


class Entity:
    """Entity."""

    events: list[Event]

    def __init__(self) -> None:
        self.events = []
