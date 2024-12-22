"""AI commands."""

from dataclasses import dataclass

from .command import Command


@dataclass
class GenerateEmbedding(Command):
    """Command for generating an embedding."""

    text: str
