from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    download_dir: str
    playlist_dir: str
    music_lib_dir: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()