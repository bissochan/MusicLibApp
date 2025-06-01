# MusicLibApp

A Flask-based web application for managing music libraries and creating iTunes-compatible playlists.

## Features

- Download songs from supported platforms using spotdl
- Organize music files with metadata into a structured library
- Create iTunes-compatible XML playlists
- Web interface with dark/light theme support
- Search functionality for your music library
- Real-time download progress monitoring

## Requirements

- Python 3.x
- Flask
- SQLAlchemy
- PyTagLib
- Flask-SocketIO

## Installation

1. Clone this repository
2. Install requirements:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file with the following variables:
```
download_dir=path/to/download/directory
playlist_dir=path/to/playlist/directory
music_lib_dir=path/to/music/library
```

## Usage

1. Run the application:
```bash
python app/main.py
```
2. Open a web browser and navigate to `http://localhost:5000`
3. Enter a playlist URL or use existing files in the download folder
4. Provide a playlist name
5. Click "Process & Create" to generate your playlist

## License

[Add your chosen license here]