"""Telegram."""

import asyncio
import logging
import os
import sys
import tempfile

from aiogram import Bot, Dispatcher, html, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dependency_injector.wiring import Provide, inject

from app.yandex_disk.yandex_storage import YandexStorage


@inject
async def tg_polling(
    dp: Dispatcher = Provide['dp'],
    bot: Bot = Provide['bot'],
    yandex_storage: YandexStorage = Provide['yandex_storage'],
):

    @dp.message(CommandStart())
    async def command_start_handler(message: Message) -> None:
        """The handler receives messages with `/start` command."""
        await message.answer(f'Hello, {html.bold(message.from_user.full_name)}!')


    @dp.message(F.document)
    async def save_document(message: Message):
        file_id = message.document.file_id

        file = await bot.get_file(file_id)
        filepath = file.file_path
        filename = filepath.split('/')[-1]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, filename)
            await bot.download_file(filepath, temp_file_path)

            print(f'Файл сохранен во временную директорию: {temp_file_path}')

            with open(temp_file_path, 'rb') as temp_file:
                await yandex_storage.upload(temp_file, filename)

            await message.reply(f'Изображение сохранено как {filename}')

    await dp.start_polling(bot)
