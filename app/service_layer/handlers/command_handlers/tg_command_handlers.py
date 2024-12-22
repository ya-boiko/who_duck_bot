"""Yandex command handlers."""

import os
import uuid
from pathlib import Path

from dependency_injector.wiring import Provide, inject
from aiogram import Bot
from PIL import Image
from pillow_heif import register_heif_opener

from app.domain.commands import DownloadFileToDir
from app.service_layer.unit_of_work import UnitOfWork


register_heif_opener()


def convert_single_file(heic_path, jpg_path, output_quality) -> tuple:
    """
    Convert a single HEIC file to JPG format.

    #### Args:
        - heic_path (str): Path to the HEIC file.
        - jpg_path (str): Path to save the converted JPG file.
        - output_quality (int): Quality of the output JPG image.

    #### Returns:
        - tuple: Path to the HEIC file and conversion status.
    """
    with Image.open(heic_path) as image:
        image.save(jpg_path, "JPEG", quality=output_quality)
    return heic_path, True  # Successful conversion


@inject
async def download_file_to_dir(cmd: DownloadFileToDir, uow: UnitOfWork, bot: Bot = Provide['bot']) -> str:
    file = await bot.get_file(cmd.file_id)
    file_path = Path(file.file_path)

    filename = file_path.name.replace(file_path.stem, cmd.filename)
    local_file_path = os.path.join(cmd.dir, filename)

    await bot.download_file(file.file_path, local_file_path)

    if filename.lower().endswith('.heic'):

        filename_split = filename.split('.')
        filename_split[-1] = 'jpg'
        jpg_filename = '.'.join(filename_split)
        jpg_path = os.path.join(cmd.dir, jpg_filename)

        convert_single_file(local_file_path, jpg_path, output_quality=100)

        local_file_path = jpg_path

    print(f'Файл сохранен во директорию: {local_file_path}')

    return local_file_path
