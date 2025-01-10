"""AI commands."""

from dataclasses import dataclass

from .command import Command


@dataclass
class GenerateEmbedding(Command):
    """Command for generating an embedding."""

    text: str


@dataclass
class GenerateDocumentDescription(Command):
    """Command for generating document description."""

    file_path: str


@dataclass
class GenerateAnswer(Command):
    """Command for generating an answer for the message."""

    user_id: int
    message: str


@dataclass
class GenerateWhiningAnswer(Command):
    """Command for generating a whining answer for the message."""

    user_id: int
    message: str


@dataclass
class FindCloseImages(Command):
    """Command for finding closer images for the description."""

    user_id: int
    description: str
    limit: int
