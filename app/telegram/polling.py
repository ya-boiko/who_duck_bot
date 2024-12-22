"""Telegram."""

from aiogram import Bot, Dispatcher, html, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dependency_injector.wiring import Provide, inject

from app.adapters.orm import bind_mappers
from app.domain import commands
from app.service_layer.message_bus import MessageBus
from app.settings import Settings


bind_mappers()


@inject
async def tg_polling(
    dp: Dispatcher = Provide['dp'],
    bot: Bot = Provide['bot'],
    bus: MessageBus = Provide['bus'],
    settings: Settings = Provide['settings'],
):

    def message_from_admin(message: Message):
        return str(message.from_user.id) in settings.app.admins

    @dp.message(CommandStart())
    async def command_start_handler(message: Message) -> None:
        """The handler receives messages with `/start` command."""
        await message.answer(f'Hello, {html.bold(message.from_user.full_name)}!')

    @dp.message(F.document)
    async def save_document(message: Message):
        if not message_from_admin(message):
            return None

        cmd = commands.SaveImage(
            file_id=message.document.file_id
        )
        text = await bus.handle(cmd).pop()

        await message.reply(text)

    await dp.start_polling(bot)
