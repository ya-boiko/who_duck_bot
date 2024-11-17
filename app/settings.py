"""Settings."""

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils import get_env_file_path


class ApplicationSettings(BaseModel):
    """Application settings."""

    ...


class YandexDiskSettings(BaseModel):
    """Yandex disk settings."""

    token: str = ''
    main_dir: str = ''
    app_dir: str = ''


class TelegramSettings(BaseModel):
    """Telegram settings."""

    token: str = ''


class Settings(BaseSettings):
    """Settings."""

    model_config = SettingsConfigDict(
        env_nested_delimiter='__',
        env_file=get_env_file_path('.env.dev.local')
    )

    app: ApplicationSettings = ApplicationSettings()
    yandex_disk: YandexDiskSettings = YandexDiskSettings()
    tg: TelegramSettings = TelegramSettings()
