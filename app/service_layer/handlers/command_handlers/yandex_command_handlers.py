"""Yandex command handlers."""

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
    with open(cmd.file_path, 'rb') as f:
        filename = cmd.file_path.split('/')[-1]
        await yandex_storage.upload(f, filename)

        return filename
