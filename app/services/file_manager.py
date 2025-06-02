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

    def truncate_filename(self, name: str, max_length: int = 100) -> str:
        """Truncate file name to max_length, preserving extension."""
        if len(name) <= max_length:
            return name
        base, ext = os.path.splitext(name)
        max_base_length = max_length - len(ext)
        truncated_base = base[:max_base_length]
        new_name = truncated_base + ext
        logging.info(f"Truncated file name from {name} to {new_name}")
        return new_name

    def add_to_library(self, initial_folder: str, keep_download_files: bool = False) -> list:
        songs = list(Path(initial_folder).glob("*.mp3"))
        logging.info(f"Found {len(songs)} files in {initial_folder}")
        song_list = []
        processed_files = set()  # Track files to delete if keep_download_files=False

        for song in songs:
            try:
                # Use \\?\ prefix for long paths
                song_path = str(song)
                if not song_path.startswith(r"\\?\\"):
                    song_path = r"\\?\\" + song_path

                # Truncate file name if too long
                song_name = self.truncate_filename(song.name)
                if song_name != song.name:
                    new_song_path = str(song.parent / song_name)
                    if not new_song_path.startswith(r"\\?\\"):
                        new_song_path = r"\\?\\" + new_song_path
                    try:
                        os.rename(song_path, new_song_path)
                        song_path = new_song_path
                    except Exception as e:
                        logging.error(f"Failed to rename {song.name} to {song_name}: {e}")
                        continue

                logging.info(f"Processing song: {song_name}")
                # Initialize metadata
                title = song.stem
                artist = "AAAnonymus"
                album = "Singles"
                year = "2024"
                track_number = "1"
                duration = 0
                bitrate = 128
                sample_rate = 48000
                size = 0

                artist_folder = self.sanitize_filename(artist) if artist != "AAAnonymus" else "AAAnonymus"
                album_folder = self.sanitize_filename(album) if album != "Singles" else "Singles"
                artist_path = Path(self.music_lib_dir) / artist_folder
                album_path = artist_path / album_folder
                destination = album_path / song_name

                destination_path = str(destination)
                if not destination_path.startswith(r"\\?\\"):
                    destination_path = r"\\?\\" + destination_path

                # Check if the song already exists in the library
                if os.path.exists(destination_path):
                    logging.info(f"Found existing song in library: {song_name}")
                    # Use the existing file in music_lib_dir for metadata
                    try:
                        with taglib.File(destination_path) as file:
                            title = file.tags.get("TITLE", [song.stem])[0]
                            artist = file.tags.get("ARTIST", ["AAAnonymus"])[0]
                            album = file.tags.get("ALBUM", ["Singles"])[0]
                            year = file.tags.get("DATE", ["2024"])[0]
                            track_number = file.tags.get("TRACKNUMBER", ["1"])[0].split("/")[0]
                            duration = file.length * 1000  # Convert seconds to milliseconds
                            bitrate = 128 if not hasattr(file, 'bitrate') or file.bitrate is None else file.bitrate
                            sample_rate = 48000 if not hasattr(file, 'sample_rate') or file.sample_rate is None else file.sample_rate
                            size = os.path.getsize(destination_path)
                    except Exception as e:
                        logging.warning(f"Failed to read metadata for existing {song_name}: {e}. Using default values")
                    # Add existing song metadata to song_list
                    song_data = {
                        "title": title,
                        "artist": artist.replace("_", "/"),
                        "album": album,
                        "path_to_song": str(destination),  # Use the library path
                        "year": year,
                        "track_number": track_number,
                        "duration": int(duration),
                        "bitrate": bitrate,
                        "sample_rate": sample_rate,
                        "size": size
                    }
                    song_list.append(song_data)
                    logging.info(f"Added existing song to playlist: {title} by {artist}")
                    processed_files.add(song_path)  # Mark for potential deletion
                    continue

                # If not a duplicate, proceed with metadata extraction and moving
                try:
                    with taglib.File(song_path) as file:
                        title = file.tags.get("TITLE", [song.stem])[0]
                        artist = file.tags.get("ARTIST", ["AAAnonymus"])[0]
                        album = file.tags.get("ALBUM", ["Singles"])[0]
                        year = file.tags.get("DATE", ["2024"])[0]
                        track_number = file.tags.get("TRACKNUMBER", ["1"])[0].split("/")[0]
                        duration = file.length * 1000  # Convert seconds to milliseconds
                        bitrate = 128 if not hasattr(file, 'bitrate') or file.bitrate is None else file.bitrate
                        sample_rate = 48000 if not hasattr(file, 'sample_rate') or file.sample_rate is None else file.sample_rate
                except Exception as e:
                    logging.warning(f"Failed to read metadata for {song_name}: {e}. Using default values")

                # Update artist and album folders based on metadata
                artist_folder = self.sanitize_filename(artist) if artist != "AAAnonymus" else "AAAnonymus"
                album_folder = self.sanitize_filename(album) if album != "Singles" else "Singles"
                artist_path = Path(self.music_lib_dir) / artist_folder
                album_path = artist_path / album_folder
                destination = album_path / song_name

                destination_path = str(destination)
                if not destination_path.startswith(r"\\?\\"):
                    destination_path = r"\\?\\" + destination_path

                try:
                    album_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    logging.error(f"Failed to create directory {album_path}: {e}")
                    continue

                try:
                    shutil.move(song_path, destination_path)
                    size = os.path.getsize(destination_path)
                except Exception as e:
                    logging.error(f"Failed to move {song_name} to {destination_path}: {e}")
                    continue

                song_data = {
                    "title": title,
                    "artist": artist.replace("_", "/"),
                    "album": album,
                    "path_to_song": str(destination),  # Clean path (no \\?\\)
                    "year": year,
                    "track_number": track_number,
                    "duration": int(duration),
                    "bitrate": bitrate,
                    "sample_rate": sample_rate,
                    "size": size
                }
                song_list.append(song_data)
                logging.info(f"Processed and moved song: {title} by {artist}")
                processed_files.add(song_path)  # Mark for potential deletion

            except Exception as e:
                logging.error(f"Unexpected error processing {song.name}: {e}")
                continue

        if not keep_download_files:
            try:
                for item in processed_files:
                    item_path = Path(item)
                    if item_path.is_file() and item_path.exists():
                        item_path.unlink()
                        logging.info(f"Deleted file: {item_path}")
                # Only delete empty directories
                for item in Path(initial_folder).glob("**/*"):
                    if item.is_dir() and not any(item.iterdir()):
                        shutil.rmtree(item, ignore_errors=True)
                        logging.info(f"Deleted empty directory: {item}")
                logging.info("Cleaned download folder of processed files")
            except Exception as e:
                logging.error(f"Failed to clean download folder {initial_folder}: {e}")

        return song_list