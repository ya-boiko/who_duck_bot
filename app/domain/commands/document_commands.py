"""Document commands."""

from dataclasses import dataclass

from .command import Command


@dataclass
class GenerateDocumentDescription(Command):
    """Command for generating document description."""

    file_path: str
