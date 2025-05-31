from pathlib import Path
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class PlaylistManager:
    def __init__(self, music_lib_dir: str, playlist_dir: str):
        self.music_lib_dir = music_lib_dir
        self.playlist_dir = playlist_dir
        try:
            Path(playlist_dir).mkdir(parents=True, exist_ok=True)
            logging.info(f"Playlist directory ensured: {playlist_dir}")
        except Exception as e:
            logging.error(f"Failed to create playlist directory {playlist_dir}: {e}")
            raise

    def create_playlist_xml(self, songs: list, playlist_name: str):
        try:
            playlist_name = self.sanitize_filename(playlist_name or str(uuid.uuid4()))
            playlist_path = Path(self.playlist_dir) / f"{playlist_name}.xml"
            logging.info(f"Creating playlist: {playlist_path}")

            # Create XML structure
            plist = ET.Element("plist")
            plist.set("version", "1.0")
            root_dict = ET.SubElement(plist, "dict")

            # Add library metadata
            self._add_key_value(root_dict, "Major Version", "integer", "1")
            self._add_key_value(root_dict, "Minor Version", "integer", "1")
            self._add_key_value(root_dict, "Date", "date", datetime.now(pytz.UTC).isoformat())
            self._add_key_value(root_dict, "Application Version", "string", "12.13.7.1")
            self._add_key_value(root_dict, "Features", "integer", "5")
            self._add_key_value(root_dict, "Show Content Ratings", "true")
            self._add_key_value(root_dict, "Music Folder", "string", "file://localhost/C:/Users/lucab/Music/MusicLib/")
            self._add_key_value(root_dict, "Library Persistent ID", "string", str(uuid.uuid4()).replace("-", "").upper()[:16])

            # Add Tracks section
            tracks_key = ET.SubElement(root_dict, "key")
            tracks_key.text = "Tracks"
            tracks_dict = ET.SubElement(root_dict, "dict")

            # Track IDs start from 100
            track_id_base = 100
            valid_songs = []
            for index, song in enumerate(songs):
                try:
                    track_id = track_id_base + index
                    track_key = ET.SubElement(tracks_dict, "key")
                    track_key.text = str(track_id)
                    track_dict = ET.SubElement(tracks_dict, "dict")
                    self._add_track_metadata(track_dict, song, track_id)
                    valid_songs.append((song, track_id))
                except Exception as e:
                    logging.error(f"Skipping track {song.get('title', 'unknown')} due to metadata error: {e}")

            if not valid_songs:
                logging.error("No valid songs to include in playlist")
                return

            # Add Playlists section
            playlists_key = ET.SubElement(root_dict, "key")
            playlists_key.text = "Playlists"
            playlists_array = ET.SubElement(root_dict, "array")
            playlist_dict = ET.SubElement(playlists_array, "dict")
            self._add_key_value(playlist_dict, "Name", "string", playlist_name)
            self._add_key_value(playlist_dict, "Description", "string", "")
            self._add_key_value(playlist_dict, "Playlist ID", "integer", str(track_id_base + len(songs) + 1))
            self._add_key_value(playlist_dict, "Playlist Persistent ID", "string", str(uuid.uuid4()).replace("-", "").upper()[:16])
            self._add_key_value(playlist_dict, "All Items", "true")
            items_key = ET.SubElement(playlist_dict, "key")
            items_key.text = "Playlist Items"
            items_array = ET.SubElement(playlist_dict, "array")
            for _, track_id in valid_songs:
                item_dict = ET.SubElement(items_array, "dict")
                self._add_key_value(item_dict, "Track ID", "integer", str(track_id))

            # Write XML with DOCTYPE
            tree = ET.ElementTree(plist)
            with open(playlist_path, "wb") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf-8'))
                f.write('<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'.encode('utf-8'))
                tree.write(f, encoding="utf-8")
            
            logging.info(f"XML Playlist '{playlist_name}.xml' created at {self.playlist_dir}")
        except Exception as e:
            logging.error(f"Failed to create playlist {playlist_path}: {e}")
            raise

    def _add_key_value(self, parent, key, value_type, value=None):
        key_elem = ET.SubElement(parent, "key")
        key_elem.text = key
        if value_type == "true":
            ET.SubElement(parent, "true")
        else:
            value_elem = ET.SubElement(parent, value_type)
            if value is not None:
                value_elem.text = str(value)

    def _add_track_metadata(self, track_dict, song, track_id):
        try:
            self._add_key_value(track_dict, "Track ID", "integer", track_id)
            self._add_key_value(track_dict, "Name", "string", song.get("title", "Unknown Title"))
            self._add_key_value(track_dict, "Artist", "string", song.get("artist", "AAAnonymus"))
            self._add_key_value(track_dict, "Album", "string", song.get("album", "Singles"))
            self._add_key_value(track_dict, "Kind", "string", "File audio MPEG")
            self._add_key_value(track_dict, "Size", "integer", song.get("size", 0))
            self._add_key_value(track_dict, "Total Time", "integer", song.get("duration", 0))
            self._add_key_value(track_dict, "Track Number", "integer", song.get("track_number", "1"))
            self._add_key_value(track_dict, "Year", "integer", song.get("year", "2024"))
            self._add_key_value(track_dict, "Date Modified", "date", datetime.now(pytz.UTC).isoformat())
            self._add_key_value(track_dict, "Date Added", "date", datetime.now(pytz.UTC).isoformat())
            self._add_key_value(track_dict, "Bit Rate", "integer", song.get("bitrate", 128))
            self._add_key_value(track_dict, "Sample Rate", "integer", song.get("sample_rate", 48000))
            self._add_key_value(track_dict, "Persistent ID", "string", str(uuid.uuid4()).replace("-", "").upper()[:16])
            self._add_key_value(track_dict, "Track Type", "string", "File")
            self._add_key_value(track_dict, "Location", "string", Path(song.get("path_to_song", "")).as_uri().replace("file:///", "file://localhost/"))
            self._add_key_value(track_dict, "File Folder Count", "integer", "-1")
            self._add_key_value(track_dict, "Library Folder Count", "integer", "-1")
        except Exception as e:
            logging.error(f"Failed to add track metadata for {song.get('title', 'unknown')}: {e}")
            raise

    def sanitize_filename(self, name: str, replacement: str = "_") -> str:
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, replacement)
        return name.strip().rstrip(".")