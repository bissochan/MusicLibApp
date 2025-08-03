import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from app.config import settings

class SettingsManager:
    def __init__(self, config_file: str = "app_config.json"):
        self.config_file = Path(config_file)
        self.settings = settings
        
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all current settings as a dictionary."""
        return {
            "app_mode": self.settings.app_mode,
            "debug_mode": self.settings.debug_mode,
            "root_folder": self.settings.root_folder,
            "download_dir": self.settings.download_dir,
            "playlist_dir": self.settings.playlist_dir,
            "music_lib_dir": self.settings.music_lib_dir,
            "max_download_retries": self.settings.max_download_retries,
            "download_timeout": self.settings.download_timeout,
            "keep_download_files": self.settings.keep_download_files,
            "auto_organize": self.settings.auto_organize,
            "duplicate_check": self.settings.duplicate_check,
            "create_artist_folders": self.settings.create_artist_folders,
            "create_album_folders": self.settings.create_album_folders,
            "auto_cleanup_after_playlist": self.settings.auto_cleanup_after_playlist,
            "playlist_format": self.settings.playlist_format,
            "show_download_options": self.settings.show_download_options,
            "show_progress_bar": self.settings.show_progress_bar,
            "enable_dark_mode": self.settings.enable_dark_mode,
            "max_search_results": self.settings.max_search_results,
            "log_level": self.settings.log_level,
            "log_file": self.settings.log_file,
            "enable_console_logging": self.settings.enable_console_logging,
            "max_concurrent_downloads": self.settings.max_concurrent_downloads,
            "cache_metadata": self.settings.cache_metadata,
            "metadata_cache_size": self.settings.metadata_cache_size
        }
    
    def get_editable_settings(self) -> Dict[str, Any]:
        """Get settings that can be edited from the frontend."""
        return {
            "app_mode": {
                "value": self.settings.app_mode,
                "type": "select",
                "options": ["debug", "deployed"],
                "description": "Application mode (debug shows more options)"
            },
            "root_folder": {
                "value": self.settings.root_folder,
                "type": "text",
                "description": "Root application folder"
            },
            "max_download_retries": {
                "value": self.settings.max_download_retries,
                "type": "number",
                "min": 1,
                "max": 10,
                "description": "Maximum download retry attempts"
            },
            "download_timeout": {
                "value": self.settings.download_timeout,
                "type": "number",
                "min": 60,
                "max": 1800,
                "description": "Download timeout in seconds"
            },
            "keep_download_files": {
                "value": self.settings.keep_download_files,
                "type": "boolean",
                "description": "Keep downloaded files after processing"
            },
            "auto_organize": {
                "value": self.settings.auto_organize,
                "type": "boolean",
                "description": "Automatically organize songs into folders"
            },
            "duplicate_check": {
                "value": self.settings.duplicate_check,
                "type": "boolean",
                "description": "Check for duplicate songs"
            },
            "create_artist_folders": {
                "value": self.settings.create_artist_folders,
                "type": "boolean",
                "description": "Create artist folders in library"
            },
            "create_album_folders": {
                "value": self.settings.create_album_folders,
                "type": "boolean",
                "description": "Create album folders in library"
            },
            "auto_cleanup_after_playlist": {
                "value": self.settings.auto_cleanup_after_playlist,
                "type": "boolean",
                "description": "Automatically clean download folder after playlist creation"
            },
            "playlist_format": {
                "value": self.settings.playlist_format,
                "type": "select",
                "options": ["xml", "m3u"],
                "description": "Playlist file format"
            },
            "show_progress_bar": {
                "value": self.settings.show_progress_bar,
                "type": "boolean",
                "description": "Show download progress bar"
            },
            "enable_dark_mode": {
                "value": self.settings.enable_dark_mode,
                "type": "boolean",
                "description": "Enable dark mode support"
            },
            "max_search_results": {
                "value": self.settings.max_search_results,
                "type": "number",
                "min": 10,
                "max": 200,
                "description": "Maximum search results to display"
            },
            "log_level": {
                "value": self.settings.log_level,
                "type": "select",
                "options": ["DEBUG", "INFO", "WARNING", "ERROR"],
                "description": "Logging level"
            },
            "enable_console_logging": {
                "value": self.settings.enable_console_logging,
                "type": "boolean",
                "description": "Enable console logging"
            },
            "max_concurrent_downloads": {
                "value": self.settings.max_concurrent_downloads,
                "type": "number",
                "min": 1,
                "max": 10,
                "description": "Maximum concurrent downloads"
            },
            "cache_metadata": {
                "value": self.settings.cache_metadata,
                "type": "boolean",
                "description": "Cache song metadata for better performance"
            },
            "metadata_cache_size": {
                "value": self.settings.metadata_cache_size,
                "type": "number",
                "min": 100,
                "max": 10000,
                "description": "Maximum metadata cache size"
            }
        }
    
    def update_setting(self, key: str, value: Any) -> bool:
        """Update a single setting."""
        try:
            if hasattr(self.settings, key):
                # Type conversion based on setting type
                current_value = getattr(self.settings, key)
                if isinstance(current_value, bool):
                    value = bool(value)
                elif isinstance(current_value, int):
                    value = int(value)
                elif isinstance(current_value, float):
                    value = float(value)
                
                setattr(self.settings, key, value)
                
                # Update derived settings
                if key == "app_mode":
                    self.settings.debug_mode = value == "debug"
                    self.settings.show_download_options = value == "debug"
                
                logging.info(f"Updated setting {key} to {value}")
                return True
            else:
                logging.error(f"Setting {key} not found")
                return False
        except Exception as e:
            logging.error(f"Error updating setting {key}: {e}")
            return False
    
    def update_multiple_settings(self, settings_dict: Dict[str, Any]) -> Dict[str, bool]:
        """Update multiple settings at once."""
        results = {}
        for key, value in settings_dict.items():
            results[key] = self.update_setting(key, value)
        return results
    
    def save_to_file(self) -> bool:
        """Save current settings to file."""
        try:
            settings_data = self.get_all_settings()
            with open(self.config_file, 'w') as f:
                json.dump(settings_data, f, indent=2)
            logging.info(f"Settings saved to {self.config_file}")
            return True
        except Exception as e:
            logging.error(f"Error saving settings: {e}")
            return False
    
    def load_from_file(self) -> bool:
        """Load settings from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    settings_data = json.load(f)
                
                for key, value in settings_data.items():
                    if hasattr(self.settings, key):
                        setattr(self.settings, key, value)
                
                # Update derived settings
                self.settings.debug_mode = self.settings.app_mode == "debug"
                self.settings.show_download_options = self.settings.app_mode == "debug"
                
                logging.info(f"Settings loaded from {self.config_file}")
                return True
            else:
                logging.info(f"Config file {self.config_file} not found, using defaults")
                return False
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to default values."""
        try:
            # Create new settings instance to get defaults
            from app.config import Settings
            default_settings = Settings()
            
            for key in self.get_all_settings().keys():
                if hasattr(default_settings, key):
                    setattr(self.settings, key, getattr(default_settings, key))
            
            logging.info("Settings reset to defaults")
            return True
        except Exception as e:
            logging.error(f"Error resetting settings: {e}")
            return False 