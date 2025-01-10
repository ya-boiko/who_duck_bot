"""Telegram."""
import tempfile

from aiogram import Bot, Dispatcher, html, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InputMediaPhoto
from dependency_injector.wiring import Provide, inject
from aiogram.utils.media_group import MediaGroupBuilder


from app.domain import commands
from app.service_layer.message_bus import MessageBus
from app.settings import Settings


@inject
async def tg_polling(
    dp: Dispatcher = Provide['dp'],
    bot: Bot = Provide['bot'],
    bus: MessageBus = Provide['bus'],
    settings: Settings = Provide['settings'],
):

    def gen_channel_id(val: int) -> int:
        return int(f'-100{val}') if not str(val).startswith('-100') else val

    def is_admin_message(message: Message):
        return str(message.from_user.id) in settings.app.admins

    @dp.message(CommandStart())
    async def command_start_handler(message: Message):
        """Handler for the `/start` command."""
        if not is_admin_message(message):
            await message.answer(f'i don`t know who you are, sorry, buy')
            return

        await message.answer(f'Hello, {html.bold(message.from_user.full_name)}!')

    @dp.message(Command("start_dialog"))
    async def start_dialog_command(message: Message):
        """Handler for the `/start_dialog` command."""
        if not is_admin_message(message):
            return None

        cmd = commands.StartDialog(
            user_id=message.from_user.id
        )
        await bus.handle(cmd).pop()


    @dp.message(Command("finish_dialog"))
    async def finish_dialog_command(message: Message):
        """Handler for the `/finish_dialog` command."""
        if not is_admin_message(message):
            return None

        cmd = commands.FinishDialog(
            user_id=message.from_user.id
        )
        await bus.handle(cmd).pop()

    @dp.message(F.document)
    async def save_document(message: Message):
        if not is_admin_message(message):
            return None

        cmd = commands.SaveImage(
            file_id=message.document.file_id
        )
        text = await bus.handle(cmd).pop()

        await message.reply(text)

    @dp.message()
    async def get_message(message: Message):
        if not is_admin_message(message):
            return None

        cmd = commands.GenerateAnswer(
            user_id=message.from_user.id,
            message = message.text
        )
        answer = await bus.handle(cmd).pop()

        send_massage_kwargs = {
            'chat_id': message.chat.id,
        }
        if 'text' in answer:
            send_massage_kwargs.update({
                'text': answer['text']
            })
        if 'media' in answer:
            # cat = FSInputFile(answer['media'][0].name)
            # ii = InputMediaPhoto(media=, caption="text")

            with tempfile.TemporaryDirectory() as temp_dir:
                cmd = commands.DownloadFile(filename=answer['media'][0].filename, dest_dir=temp_dir)
                answer = await bus.handle(cmd).pop()

            send_massage_kwargs.update({
                'media': answer['media']
            })


        if 'text' or 'media' in send_massage_kwargs:
            await bot.send_message(**send_massage_kwargs)

        # await bot.send_message(
        #     chat_id=gen_channel_id(settings.app.channel),
        #     text=answer
        # )

    await dp.start_polling(bot)
