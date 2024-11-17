"""Container."""

from sqlalchemy import create_engine, orm
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dependency_injector import containers, providers

from app.adapters.unit_of_work import UnitOfWork
from app.service_layer.handlers import mapping
from app.service_layer.message_bus import MessageBus
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

    # database
    database_engine = providers.Singleton(
        create_engine,
        config.database.url,
        echo=True,
        pool_recycle=3600,
        pool_pre_ping=True,
    )
    session_factory = providers.Factory(
        orm.sessionmaker,
        autocommit=False,
        autoflush=False,
        bind=database_engine,
        expire_on_commit=False,
    )
    uow = providers.Factory(UnitOfWork, session_factory)

    # bus
    event_handlers = providers.Object(mapping.EVENT_HANDLERS)
    command_handlers = providers.Object(mapping.COMMAND_HANDLERS)
    bus = providers.Singleton(MessageBus, uow, event_handlers, command_handlers)
