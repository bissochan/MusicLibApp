from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional
import os

class Settings(BaseSettings):
    # App Configuration
    app_mode: str = "deployed"  # "debug" or "deployed"
    debug_mode: bool = True
    
    # Directory Configuration
    root_folder: str = ""
    download_dir: str
    playlist_dir: str
    music_lib_dir: str
    
    # Download Configuration
    max_download_retries: int = 3
    download_timeout: int = 300  # seconds
    keep_download_files: bool = False
    
    # Library Configuration
    auto_organize: bool = True
    duplicate_check: bool = True
    create_artist_folders: bool = True
    create_album_folders: bool = True
    
    # Playlist Configuration
    auto_cleanup_after_playlist: bool = True
    playlist_format: str = "xml"  # "xml" or "m3u"
    
    # UI Configuration
    show_download_options: bool = True
    show_progress_bar: bool = True
    enable_dark_mode: bool = True
    max_search_results: int = 50
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None
    enable_console_logging: bool = True
    
    # Performance Configuration
    max_concurrent_downloads: int = 3
    cache_metadata: bool = True
    metadata_cache_size: int = 1000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set debug_mode based on app_mode
        self.debug_mode = self.app_mode == "debug"
        # Set show_download_options based on app_mode
        self.show_download_options = self.app_mode == "debug"
        
        # Set root_folder if not provided
        if not self.root_folder:
            self.root_folder = str(Path.cwd())

settings = Settings()