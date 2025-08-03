#!/usr/bin/env python3
"""
Create .env file with proper configuration
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file with proper configuration."""
    
    # Get the project root directory
    root_dir = Path(__file__).parent.absolute()
    
    # Define the paths
    download_dir = root_dir / "downloads"
    playlist_dir = root_dir / "playlists"
    music_lib_dir = root_dir / "music_library"
    
    # Create the .env content
    env_content = f"""# Music Library Manager Configuration

# App Configuration
APP_MODE=deployed
DEBUG_MODE=false

# Directory Configuration
ROOT_FOLDER={root_dir}
DOWNLOAD_DIR={download_dir}
PLAYLIST_DIR={playlist_dir}
MUSIC_LIB_DIR={music_lib_dir}

# Download Configuration
MAX_DOWNLOAD_RETRIES=3
DOWNLOAD_TIMEOUT=300
KEEP_DOWNLOAD_FILES=false

# Library Configuration
AUTO_ORGANIZE=true
DUPLICATE_CHECK=true
CREATE_ARTIST_FOLDERS=true
CREATE_ALBUM_FOLDERS=true

# Playlist Configuration
AUTO_CLEANUP_AFTER_PLAYLIST=true
PLAYLIST_FORMAT=xml

# UI Configuration
SHOW_DOWNLOAD_OPTIONS=false
SHOW_PROGRESS_BAR=true
ENABLE_DARK_MODE=true
MAX_SEARCH_RESULTS=50

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=
ENABLE_CONSOLE_LOGGING=true

# Performance Configuration
MAX_CONCURRENT_DOWNLOADS=3
CACHE_METADATA=true
METADATA_CACHE_SIZE=1000
"""
    
    # Write the .env file
    env_file = root_dir / ".env"
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"[SUCCESS] Created .env file at {env_file}")
    print(f"[INFO] Download directory: {download_dir}")
    print(f"[INFO] Playlist directory: {playlist_dir}")
    print(f"[INFO] Music library directory: {music_lib_dir}")
    
    # Create the directories if they don't exist
    for directory in [download_dir, playlist_dir, music_lib_dir]:
        directory.mkdir(exist_ok=True)
        print(f"[INFO] Created directory: {directory}")

if __name__ == "__main__":
    create_env_file() 