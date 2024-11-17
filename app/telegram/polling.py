"""Telegram."""

import tempfile

from aiogram import Bot, Dispatcher, html, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dependency_injector.wiring import Provide, inject

from app.domain import commands
from app.service_layer.message_bus import MessageBus


@inject
async def tg_polling(
    dp: Dispatcher = Provide['dp'],
    bot: Bot = Provide['bot'],
    bus: MessageBus = Provide['bus'],
):

    @dp.message(CommandStart())
    async def command_start_handler(message: Message) -> None:
        """The handler receives messages with `/start` command."""
        await message.answer(f'Hello, {html.bold(message.from_user.full_name)}!')


    @dp.message(F.document)
    async def save_document(message: Message):
        with tempfile.TemporaryDirectory() as temp_dir:
            cmd = commands.DownloadFileToDir(
                file_id=message.document.file_id,
                dir=temp_dir
            )
            temp_file_path = await bus.handle(cmd).pop()

            with open(temp_file_path, 'rb') as temp_file:
                cmd = commands.UploadFile(
                    file_path=temp_file_path,
                )
                filename = await bus.handle(cmd).pop()

            await message.reply(f'Изображение сохранено как {filename}')

    await dp.start_polling(bot)
