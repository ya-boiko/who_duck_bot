"""Bot commands."""

from dataclasses import dataclass

from .command import Command


@dataclass
class SaveImage(Command):
    """Command for saving image to the store."""

    file_id: str
