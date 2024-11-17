"""Main script."""

import asyncio
import logging
import sys

from app.container import Container
from app.settings import Settings
from app.telegram import tg_polling


def create_app():
    """Creates the application."""
    container = Container()
    container.config.from_dict(Settings().model_dump())

    return tg_polling()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(create_app())
