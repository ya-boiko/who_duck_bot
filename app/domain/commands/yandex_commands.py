"""Yandex commands."""

from dataclasses import dataclass

from .command import Command


@dataclass
class UploadFile(Command):
    """Command for uploading file to Yandex storage."""

    file_path: str
