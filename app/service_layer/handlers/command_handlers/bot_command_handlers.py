"""Yandex command handlers."""

import json
import tempfile
import uuid
from datetime import datetime, UTC

from dependency_injector.wiring import Provide, inject
from redis.asyncio import Redis

from app.domain import commands
from app.domain.models import StoreImage
from app.service_layer.message_bus import MessageBus
from app.service_layer.unit_of_work import UnitOfWork


@inject
async def save_image(
    cmd: commands.SaveImage,
    uow: UnitOfWork,
    bus: MessageBus = Provide['bus']
) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        id = uuid.uuid4()
        cmd = commands.DownloadFileToDir(
            file_id=cmd.file_id,
            dir=temp_dir,
            filename=str(id),
        )
        temp_file_path = await bus.handle(cmd).pop()

        cmd = commands.GenerateDocumentDescription(file_path=temp_file_path)
        description = await bus.handle(cmd).pop()

        cmd = commands.UploadFile(file_path=temp_file_path)
        filename = await bus.handle(cmd).pop()

        generate_embeddings_cmd = commands.GenerateEmbedding(
            text=description,
        )
        vector = bus.handle(generate_embeddings_cmd).pop()

        filename_split = filename.split('/')
        with uow:
            store_image = StoreImage.create(
                id=id,
                filename=filename_split[-1],
                dir_path="/".join(filename_split[:-1]),
                description=description,
                vector=vector
            )

            uow.store_images.add(store_image)
            uow.commit()

        text = f'Изображение сохранено как {filename}.\n\n{description}'
        return text


@inject
async def start_dialog(
    cmd: commands.StartDialog,
    uow: UnitOfWork,
    redis_cli: Redis = Provide['redis_cli']
):
    val = await redis_cli.get(str(cmd.user_id))
    if not val:
        data = {
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": None,
            "version": 1,
        }
        await redis_cli.set(str(cmd.user_id), json.dumps(data))


@inject
async def finish_dialog(
    cmd: commands.FinishDialog,
    uow: UnitOfWork,
    redis_cli: Redis = Provide['redis_cli']
):
    await redis_cli.delete(str(cmd.user_id))
