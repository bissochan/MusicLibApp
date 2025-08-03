#!/usr/bin/env python3
"""
Troubleshooting script for Music Library Manager
Helps diagnose common issues with the setup.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_status(message, status="INFO"):
    """Print a formatted status message."""
    print(f"[{status}] {message}")

def check_python():
    """Check Python installation."""
    print_status("=== Python Environment Check ===", "INFO")
    
    version = sys.version_info
    print_status(f"Python version: {version.major}.{version.minor}.{version.micro}", "INFO")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_status("❌ Python 3.8 or higher is required!", "ERROR")
        return False
    
    print_status("✅ Python version is compatible", "SUCCESS")
    return True

def check_virtual_environment():
    """Check virtual environment."""
    print_status("=== Virtual Environment Check ===", "INFO")
    
    root_dir = Path(__file__).parent
    venv_dir = root_dir / "venv"
    
    if not venv_dir.exists():
        print_status("❌ Virtual environment not found", "ERROR")
        return False
    
    print_status("✅ Virtual environment exists", "SUCCESS")
    
    # Check if pip is available
    if platform.system() == "Windows":
        pip_path = venv_dir / "Scripts" / "pip.exe"
    else:
        pip_path = venv_dir / "bin" / "pip"
    
    if not pip_path.exists():
        print_status("❌ pip not found in virtual environment", "ERROR")
        return False
    
    print_status("✅ pip is available", "SUCCESS")
    return True

def check_dependencies():
    """Check if dependencies are installed."""
    print_status("=== Dependencies Check ===", "INFO")
    
    root_dir = Path(__file__).parent
    venv_dir = root_dir / "venv"
    
    if platform.system() == "Windows":
        python_path = venv_dir / "Scripts" / "python.exe"
    else:
        python_path = venv_dir / "bin" / "python"
    
    if not python_path.exists():
        print_status("❌ Python not found in virtual environment", "ERROR")
        return False
    
    # Try to import key dependencies
    try:
        result = subprocess.run([str(python_path), "-c", "import flask"], 
                             capture_output=True, text=True)
        if result.returncode != 0:
            print_status("❌ Flask not installed", "ERROR")
            return False
        print_status("✅ Flask is installed", "SUCCESS")
    except Exception as e:
        print_status(f"❌ Error checking Flask: {e}", "ERROR")
        return False
    
    try:
        result = subprocess.run([str(python_path), "-c", "import pytaglib"], 
                             capture_output=True, text=True)
        if result.returncode != 0:
            print_status("❌ pytaglib not installed", "ERROR")
            return False
        print_status("✅ pytaglib is installed", "SUCCESS")
    except Exception as e:
        print_status(f"❌ Error checking pytaglib: {e}", "ERROR")
        return False
    
    try:
        result = subprocess.run([str(python_path), "-c", "import spotdl"], 
                             capture_output=True, text=True)
        if result.returncode != 0:
            print_status("❌ spotdl not installed", "ERROR")
            return False
        print_status("✅ spotdl is installed", "SUCCESS")
    except Exception as e:
        print_status(f"❌ Error checking spotdl: {e}", "ERROR")
        return False
    
    return True

def check_files():
    """Check if required files exist."""
    print_status("=== Files Check ===", "INFO")
    
    root_dir = Path(__file__).parent
    required_files = [
        ".env",
        "app/config.py",
        "app/main.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (root_dir / file_path).exists():
            missing_files.append(file_path)
        else:
            print_status(f"✅ {file_path} exists", "SUCCESS")
    
    if missing_files:
        print_status("❌ Missing required files:", "ERROR")
        for file in missing_files:
            print_status(f"   - {file}", "ERROR")
        return False
    
    return True

def check_network():
    """Check network connectivity."""
    print_status("=== Network Check ===", "INFO")
    
    try:
        import urllib.request
        urllib.request.urlopen('https://pypi.org', timeout=5)
        print_status("✅ Network connectivity is good", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ Network connectivity issue: {e}", "ERROR")
        return False

def suggest_fixes():
    """Suggest fixes for common issues."""
    print_status("=== Troubleshooting Suggestions ===", "INFO")
    
    print_status("If you're having issues:", "INFO")
    print_status("1. Make sure Python 3.8+ is installed", "INFO")
    print_status("2. Try running as administrator (Windows)", "INFO")
    print_status("3. Check your internet connection", "INFO")
    print_status("4. Try deleting the 'venv' folder and running again", "INFO")
    print_status("5. Make sure all required files are present", "INFO")
    print_status("6. Try using the Windows-specific launcher: python launcher_windows.py", "INFO")

def main():
    """Main troubleshooting function."""
    print_status("=== Music Library Manager Troubleshooter ===", "INFO")
    print_status(f"Platform: {platform.system()} {platform.release()}", "INFO")
    
    all_good = True
    
    # Run all checks
    if not check_python():
        all_good = False
    
    if not check_files():
        all_good = False
    
    if not check_network():
        all_good = False
    
    if not check_virtual_environment():
        all_good = False
    
    if not check_dependencies():
        all_good = False
    
    print_status("=== Summary ===", "INFO")
    if all_good:
        print_status("✅ All checks passed! Your setup should work correctly.", "SUCCESS")
    else:
        print_status("❌ Some issues were found. Check the suggestions below.", "ERROR")
        suggest_fixes()
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main() 