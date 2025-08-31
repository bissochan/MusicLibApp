import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, flash, redirect, url_for, Response, jsonify
import taglib
import logging
from app.services.file_manager import FileManager
from app.services.playlist_manager import PlaylistManager
from app.services.script_manager import ScriptManager
from app.services.settings_manager import SettingsManager
from app.config import settings
import shutil

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "supersecretkey"

# Initialize settings manager
settings_manager = SettingsManager()

def get_directories():
    """Get current directory paths from config (for dynamic updates)."""
    return {
        'download_dir': settings.download_dir,
        'music_lib_dir': settings.music_lib_dir,
        'playlist_dir': settings.playlist_dir
    }

def search_library(query: str):
    """Search for songs in the library by title, artist, or album."""
    results = []
    query_lower = query.lower().strip()
    
    if not query_lower:
        return results
    
    try:
        # Get current music library directory from config
        current_music_lib_dir = settings.music_lib_dir
        music_path = Path(current_music_lib_dir)
        if not music_path.exists():
            logging.warning(f"Music library directory does not exist: {current_music_lib_dir}")
            return results
            
        logging.info(f"Searching for '{query}' in library: {current_music_lib_dir}")
        
        for mp3_file in music_path.rglob("*.mp3"):
            try:
                with taglib.File(str(mp3_file)) as file:
                    title = file.tags.get("TITLE", [mp3_file.stem])[0]
                    artist = file.tags.get("ARTIST", ["AAAnonymus"])[0]
                    album = file.tags.get("ALBUM", ["Singles"])[0]
                    
                    # Check if query matches title, artist, or album (partial matching)
                    title_lower = title.lower()
                    artist_lower = artist.lower()
                    album_lower = album.lower()
                    
                    if (query_lower in title_lower or 
                        query_lower in artist_lower or 
                        query_lower in album_lower):
                        
                        logging.debug(f"Match found: '{query_lower}' in '{title}' by '{artist}' from '{album}'")
                        results.append({
                            "title": title,
                            "artist": artist.replace("_", "/"),
                            "album": album,
                            "path": str(mp3_file),
                            "found": True
                        })
            except Exception as e:
                logging.warning(f"Failed to read metadata from {mp3_file}: {e}")
                # Fallback: check filename
                filename_lower = mp3_file.stem.lower()
                if query_lower in filename_lower:
                    logging.debug(f"Match found by filename: '{query_lower}' in '{mp3_file.stem}'")
                    results.append({
                        "title": mp3_file.stem,
                        "artist": "Unknown",
                        "album": "Unknown",
                        "path": str(mp3_file),
                        "found": True
                    })
                continue
                
    except Exception as e:
        logging.error(f"Error searching library: {e}")
    
    logging.info(f"Search completed. Found {len(results)} results for query: '{query}'")
    return results

def get_existing_playlists():
    """Get list of existing playlists."""
    # Get current playlist directory from config
    current_playlist_dir = settings.playlist_dir
    playlist_manager = PlaylistManager(settings.music_lib_dir, current_playlist_dir)
    return playlist_manager.get_existing_playlists()

def cleanup_download_folder():
    """Clean up the download folder by removing all MP3 files and empty directories."""
    try:
        # Get current download directory from config
        current_download_dir = settings.download_dir
        download_path = Path(current_download_dir)
        if not download_path.exists():
            logging.info("Download folder does not exist, nothing to clean")
            return
        
        # Remove all MP3 files
        mp3_files = list(download_path.glob("*.mp3"))
        for mp3_file in mp3_files:
            try:
                mp3_file.unlink()
                logging.info(f"Deleted file: {mp3_file}")
            except Exception as e:
                logging.error(f"Failed to delete {mp3_file}: {e}")
        
        # Remove empty directories
        for item in download_path.rglob("*"):
            if item.is_dir() and not any(item.iterdir()):
                try:
                    shutil.rmtree(item, ignore_errors=True)
                    logging.info(f"Deleted empty directory: {item}")
                except Exception as e:
                    logging.error(f"Failed to delete directory {item}: {e}")
        
        logging.info("Download folder cleanup completed")
    except Exception as e:
        logging.error(f"Error during download folder cleanup: {e}")

def find_song_in_library(title: str, artist: str, album: str) -> Path:
    """Find a song in the music library based on title, artist, and album."""
    try:
        # Get current music library directory from config
        current_music_lib_dir = settings.music_lib_dir
        
        # Sanitize folder names
        artist_folder = sanitize_filename(artist) if artist != "AAAnonymus" else "AAAnonymus"
        album_folder = sanitize_filename(album) if album != "Singles" else "Singles"
        
        # Construct the expected library path
        library_path = Path(current_music_lib_dir) / artist_folder / album_folder
        
        if not library_path.exists():
            logging.info(f"Library path does not exist: {library_path}")
            return None
        
        # Look for the song file
        title_lower = title.lower().strip()
        for mp3_file in library_path.glob("*.mp3"):
            try:
                with taglib.File(str(mp3_file)) as file:
                    existing_title = file.tags.get("TITLE", [mp3_file.stem])[0].lower().strip()
                    if title_lower == existing_title:
                        logging.info(f"Found song in library: {mp3_file}")
                        return mp3_file
            except Exception as e:
                logging.warning(f"Failed to read metadata from {mp3_file}: {e}")
                # Fallback: check filename
                if title_lower == mp3_file.stem.lower().strip():
                    logging.info(f"Found song in library by filename: {mp3_file}")
                    return mp3_file
                continue
        
        logging.warning(f"Could not find song '{title}' by '{artist}' in library path: {library_path}")
        return None
    except Exception as e:
        logging.error(f"Error finding song in library: {e}")
        return None

def sanitize_filename(name: str, replacement: str = "_") -> str:
    """Sanitize filename by replacing invalid characters."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, replacement)
    return name.strip().rstrip(".")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        playlist_name = request.form.get("playlist_name")
        use_download_folder = request.form.get("use_download_folder") == "on"
        keep_download_files = request.form.get("keep_download_files") == "on"
        add_to_existing_playlist = request.form.get("add_to_existing_playlist") == "on"
        existing_playlist_name = request.form.get("existing_playlist_name")
        
        if not playlist_name and not add_to_existing_playlist:
            flash("Please provide a playlist name or select an existing playlist.", "error")
            logging.error("No playlist name provided and not adding to existing playlist")
            return redirect(url_for("index"))
        
        if add_to_existing_playlist and not existing_playlist_name:
            flash("Please select an existing playlist to add songs to.", "error")
            logging.error("No existing playlist selected")
            return redirect(url_for("index"))
        
        # If no URL is provided, automatically use download folder
        if not url and not use_download_folder:
            use_download_folder = True
            logging.info("No URL provided, automatically using download folder")
        
        try:
            songs = []
            if not use_download_folder:
                logging.info("Starting download process")
                # Download songs - run spotdl only once
                script_manager = ScriptManager()
                # Get current download directory from config
                current_download_dir = settings.download_dir
                spotdl_generator = script_manager.run_spotdl(url, current_download_dir)
                for line in spotdl_generator:
                    
                    logging.info(line)
            
            logging.info("Organizing songs")
            # Organize songs
            # Get current directories from config
            current_music_lib_dir = settings.music_lib_dir
            current_download_dir = settings.download_dir
            file_manager = FileManager(current_music_lib_dir, current_download_dir)
            
            # For existing playlists, we want to keep the files even if they're duplicates
            # so we can still add them to the playlist
            if add_to_existing_playlist:
                keep_files_for_playlist = True
            else:
                keep_files_for_playlist = keep_download_files
                
            songs = file_manager.add_to_library(current_download_dir, keep_download_files=keep_files_for_playlist)
            
            # Handle playlist creation or addition
            current_playlist_dir = settings.playlist_dir
            playlist_manager = PlaylistManager(current_music_lib_dir, current_playlist_dir)
            
            if add_to_existing_playlist:
                # For existing playlists, we want to add songs even if they're duplicates in the library
                # because they might not be in the playlist yet
                if not songs:
                    # If no songs were added to library (all duplicates), try to get them from download folder
                    download_songs = list(Path(current_download_dir).glob("*.mp3"))
                    logging.info(f"Found {len(download_songs)} files in download folder to process for playlist")
                    if download_songs:
                        # Create song objects from download folder for playlist addition
                        songs = []
                        for song_file in download_songs:
                            try:
                                with taglib.File(str(song_file)) as file:
                                    title = file.tags.get("TITLE", [song_file.stem])[0]
                                    artist = file.tags.get("ARTIST", ["AAAnonymus"])[0]
                                    album = file.tags.get("ALBUM", ["Singles"])[0]
                                    year = file.tags.get("DATE", ["2024"])[0]
                                    track_number = file.tags.get("TRACKNUMBER", ["1"])[0].split("/")[0]
                                    duration = file.length * 1000 if hasattr(file, 'length') else 0
                                    bitrate = 128 if not hasattr(file, 'bitrate') or file.bitrate is None else file.bitrate
                                    sample_rate = 48000 if not hasattr(file, 'sample_rate') or file.sample_rate is None else file.sample_rate
                                    size = song_file.stat().st_size
                                    
                                    # Find the corresponding song in the library
                                    library_path = find_song_in_library(title, artist, album)
                                    if library_path:
                                        song_data = {
                                            "title": title,
                                            "artist": artist.replace("_", "/"),
                                            "album": album,
                                            "path_to_song": str(library_path),
                                            "year": year,
                                            "track_number": track_number,
                                            "duration": int(duration),
                                            "bitrate": bitrate,
                                            "sample_rate": sample_rate,
                                            "size": size
                                        }
                                        songs.append(song_data)
                                        logging.info(f"Added song to playlist processing: {title} by {artist} (library path: {library_path})")
                                    else:
                                        logging.warning(f"Could not find {title} by {artist} in library, skipping playlist addition")
                            except Exception as e:
                                logging.warning(f"Failed to read metadata from {song_file}: {e}")
                                continue
                
                if songs:
                    # Add songs to existing playlist
                    result = playlist_manager.add_songs_to_existing_playlist(songs, existing_playlist_name)
                    flash(result['message'], "success")
                    logging.info(f"Added songs to existing playlist: {result['message']}")
                    
                    # Clean up download folder after successful playlist addition
                    cleanup_download_folder()
                else:
                    flash("No songs were found to add to the playlist.", "warning")
                    logging.warning("No songs found to add to playlist")
            else:
                # For new playlists, we want to create a playlist with the downloaded songs
                # even if they're duplicates in the library
                if not songs:
                    # If no songs were added to library (all duplicates), try to get them from download folder
                    download_songs = list(Path(current_download_dir).glob("*.mp3"))
                    logging.info(f"Found {len(download_songs)} files in download folder to process for new playlist")
                    if download_songs:
                        # Create song objects from download folder for playlist creation
                        songs = []
                        for song_file in download_songs:
                            try:
                                with taglib.File(str(song_file)) as file:
                                    title = file.tags.get("TITLE", [song_file.stem])[0]
                                    artist = file.tags.get("ARTIST", ["AAAnonymus"])[0]
                                    album = file.tags.get("ALBUM", ["Singles"])[0]
                                    year = file.tags.get("DATE", ["2024"])[0]
                                    track_number = file.tags.get("TRACKNUMBER", ["1"])[0].split("/")[0]
                                    duration = file.length * 1000 if hasattr(file, 'length') else 0
                                    bitrate = 128 if not hasattr(file, 'bitrate') or file.bitrate is None else file.bitrate
                                    sample_rate = 48000 if not hasattr(file, 'sample_rate') or file.sample_rate is None else file.sample_rate
                                    size = song_file.stat().st_size
                                    
                                    # Find the corresponding song in the library
                                    library_path = find_song_in_library(title, artist, album)
                                    if library_path:
                                        song_data = {
                                            "title": title,
                                            "artist": artist.replace("_", "/"),
                                            "album": album,
                                            "path_to_song": str(library_path),
                                            "year": year,
                                            "track_number": track_number,
                                            "duration": int(duration),
                                            "bitrate": bitrate,
                                            "sample_rate": sample_rate,
                                            "size": size
                                        }
                                        songs.append(song_data)
                                        logging.info(f"Added song to new playlist processing: {title} by {artist} (library path: {library_path})")
                                    else:
                                        logging.warning(f"Could not find {title} by {artist} in library, skipping playlist creation")
                            except Exception as e:
                                logging.warning(f"Failed to read metadata from {song_file}: {e}")
                                continue
                
                if songs:
                    # Create new playlist
                    playlist_manager.create_playlist_xml(songs, playlist_name)
                    flash(f"Playlist '{playlist_name}.xml' created successfully!", "success")
                    logging.info(f"Playlist '{playlist_name}.xml' created successfully")
                    
                    # Clean up download folder after successful playlist creation
                    cleanup_download_folder()
                else:
                    flash("No songs were found to create the playlist.", "warning")
                    logging.warning("No songs found to create playlist")
            
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            logging.error(f"Error in POST handler: {e}")
        
        return redirect(url_for("index"))
    
    existing_playlists = get_existing_playlists()
    return render_template("index.html", existing_playlists=existing_playlists, app_mode=settings.app_mode, show_download_options=settings.show_download_options)

@app.route("/download-progress")
def download_progress():
    url = request.args.get("url")
    def generate():
        if not url:
            yield "data: Error: No URL provided\n\n"
            return
        try:
            script_manager = ScriptManager()
            # Get current download directory from config
            current_download_dir = settings.download_dir
            for line in script_manager.run_spotdl(url, current_download_dir):
                yield f"data: {line}\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
    
    return Response(generate(), mimetype="text/event-stream")

@app.route("/api/search")
def api_search():
    """API endpoint to search for songs in the library."""
    query = request.args.get("q", "").strip()
    
    if not query:
        return jsonify({"error": "No search query provided"}), 400
    
    try:
        results = search_library(query)
        
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })
    except Exception as e:
        logging.error(f"Search error: {e}")
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

@app.route("/api/playlists")
def api_playlists():
    """API endpoint to get existing playlists."""
    try:
        playlists = get_existing_playlists()
        return jsonify(playlists)
    except Exception as e:
        logging.error(f"Error getting playlists: {e}")
        return jsonify({"error": f"Failed to get playlists: {str(e)}"}), 500

@app.route("/api/playlists/refresh", methods=["POST"])
def api_refresh_playlists():
    """API endpoint to refresh playlists after operations."""
    try:
        playlists = get_existing_playlists()
        return jsonify({
            "success": True,
            "playlists": playlists,
            "message": "Playlists refreshed successfully"
        })
    except Exception as e:
        logging.error(f"Error refreshing playlists: {e}")
        return jsonify({"error": f"Failed to refresh playlists: {str(e)}"}), 500

@app.route("/api/playlists/<playlist_name>")
def api_get_playlist_details(playlist_name):
    """API endpoint to get details of a specific playlist."""
    try:
        # Get current directories from config
        current_music_lib_dir = settings.music_lib_dir
        current_playlist_dir = settings.playlist_dir
        playlist_manager = PlaylistManager(current_music_lib_dir, current_playlist_dir)
        playlist_path = Path(current_playlist_dir) / f"{playlist_name}.xml"
        
        if not playlist_path.exists():
            return jsonify({"error": f"Playlist '{playlist_name}' not found"}), 404
        
        songs = playlist_manager.read_playlist_songs(str(playlist_path))
        playlist_info = {
            "name": playlist_name,
            "path": str(playlist_path),
            "size": playlist_path.stat().st_size,
            "song_count": len(songs),
            "songs": songs
        }
        
        return jsonify(playlist_info)
    except Exception as e:
        logging.error(f"Error getting playlist details for {playlist_name}: {e}")
        return jsonify({"error": f"Failed to get playlist details: {str(e)}"}), 500

@app.route("/settings")
def settings_page():
    """Settings page route."""
    editable_settings = settings_manager.get_editable_settings()
    return render_template("settings.html", settings=editable_settings, app_mode=settings.app_mode)

@app.route("/api/settings", methods=["GET"])
def api_get_settings():
    """API endpoint to get current settings."""
    editable_settings = settings_manager.get_editable_settings()
    return jsonify(editable_settings)

@app.route("/api/settings", methods=["POST"])
def api_update_settings():
    """API endpoint to update settings."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        results = settings_manager.update_multiple_settings(data)
        success = all(results.values())
        
        if success:
            # Save settings to file
            settings_manager.save_to_file()
            flash("Settings updated successfully!", "success")
            return jsonify({"message": "Settings updated successfully", "results": results})
        else:
            failed_settings = [key for key, success in results.items() if not success]
            flash(f"Failed to update some settings: {', '.join(failed_settings)}", "error")
            return jsonify({"error": "Some settings failed to update", "results": results}), 400
            
    except Exception as e:
        logging.error(f"Error updating settings: {e}")
        flash(f"Error updating settings: {str(e)}", "error")
        return jsonify({"error": str(e)}), 500

@app.route("/api/settings/reset", methods=["POST"])
def api_reset_settings():
    """API endpoint to reset settings to defaults."""
    try:
        success = settings_manager.reset_to_defaults()
        if success:
            settings_manager.save_to_file()
            flash("Settings reset to defaults!", "success")
            return jsonify({"message": "Settings reset to defaults"})
        else:
            flash("Failed to reset settings", "error")
            return jsonify({"error": "Failed to reset settings"}), 500
    except Exception as e:
        logging.error(f"Error resetting settings: {e}")
        flash(f"Error resetting settings: {str(e)}", "error")
        return jsonify({"error": str(e)}), 500

@app.route("/api/paths")
def api_get_paths():
    """API endpoint to get current resolved paths for debugging."""
    try:
        # Get current directories from config
        current_download_dir = settings.download_dir
        current_playlist_dir = settings.playlist_dir
        current_music_lib_dir = settings.music_lib_dir
        
        paths = {
            "root_folder": settings.root_folder,
            "download_dir": current_download_dir,
            "playlist_dir": current_playlist_dir,
            "music_lib_dir": current_music_lib_dir,
            "resolved": {
                "download_dir": str(Path(current_download_dir).resolve()),
                "playlist_dir": str(Path(current_playlist_dir).resolve()),
                "music_lib_dir": str(Path(current_music_lib_dir).resolve())
            }
        }
        return jsonify(paths)
    except Exception as e:
        logging.error(f"Error getting paths: {e}")
        return jsonify({"error": f"Failed to get paths: {str(e)}"}), 500

if __name__ == "__main__":
    # Get current directories from config
    current_download_dir = settings.download_dir
    current_music_lib_dir = settings.music_lib_dir
    current_playlist_dir = settings.playlist_dir
    
    os.makedirs(current_download_dir, exist_ok=True)
    os.makedirs(current_music_lib_dir, exist_ok=True)
    os.makedirs(current_playlist_dir, exist_ok=True)
    app.run(debug=True)