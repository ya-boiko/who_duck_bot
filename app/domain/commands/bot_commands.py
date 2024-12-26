"""Bot commands."""

from dataclasses import dataclass

from .command import Command


@dataclass
class SaveImage(Command):
    """Command for saving image to the store."""

    file_id: str


@dataclass
class StartDialog(Command):
    """Command for starting the dialog with user."""

    user_id: int


@dataclass
class FinishDialog(Command):
    """Command for finishing the dialog with user."""

    user_id: int
