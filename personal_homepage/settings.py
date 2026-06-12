from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "你的人生学无限"
    database_url: str = "sqlite:///./data/dev.db"
    media_root: Path = Path("./media")
    public_media_url: str = "/media"
    auto_seed: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
