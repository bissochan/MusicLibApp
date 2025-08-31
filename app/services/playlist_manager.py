from pathlib import Path
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz
import logging
import os

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

    def get_existing_playlists(self):
        """Get list of existing playlists."""
        playlists = []
        try:
            for file in Path(self.playlist_dir).glob("*.xml"):
                playlists.append({
                    'name': file.stem,
                    'path': str(file),
                    'size': file.stat().st_size
                })
            logging.info(f"Found {len(playlists)} existing playlists")
        except Exception as e:
            logging.error(f"Failed to get existing playlists: {e}")
        return playlists

    def read_playlist_songs(self, playlist_path: str):
        """Read songs from an existing playlist XML file."""
        songs = []
        try:
            tree = ET.parse(playlist_path)
            root = tree.getroot()
            
            # Find tracks section
            tracks_dict = None
            for i, elem in enumerate(root.iter()):
                if elem.tag == "key" and elem.text == "Tracks":
                    # Get the next element which should be the tracks dict
                    if i + 1 < len(list(root.iter())):
                        tracks_dict = list(root.iter())[i + 1]
                        if tracks_dict.tag == "dict":
                            break
            
            if tracks_dict is None:
                logging.warning(f"No tracks section found in {playlist_path}")
                return songs
            
            # Extract song information from tracks
            current_key = None
            song_info = {}
            
            for elem in tracks_dict:
                if elem.tag == "key":
                    if song_info and current_key:  # Save previous song
                        converted_song = self._convert_song_info(song_info)
                        if converted_song:
                            songs.append(converted_song)
                        song_info = {}
                    current_key = elem.text
                elif elem.tag in ["string", "integer", "date"] and current_key:
                    song_info[current_key] = elem.text
            
            # Don't forget the last song
            if song_info and current_key:
                converted_song = self._convert_song_info(song_info)
                if converted_song:
                    songs.append(converted_song)
            
            logging.info(f"Read {len(songs)} songs from playlist {playlist_path}")
        except Exception as e:
            logging.error(f"Failed to read playlist {playlist_path}: {e}")
        
        return songs

    def _convert_song_info(self, song_info: dict):
        """Convert song info from XML format to standard format."""
        try:
            return {
                "title": song_info.get("Name", "Unknown Title"),
                "artist": song_info.get("Artist", "AAAnonymus"),
                "album": song_info.get("Album", "Singles"),
                "path_to_song": song_info.get("Location", "").replace("file://localhost/", "").replace("file:///", ""),
                "year": song_info.get("Year", "2024"),
                "track_number": song_info.get("Track Number", "1"),
                "duration": int(song_info.get("Total Time", 0)),
                "bitrate": int(song_info.get("Bit Rate", 128)),
                "sample_rate": int(song_info.get("Sample Rate", 48000)),
                "size": int(song_info.get("Size", 0))
            }
        except Exception as e:
            logging.warning(f"Failed to convert song info: {e}")
            return None

    def is_song_duplicate(self, new_song: dict, existing_songs: list):
        """Check if a song is a duplicate based on title, artist, and album."""
        new_title = new_song.get("title", "").lower().strip()
        new_artist = new_song.get("artist", "").lower().strip()
        new_album = new_song.get("album", "").lower().strip()
        
        for existing_song in existing_songs:
            existing_title = existing_song.get("title", "").lower().strip()
            existing_artist = existing_song.get("artist", "").lower().strip()
            existing_album = existing_song.get("album", "").lower().strip()
            
            # Check if title, artist, and album match
            if (new_title == existing_title and 
                new_artist == existing_artist and 
                new_album == existing_album):
                return True
        
        return False

    def add_songs_to_existing_playlist(self, songs: list, playlist_name: str):
        """Add songs to an existing playlist, checking for duplicates."""
        playlist_path = Path(self.playlist_dir) / f"{playlist_name}.xml"
        
        if not playlist_path.exists():
            logging.error(f"Playlist {playlist_name} does not exist")
            raise FileNotFoundError(f"Playlist {playlist_name} not found")
        
        try:
            # Read existing playlist
            existing_songs = self.read_playlist_songs(str(playlist_path))
            logging.info(f"Found {len(existing_songs)} existing songs in playlist {playlist_name}")
            
            # Filter out duplicates
            new_songs = []
            duplicates_found = 0
            
            for song in songs:
                if self.is_song_duplicate(song, existing_songs):
                    logging.info(f"Duplicate found: {song.get('title', 'Unknown')} by {song.get('artist', 'Unknown')}")
                    duplicates_found += 1
                else:
                    new_songs.append(song)
            
            if not new_songs:
                logging.info(f"No new songs to add to playlist {playlist_name} (all were duplicates)")
                return {
                    'success': True,
                    'message': f"No new songs added to '{playlist_name}' (all {len(songs)} songs were duplicates)",
                    'added': 0,
                    'duplicates': len(songs)
                }
            
            # Update the existing playlist by adding new songs
            self.update_playlist_with_new_songs(playlist_path, existing_songs, new_songs, playlist_name)
            
            total_songs = len(existing_songs) + len(new_songs)
            logging.info(f"Added {len(new_songs)} new songs to playlist {playlist_name}")
            return {
                'success': True,
                'message': f"Added {len(new_songs)} new songs to '{playlist_name}' ({duplicates_found} duplicates skipped). Total songs: {total_songs}",
                'added': len(new_songs),
                'duplicates': duplicates_found,
                'total_songs': total_songs
            }
            
        except Exception as e:
            logging.error(f"Failed to add songs to playlist {playlist_name}: {e}")
            raise

    def update_playlist_with_new_songs(self, playlist_path: Path, existing_songs: list, new_songs: list, playlist_name: str):
        """Update an existing playlist by adding new songs without recreating the entire structure."""
        try:
            # Parse the existing XML
            tree = ET.parse(playlist_path)
            root = tree.getroot()
            
            # Find the tracks section
            tracks_dict = None
            for i, elem in enumerate(root.iter()):
                if elem.tag == "key" and elem.text == "Tracks":
                    if i + 1 < len(list(root.iter())):
                        tracks_dict = list(root.iter())[i + 1]
                        if tracks_dict.tag == "dict":
                            break
            
            if tracks_dict is None:
                logging.error("No tracks section found in existing playlist")
                raise ValueError("Invalid playlist format")
            
            # Find the playlists section
            playlists_array = None
            for i, elem in enumerate(root.iter()):
                if elem.tag == "key" and elem.text == "Playlists":
                    if i + 1 < len(list(root.iter())):
                        playlists_array = list(root.iter())[i + 1]
                        if playlists_array.tag == "array":
                            break
            
            if playlists_array is None:
                logging.error("No playlists section found in existing playlist")
                raise ValueError("Invalid playlist format")
            
            # Get the first playlist dict (assuming single playlist)
            playlist_dict = None
            for elem in playlists_array:
                if elem.tag == "dict":
                    playlist_dict = elem
                    break
            
            if playlist_dict is None:
                logging.error("No playlist dict found")
                raise ValueError("Invalid playlist format")
            
            # Find the playlist items array
            items_array = None
            for i, elem in enumerate(playlist_dict):
                if elem.tag == "key" and elem.text == "Playlist Items":
                    if i + 1 < len(list(playlist_dict)):
                        items_array = list(playlist_dict)[i + 1]
                        if items_array.tag == "array":
                            break
            
            if items_array is None:
                logging.error("No playlist items array found")
                raise ValueError("Invalid playlist format")
            
            # Get the next available track ID
            existing_track_ids = []
            for elem in tracks_dict:
                if elem.tag == "key":
                    try:
                        existing_track_ids.append(int(elem.text))
                    except ValueError:
                        continue
            
            next_track_id = max(existing_track_ids) + 1 if existing_track_ids else 100
            
            # Add new songs to tracks section
            for song in new_songs:
                # Add track entry
                track_key = ET.SubElement(tracks_dict, "key")
                track_key.text = str(next_track_id)
                track_dict = ET.SubElement(tracks_dict, "dict")
                self._add_track_metadata(track_dict, song, next_track_id)
                
                # Add playlist item
                item_dict = ET.SubElement(items_array, "dict")
                self._add_key_value(item_dict, "Track ID", "integer", str(next_track_id))
                
                next_track_id += 1
            
            # Write the updated XML
            with open(playlist_path, "wb") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf-8'))
                f.write('<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'.encode('utf-8'))
                tree.write(f, encoding="utf-8")
            
            logging.info(f"Updated playlist {playlist_name} with {len(new_songs)} new songs")
            
        except Exception as e:
            logging.error(f"Failed to update playlist {playlist_path}: {e}")
            raise

    def create_playlist_xml(self, songs: list, playlist_name: str, is_update: bool = False):
        try:
            playlist_name = self.sanitize_filename(playlist_name or str(uuid.uuid4()))
            playlist_path = Path(self.playlist_dir) / f"{playlist_name}.xml"
            
            if is_update:
                logging.info(f"Updating playlist: {playlist_path}")
            else:
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
            
            # Use the actual music library directory from settings instead of hardcoded path
            music_folder_uri = Path(self.music_lib_dir).as_uri().replace("file:///", "file://localhost/")
            self._add_key_value(root_dict, "Music Folder", "string", music_folder_uri)
            
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
            
            if is_update:
                logging.info(f"Updated playlist '{playlist_name}.xml' at {self.playlist_dir}")
            else:
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