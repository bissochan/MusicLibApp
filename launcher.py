#!/usr/bin/env python3
"""
Music Library Manager Launcher
Automatically sets up the environment and starts the application.
"""

import os
import sys
import subprocess
import time
import webbrowser
import platform
from pathlib import Path
import json

class MusicLibLauncher:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.venv_dir = self.root_dir / "venv"
        self.requirements_file = self.root_dir / "requirements.txt"
        self.app_dir = self.root_dir / "app"
        
        # OS-specific paths
        self.is_windows = platform.system() == "Windows"
        self.is_macos = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
        
        # Virtual environment paths
        if self.is_windows:
            self.venv_python = self.venv_dir / "Scripts" / "python.exe"
            self.venv_pip = self.venv_dir / "Scripts" / "pip.exe"
        else:
            self.venv_python = self.venv_dir / "bin" / "python"
            self.venv_pip = self.venv_dir / "bin" / "pip"
    
    def print_status(self, message, status="INFO"):
        """Print a formatted status message."""
        colors = {
            "INFO": "\033[94m",    # Blue
            "SUCCESS": "\033[92m", # Green
            "WARNING": "\033[93m", # Yellow
            "ERROR": "\033[91m",   # Red
            "RESET": "\033[0m"     # Reset
        }
        
        if self.is_windows:
            # Windows doesn't support ANSI colors by default, use plain text
            print(f"[{status}] {message}")
        else:
            print(f"{colors.get(status, '')}[{status}]{colors['RESET']} {message}")
    
    def check_python_version(self):
        """Check if Python version is compatible."""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.print_status("Python 3.8 or higher is required!", "ERROR")
            self.print_status(f"Current version: {version.major}.{version.minor}.{version.micro}", "ERROR")
            return False
        self.print_status(f"Python version: {version.major}.{version.minor}.{version.micro}", "SUCCESS")
        return True
    
    def create_env_file(self):
        """Create .env file if it doesn't exist."""
        env_file = self.root_dir / ".env"
        
        if env_file.exists():
            self.print_status(".env file already exists", "INFO")
            return True
        
        self.print_status("Creating .env file...", "INFO")
        
        # Define the paths
        download_dir = self.root_dir / "downloads"
        playlist_dir = self.root_dir / "playlists"
        music_lib_dir = self.root_dir / "music_library"
        
        # Create the .env content
        env_content = f"""# Music Library Manager Configuration

# App Configuration
APP_MODE=deployed
DEBUG_MODE=false

# Directory Configuration
ROOT_FOLDER={self.root_dir}
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
        
        try:
            # Write the .env file
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            # Create the directories if they don't exist
            for directory in [download_dir, playlist_dir, music_lib_dir]:
                directory.mkdir(exist_ok=True)
            
            self.print_status(".env file created successfully", "SUCCESS")
            self.print_status(f"Download directory: {download_dir}", "INFO")
            self.print_status(f"Playlist directory: {playlist_dir}", "INFO")
            self.print_status(f"Music library directory: {music_lib_dir}", "INFO")
            return True
            
        except Exception as e:
            self.print_status(f"Failed to create .env file: {e}", "ERROR")
            return False
    
    def create_virtual_environment(self):
        """Create virtual environment if it doesn't exist."""
        if self.venv_dir.exists():
            self.print_status("Virtual environment already exists", "INFO")
            return True
        
        self.print_status("Creating virtual environment...", "INFO")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)], 
                         check=True, capture_output=True)
            self.print_status("Virtual environment created successfully", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            self.print_status(f"Failed to create virtual environment: {e}", "ERROR")
            return False
    
    def install_dependencies(self):
        """Install required dependencies."""
        if not self.venv_pip.exists():
            self.print_status("Virtual environment not found. Please run the launcher again.", "ERROR")
            return False
        
        self.print_status("Installing dependencies...", "INFO")
        
        try:
            # Try to upgrade pip, but don't fail if it doesn't work
            self.print_status("Upgrading pip...", "INFO")
            try:
                subprocess.run([str(self.venv_pip), "install", "--upgrade", "pip"], 
                             check=True, capture_output=True, timeout=60)
                self.print_status("Pip upgraded successfully", "SUCCESS")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                self.print_status("Pip upgrade failed, continuing with existing version", "WARNING")
                self.print_status(f"Error: {e}", "WARNING")
            
            # Install requirements
            if self.requirements_file.exists():
                self.print_status("Installing requirements...", "INFO")
                try:
                    # Use --no-cache-dir to avoid cache issues
                    result = subprocess.run([str(self.venv_pip), "install", "--no-cache-dir", "-r", str(self.requirements_file)], 
                                         check=True, capture_output=True, text=True, timeout=300)
                    self.print_status("Dependencies installed successfully", "SUCCESS")
                    return True
                except subprocess.CalledProcessError as e:
                    self.print_status(f"Failed to install requirements: {e}", "ERROR")
                    if e.stderr:
                        self.print_status(f"Error details: {e.stderr}", "ERROR")
                    
                    # Try alternative installation method
                    self.print_status("Trying alternative installation method...", "INFO")
                    try:
                        # Install packages one by one
                        with open(self.requirements_file, 'r') as f:
                            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                        
                        for req in requirements:
                            self.print_status(f"Installing {req}...", "INFO")
                            subprocess.run([str(self.venv_pip), "install", "--no-cache-dir", req], 
                                         check=True, capture_output=True, timeout=120)
                        
                        self.print_status("Dependencies installed successfully (alternative method)", "SUCCESS")
                        return True
                    except subprocess.CalledProcessError as e2:
                        self.print_status(f"Alternative installation also failed: {e2}", "ERROR")
                        return False
                    except subprocess.TimeoutExpired:
                        self.print_status("Installation timed out", "ERROR")
                        return False
                except subprocess.TimeoutExpired:
                    self.print_status("Installation timed out", "ERROR")
                    return False
            else:
                self.print_status("requirements.txt not found!", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"Unexpected error during installation: {e}", "ERROR")
            return False
    
    def check_config_files(self):
        """Check if necessary configuration files exist."""
        config_files = {
            "app/config.py": "Application configuration",
            "app/main.py": "Main application"
        }
        
        missing_files = []
        for file_path, description in config_files.items():
            if not (self.root_dir / file_path).exists():
                missing_files.append(f"{file_path} ({description})")
        
        if missing_files:
            self.print_status("Missing required files:", "WARNING")
            for file in missing_files:
                self.print_status(f"  - {file}", "WARNING")
            return False
        
        self.print_status("All configuration files found", "SUCCESS")
        return True
    
    def start_application(self):
        """Start the Flask application."""
        if not self.venv_python.exists():
            self.print_status("Virtual environment not found!", "ERROR")
            return False
        
        self.print_status("Starting Music Library Manager...", "INFO")
        
        # Change to app directory
        os.chdir(self.app_dir)
        
        try:
            # Start the application
            process = subprocess.Popen([str(self.venv_python), "main.py"])
            
            # Wait a moment for the app to start
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                self.print_status("Application started successfully", "SUCCESS")
                self.print_status("Opening browser...", "INFO")
                
                # Open browser
                webbrowser.open("http://localhost:5000")
                
                self.print_status("Browser opened successfully", "SUCCESS")
                self.print_status("Press Ctrl+C to stop the application", "INFO")
                
                try:
                    # Wait for the process to finish
                    process.wait()
                except KeyboardInterrupt:
                    self.print_status("Stopping application...", "INFO")
                    process.terminate()
                    process.wait()
                    self.print_status("Application stopped", "SUCCESS")
            else:
                self.print_status("Failed to start application", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"Error starting application: {e}", "ERROR")
            return False
        
        return True
    
    def create_desktop_shortcut(self):
        """Create a desktop shortcut for easy access."""
        try:
            if self.is_windows:
                import winshell
                from win32com.client import Dispatch
                
                desktop = winshell.desktop()
                shortcut_path = os.path.join(desktop, "Music Library Manager.lnk")
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = sys.executable
                shortcut.Arguments = f'"{self.root_dir / "launcher.py"}"'
                shortcut.WorkingDirectory = str(self.root_dir)
                shortcut.IconLocation = sys.executable
                shortcut.save()
                
                self.print_status("Desktop shortcut created", "SUCCESS")
            else:
                # For Linux/macOS, create a .desktop file
                desktop_file = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Music Library Manager
Comment=Music Library Management Application
Exec={sys.executable} {self.root_dir / "launcher.py"}
Path={self.root_dir}
Icon={self.root_dir / "icon.png" if (self.root_dir / "icon.png").exists() else ""}
Terminal=false
Categories=AudioVideo;Audio;Player;Music;
"""
                
                desktop_dir = Path.home() / "Desktop"
                if not desktop_dir.exists():
                    desktop_dir = Path.home() / ".local" / "share" / "applications"
                
                shortcut_path = desktop_dir / "music-library-manager.desktop"
                with open(shortcut_path, 'w') as f:
                    f.write(desktop_file)
                
                # Make executable
                os.chmod(shortcut_path, 0o755)
                self.print_status("Desktop shortcut created", "SUCCESS")
                
        except Exception as e:
            self.print_status(f"Could not create desktop shortcut: {e}", "WARNING")
    
    def run(self):
        """Main launcher function."""
        self.print_status("=== Music Library Manager Launcher ===", "INFO")
        self.print_status(f"Platform: {platform.system()} {platform.release()}", "INFO")
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Check configuration files
        if not self.check_config_files():
            return False
        
        # Create .env file if it doesn't exist
        if not self.create_env_file():
            return False
        
        # Create virtual environment
        if not self.create_virtual_environment():
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Ask user if they want a desktop shortcut
        try:
            create_shortcut = input("\nCreate desktop shortcut for easy access? (y/n): ").lower().strip()
            if create_shortcut in ['y', 'yes']:
                self.create_desktop_shortcut()
        except KeyboardInterrupt:
            pass
        
        # Start the application
        return self.start_application()

def main():
    """Main entry point."""
    launcher = MusicLibLauncher()
    
    try:
        success = launcher.run()
        if not success:
            print("\nPress Enter to exit...")
            input()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nLauncher interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Press Enter to exit...")
        input()
        sys.exit(1)

if __name__ == "__main__":
    main() 