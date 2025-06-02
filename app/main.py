import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, flash, redirect, url_for, Response
import taglib
import logging
from app.services.file_manager import FileManager
from app.services.playlist_manager import PlaylistManager
from app.services.script_manager import ScriptManager
from app.config import settings

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "supersecretkey"

# Directories from config
DOWNLOAD_DIR = settings.download_dir
MUSIC_LIB_DIR = settings.music_lib_dir
PLAYLIST_DIR = settings.playlist_dir

def scan_music_library():
    """Scan MusicLib directory for songs and extract metadata, limiting to 3 songs."""
    songs = []
    music_path = Path(MUSIC_LIB_DIR)
    mp3_files = music_path.rglob("*.mp3")
    for mp3_file in list(mp3_files)[:3]:  # Limit to first 3 songs
        try:
            with taglib.File(mp3_file) as file:
                title = file.tags.get("TITLE", [mp3_file.stem])[0]
                artist = file.tags.get("ARTIST", ["AAAnonymus"])[0]
                album = file.tags.get("ALBUM", ["Singles"])[0]
            songs.append({
                "title": title,
                "artist": artist.replace("_", "/"),
                "album": album,
                "path_to_song": str(mp3_file)
            })
        except Exception as e:
            logging.error(f"Error scanning {mp3_file}: {e}")
    logging.info(f"Scanned {len(songs)} songs for preview")
    return songs

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        playlist_name = request.form.get("playlist_name")
        use_download_folder = request.form.get("use_download_folder") == "on"
        keep_download_files = request.form.get("keep_download_files") == "on"
        
        if not playlist_name:
            flash("Please provide a playlist name.", "error")
            logging.error("No playlist name provided")
            return redirect(url_for("index"))
        
        if not use_download_folder and not url:
            flash("Please provide a playlist URL or select use download folder.", "error")
            logging.error("No playlist URL provided and use_download_folder not selected")
            return redirect(url_for("index"))
        
        try:
            songs = []
            if not use_download_folder:
                logging.info("Starting download process")
                # Download songs
                script_manager = ScriptManager()
                for line in script_manager.run_spotdl(url, DOWNLOAD_DIR):
                    print(line)
                    logging.info(line)
            
            logging.info("Organizing songs")
            # Organize songs
            file_manager = FileManager(MUSIC_LIB_DIR, DOWNLOAD_DIR)
            songs = file_manager.add_to_library(DOWNLOAD_DIR, keep_download_files=keep_download_files)
            
            if not songs:
                flash("No songs were found to organize.", "error")
                logging.error("No songs found in download folder")
                return redirect(url_for("index"))
            
            logging.info(f"Creating playlist: {playlist_name}")
            # Create XML playlist
            playlist_manager = PlaylistManager(MUSIC_LIB_DIR, PLAYLIST_DIR)
            playlist_manager.create_playlist_xml(songs, playlist_name)
            
            flash(f"Playlist '{playlist_name}.xml' created successfully!", "success")
            logging.info(f"Playlist '{playlist_name}.xml' created successfully")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            logging.error(f"Error in POST handler: {e}")
        
        return redirect(url_for("index"))
    
    songs = scan_music_library()
    return render_template("index.html", songs=songs)

@app.route("/download-progress")
def download_progress():
    url = request.args.get("url")
    def generate():
        if not url:
            yield "data: Error: No URL provided\n\n"
            return
        try:
            script_manager = ScriptManager()
            for line in script_manager.run_spotdl(url, DOWNLOAD_DIR):
                yield f"data: {line}\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
    
    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(MUSIC_LIB_DIR, exist_ok=True)
    os.makedirs(PLAYLIST_DIR, exist_ok=True)
    app.run(debug=True)