#!/usr/bin/env python3
"""
Windows-specific Music Library Manager Launcher
Handles common Windows issues with pip and virtual environments.
"""

import os
import sys
import subprocess
import time
import webbrowser
import platform
from pathlib import Path
import json

class WindowsMusicLibLauncher:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.venv_dir = self.root_dir / "venv"
        self.requirements_file = self.root_dir / "requirements.txt"
        self.app_dir = self.root_dir / "app"
        
        # Windows-specific paths
        self.venv_python = self.venv_dir / "Scripts" / "python.exe"
        self.venv_pip = self.venv_dir / "Scripts" / "pip.exe"
    
    def print_status(self, message, status="INFO"):
        """Print a formatted status message."""
        print(f"[{status}] {message}")
    
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
            # Use python -m venv with explicit path
            result = subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)], 
                                 check=True, capture_output=True, text=True)
            self.print_status("Virtual environment created successfully", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            self.print_status(f"Failed to create virtual environment: {e}", "ERROR")
            if e.stderr:
                self.print_status(f"Error details: {e.stderr}", "ERROR")
            return False
    
    def install_dependencies(self):
        """Install required dependencies with Windows-specific handling."""
        if not self.venv_pip.exists():
            self.print_status("Virtual environment not found. Please run the launcher again.", "ERROR")
            return False
        
        self.print_status("Installing dependencies...", "INFO")
        
        try:
            # Skip pip upgrade on Windows to avoid common issues
            self.print_status("Skipping pip upgrade (Windows compatibility)", "INFO")
            
            # Install requirements with Windows-specific options
            if self.requirements_file.exists():
                self.print_status("Installing requirements...", "INFO")
                try:
                    # Use --user flag and --no-cache-dir for Windows compatibility
                    cmd = [str(self.venv_pip), "install", "--no-cache-dir", "--trusted-host", "pypi.org", "--trusted-host", "pypi.python.org", "--trusted-host", "files.pythonhosted.org", "-r", str(self.requirements_file)]
                    
                    result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)
                    self.print_status("Dependencies installed successfully", "SUCCESS")
                    return True
                    
                except subprocess.CalledProcessError as e:
                    self.print_status(f"Failed to install requirements: {e}", "ERROR")
                    if e.stderr:
                        self.print_status(f"Error details: {e.stderr}", "ERROR")
                    
                    # Try alternative installation method
                    self.print_status("Trying alternative installation method...", "INFO")
                    try:
                        # Install packages one by one with Windows-specific options
                        with open(self.requirements_file, 'r') as f:
                            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                        
                        for req in requirements:
                            self.print_status(f"Installing {req}...", "INFO")
                            cmd = [str(self.venv_pip), "install", "--no-cache-dir", "--trusted-host", "pypi.org", "--trusted-host", "pypi.python.org", "--trusted-host", "files.pythonhosted.org", req]
                            subprocess.run(cmd, check=True, capture_output=True, timeout=300)
                        
                        self.print_status("Dependencies installed successfully (alternative method)", "SUCCESS")
                        return True
                        
                    except subprocess.CalledProcessError as e2:
                        self.print_status(f"Alternative installation also failed: {e2}", "ERROR")
                        if e2.stderr:
                            self.print_status(f"Error details: {e2.stderr}", "ERROR")
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
    
    def run(self):
        """Main launcher function."""
        self.print_status("=== Music Library Manager Launcher (Windows) ===", "INFO")
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
        
        # Start the application
        return self.start_application()

def main():
    """Main entry point."""
    launcher = WindowsMusicLibLauncher()
    
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