from datetime import datetime
from typing import Union

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    name: str = 'My Raspberry'
    location: str = 'Home'
    host: str = '127.0.0.1'
    port: int = 8100
    updated_at: Union[datetime, None] = None

    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env',
        env_file_encoding='utf-8',
    )
