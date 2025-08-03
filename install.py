import os
import sys
import subprocess
import platform
import venv
from pathlib import Path
import logging
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Subdirectory names
DOWNLOAD_SUBDIR = "downloads"
MUSIC_LIB_SUBDIR = "MusicLib"
PLAYLIST_SUBDIR = "playlists"

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    if current_version < required_version:
        logging.error(f"Python {required_version[0]}.{required_version[1]} or higher is required. Found {current_version[0]}.{current_version[1]}.")
        sys.exit(1)
    logging.info(f"Python version {current_version[0]}.{current_version[1]} is compatible.")

def get_venv_python_path(venv_dir):
    """Get the Python executable path for the virtual environment across all platforms."""
    if platform.system() == "Windows":
        return venv_dir / "Scripts" / "python.exe"
    else:
        return venv_dir / "bin" / "python"

def get_venv_activate_path(venv_dir):
    """Get the activation script path for the virtual environment across all platforms."""
    if platform.system() == "Windows":
        return venv_dir / "Scripts" / "activate.bat"
    else:
        return venv_dir / "bin" / "activate"

def create_virtualenv():
    """Create a virtual environment in the project directory."""
    venv_dir = Path("venv")
    if venv_dir.exists():
        logging.info("Virtual environment already exists. Skipping creation.")
        return get_venv_python_path(venv_dir)
    
    logging.info("Creating virtual environment...")
    try:
        venv.create(venv_dir, with_pip=True)
        logging.info("Virtual environment created successfully.")
        return get_venv_python_path(venv_dir)
    except Exception as e:
        logging.error(f"Failed to create virtual environment: {e}")
        sys.exit(1)

def install_dependencies(python_exec):
    """Install dependencies from requirements.txt."""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        logging.error(f"requirements.txt not found in {Path.cwd()}. Please create it with required dependencies.")
        sys.exit(1)

    logging.info("Installing dependencies from requirements.txt...")
    try:
        # Upgrade pip
        subprocess.check_call([str(python_exec), "-m", "pip", "install", "--upgrade", "pip"])
        # Install dependencies from requirements.txt
        subprocess.check_call([str(python_exec), "-m", "pip", "install", "-r", str(requirements_file)])
        logging.info("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install dependencies: {e}")
        sys.exit(1)

def get_user_input(prompt, default):
    """Prompt user for input, return default if empty."""
    user_input = input(f"{prompt} [{default}]: ").strip()
    return user_input or default

def create_env_file():
    """Create .env file with directories under a user-specified root directory."""
    env_content = []
    project_root = Path.cwd()

    # Prompt for root directory
    logging.info("Configuring .env file...")
    root_dir = get_user_input(
        "Enter root directory for downloads, music library, and playlists",
        str(project_root)
    )

    # Ensure root directory is absolute and handle path separators
    root_path = Path(root_dir).resolve()
    root_dir = str(root_path)

    # Define subdirectories using pathlib for cross-platform compatibility
    download_dir = str(root_path / DOWNLOAD_SUBDIR)
    music_lib_dir = str(root_path / MUSIC_LIB_SUBDIR)
    playlist_dir = str(root_path / PLAYLIST_SUBDIR)

    # Create directories
    for dir_path in [download_dir, music_lib_dir, playlist_dir]:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logging.info(f"Created directory: {dir_path}")
        except Exception as e:
            logging.error(f"Failed to create directory {dir_path}: {e}")
            sys.exit(1)

    # Create .env content with proper path separators
    env_content.append(f"DOWNLOAD_DIR={download_dir}")
    env_content.append(f"MUSIC_LIB_DIR={music_lib_dir}")
    env_content.append(f"PLAYLIST_DIR={playlist_dir}")

    # Write .env file
    env_file_path = project_root / ".env"
    try:
        with open(env_file_path, "w", encoding='utf-8') as f:
            f.write("\n".join(env_content) + "\n")
        logging.info(f".env file created at {env_file_path}")
    except Exception as e:
        logging.error(f"Failed to create .env file: {e}")
        sys.exit(1)

def get_shell_instructions():
    """Get platform-specific shell activation instructions."""
    system = platform.system()
    if system == "Windows":
        return {
            "cmd": "venv\\Scripts\\activate.bat",
            "powershell": "venv\\Scripts\\Activate.ps1",
            "bash": "venv\\Scripts\\activate"
        }
    else:
        return {
            "bash": "source venv/bin/activate",
            "zsh": "source venv/bin/activate",
            "fish": "source venv/bin/activate.fish"
        }

def main():
    """Main installation function."""
    logging.info("Starting installation process...")
    logging.info(f"Operating System: {platform.system()} {platform.release()}")
    logging.info(f"Python Executable: {sys.executable}")

    # Check Python version
    check_python_version()

    # Create virtual environment
    python_exec = create_virtualenv()

    # Install dependencies
    install_dependencies(python_exec)

    # Create .env file
    create_env_file()

    logging.info("Installation completed successfully!")
    logging.info("To run the application:")
    
    # Get platform-specific activation instructions
    shell_instructions = get_shell_instructions()
    
    logging.info("1. Activate the virtual environment:")
    for shell, command in shell_instructions.items():
        logging.info(f"   {shell}: {command}")
    
    logging.info(f"2. Run the Flask app: {python_exec} app.py")
    logging.info("3. Open http://localhost:5000 in your browser.")
    
    # Platform-specific notes
    system = platform.system()
    if system == "Windows":
        logging.info("Note: If using PowerShell, you may need to set execution policy:")
        logging.info("   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser")
    elif system == "Darwin":  # macOS
        logging.info("Note: If using spotdl, install FFmpeg with: brew install ffmpeg")
    else:  # Linux
        logging.info("Note: If using spotdl, install FFmpeg with: sudo apt install ffmpeg")
    
    logging.info("For FFmpeg installation on all platforms, see: https://ffmpeg.org/")

if __name__ == "__main__":
    main()