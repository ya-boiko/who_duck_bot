"""Container."""

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dependency_injector import containers, providers
from yadisk import AsyncClient

from app.yandex_disk.yandex_storage import YandexStorage


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""

    wiring_config = containers.WiringConfiguration(
        packages=['app'],
    )
    config = providers.Configuration()

    # yandex disk

    yandex_storage = providers.Factory(
        YandexStorage,
        token=config.yandex_disk.token,
        main_dir=config.yandex_disk.main_dir,
        app_dir=config.yandex_disk.app_dir,
    )

    # telegram

    dp = providers.Singleton(Dispatcher)
    bot = providers.Singleton(
        Bot,
        token=config.tg.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
