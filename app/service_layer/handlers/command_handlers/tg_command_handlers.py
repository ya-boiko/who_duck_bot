"""Yandex command handlers."""

import os

from dependency_injector.wiring import Provide, inject
from aiogram import Bot

from app.domain.commands import DownloadFileToDir
from app.service_layer.unit_of_work import UnitOfWork


@inject
async def download_file_to_dir(cmd: DownloadFileToDir, uow: UnitOfWork, bot: Bot = Provide['bot']) -> str:
    file = await bot.get_file(cmd.file_id)
    filename = file.file_path.split('/')[-1]
    local_file_path = os.path.join(cmd.dir, filename)

    await bot.download_file(file.file_path, local_file_path)

    print(f'Файл сохранен во временную директорию: {local_file_path}')

    return local_file_path
