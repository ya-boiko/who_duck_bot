"""Settings."""

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils import get_env_file_path


class ApplicationSettings(BaseModel):
    """Application settings."""

    admins: str = ''


class DatabaseSettings(BaseModel):
    """Database settings."""

    url: str = ''
    db: str = ''
    user: str = ''
    password: str = ''


class OpenAISettings(BaseModel):
    """OpenAI settings."""

    api_secret_key: str = ''
    embedding_model: str = ''
    embedding_dimensions: int = 1536


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
    database: DatabaseSettings = DatabaseSettings()
    yandex_disk: YandexDiskSettings = YandexDiskSettings()
    tg: TelegramSettings = TelegramSettings()
    openai: OpenAISettings = OpenAISettings()

