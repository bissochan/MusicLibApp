#!/bin/bash

# Music Library Manager Launcher for Linux/macOS
# Make this file executable with: chmod +x start.sh

echo ""
echo "========================================"
echo "   Music Library Manager Launcher"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "[ERROR] Python 3.8 or higher is required"
    echo "Current version: $python_version"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "[INFO] Python version: $python_version"

# Run the launcher
python3 launcher.py

# If there was an error, pause so user can see the message
if [ $? -ne 0 ]; then
    echo ""
    echo "Press Enter to exit..."
    read
fi 