"""Telegram commands."""

from dataclasses import dataclass

from .command import Command


@dataclass
class DownloadFileToDir(Command):
    """Command for downloading file from tg chat to local directory."""

    file_id: str
    dir: str
    filename: str
