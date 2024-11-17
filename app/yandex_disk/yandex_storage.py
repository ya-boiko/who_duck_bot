"""Yandex storage."""

from typing import Optional
import asyncio

from yadisk import AsyncClient


class YandexStorage:
    """Yandex storage."""

    token: str
    main_dir: str
    app_dir: str

    _app_dir_exists: bool
    _full_path: str

    lock = asyncio.Lock()

    def __init__(self, token: str, main_dir: str, app_dir: str):
        self.token = token

        self._app_dir_exists = False

        self._set_main_dir(main_dir)
        self._set_app_dir(app_dir)

        self._full_path = self.main_dir + self.app_dir

    def client(self):
        return AsyncClient(
            token=self.token,
        )

    async def upload(self, file, filename: str) -> None:
        """Uploads file to the storage.

        :param file: file-like object to be uploaded;
        :param filename: name for the file to be uploaded.
        """
        async with self.client() as client:
            await self._create_app_dirs_if_not_exists(client)

            print(await client.check_token())
            await client.upload(file, self._full_path + '/' + filename, timeout=300)

    async def mkdir(self, dir_path: str, client: Optional[AsyncClient] = None) -> None:
        if client:
            await client.mkdir(dir_path)
            return

        async with self.client() as client:
            await client.mkdir(dir_path)

    async def ls(self, dir_path, client: Optional[AsyncClient] = None) -> list[str]:
        if client:
            return list([i.name async for i in client.listdir(dir_path)])

        async with self.client() as client:
            return list([i.name async for i in client.listdir(dir_path)])

    def _set_main_dir(self, value: str) -> None:
        value = value.strip()
        if not value.startswith('/'):
            value = '/' + value

        if not value.endswith('/'):
            value += '/'

        self.main_dir = value

    def _set_app_dir(self, value: str) -> None:
        value = value.strip()
        if value.startswith('/'):
            value = value[1:]

        self.app_dir = value

    async def _create_app_dirs_if_not_exists(self, client: AsyncClient) -> None:
        async with self.lock:
            if self._app_dir_exists:
                return

            app_dirs = self.app_dir.split('/')
            path = self.main_dir[:-1]
            for app_dir in [d for d in app_dirs if d]:
                if app_dir in await self.ls(path, client):
                    path += f'/{app_dir}'
                    continue

                path += f'/{app_dir}'
                await self.mkdir(path, client)
                print(f'Директория {path} создана.')

            self._app_dir_exists = True