from pathlib import Path
import taglib
import shutil
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class FileManager:
    def __init__(self, music_lib_dir: str, download_dir: str):
        self.music_lib_dir = music_lib_dir
        self.download_dir = download_dir

    def sanitize_filename(self, name: str, replacement: str = "_") -> str:
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, replacement)
        return name.strip().rstrip(".")

    def add_to_library(self, initial_folder: str) -> list:
        songs = list(Path(initial_folder).glob("*.mp3"))
        logging.info(f"Found {len(songs)} files")
        song_list = []

        for song in songs:
            try:
                with taglib.File(song) as file:
                    title = file.tags.get("TITLE", [song.stem])[0]
                    artist = file.tags.get("ARTIST", ["AAAnonymus"])[0]
                    album = file.tags.get("ALBUM", ["Singles"])[0]
                    year = file.tags.get("DATE", ["2024"])[0]
                    track_number = file.tags.get("TRACKNUMBER", ["1"])[0].split("/")[0]
                    duration = file.length * 1000  # Convert seconds to milliseconds
                    bitrate = file.bitrate or 128
                    sample_rate = file.sampleRate or 48000

                # Clean artist name for folder (use _), keep original for metadata
                artist_folder = self.sanitize_filename(artist) if artist != "AAAnonymus" else "AAAnonymus"
                album_folder = self.sanitize_filename(album) if album != "Singles" else "Singles"
                artist_path = Path(self.music_lib_dir) / artist_folder
                album_path = artist_path / album_folder
                destination = album_path / song.name

                # Check for duplicates
                if destination.exists():
                    logging.info(f"Skipping duplicate: {title} by {artist}")
                    continue

                # Create directories and move file
                album_path.mkdir(parents=True, exist_ok=True)
                shutil.move(song, destination)

                # Collect song metadata
                song_data = {
                    "title": title,
                    "artist": artist.replace("_", "/"),
                    "album": album,
                    "path_to_song": str(destination),
                    "year": year,
                    "track_number": track_number,
                    "duration": int(duration),
                    "bitrate": bitrate,
                    "sample_rate": sample_rate,
                    "size": destination.stat().st_size
                }
                song_list.append(song_data)
                logging.info(f"Processed song: {title} by {artist}")
            except Exception as e:
                logging.error(f"Error processing {song}: {e}")
                default_path = Path(self.music_lib_dir) / "AAAnonymus" / "Singles" / song.name
                default_path.parent.mkdir(parents=True, exist_ok=True)
                if not default_path.exists():
                    shutil.move(song, default_path)
                    song_data = {
                        "title": song.stem,
                        "artist": "AAAnonymus",
                        "album": "Singles",
                        "path_to_song": str(default_path),
                        "year": "2024",
                        "track_number": "1",
                        "duration": 0,
                        "bitrate": 128,
                        "sample_rate": 48000,
                        "size": default_path.stat().st_size
                    }
                    song_list.append(song_data)
                    logging.info(f"Processed song in default folder: {song.stem}")
                else:
                    logging.info(f"Skipping duplicate: {song.stem} in AAAnonymus/Singles")

        # Clean the download folder
        for item in Path(initial_folder).glob("*"):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
        logging.info("Cleaned download folder")

        return song_list