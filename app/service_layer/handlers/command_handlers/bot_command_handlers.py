"""Yandex command handlers."""

import tempfile
import uuid

from dependency_injector.wiring import Provide, inject

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
