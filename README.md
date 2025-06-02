# Music Library Manager

A Flask-based web app to organize MP3 files and create iTunes-compatible XML playlists. Download songs from playlist URLs (via `spotdl`), structure them by artist/album, include duplicates in playlists without re-adding, and preview up to three songs.

## Features
- Organizes MP3s into `MusicLib/artist/album/`.
- Includes duplicates in playlists using existing library paths.
- Creates XML playlists with metadata (title, artist, album, etc.).
- Web interface for downloading or processing files, with options to keep downloads.
- Previews three songs for fast loading.
- Cross-platform (Windows, macOS, Linux).

## Prerequisites
- Python 3.8+
- FFmpeg (for `spotdl`):
  - Ubuntu: `sudo apt-get install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org), add to PATH.
- Git

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/music-library-manager.git
   cd music-library-manager
   python install.py