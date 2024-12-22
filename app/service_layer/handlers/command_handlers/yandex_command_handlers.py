"""Yandex command handlers."""

from pathlib import Path

from dependency_injector.wiring import Provide, inject

from app.domain.commands import UploadFile
from app.service_layer.unit_of_work import UnitOfWork
from app.yandex_disk import YandexStorage


@inject
async def upload_file(
    cmd: UploadFile,
    uow: UnitOfWork,
    yandex_storage: YandexStorage = Provide['yandex_storage'],
) -> str:
    file_path = Path(cmd.file_path)
    with open(file_path, 'rb') as f:
        filename = file_path.name
        await yandex_storage.upload(f, filename)

        return f'{yandex_storage.app_dir}/{filename}'
