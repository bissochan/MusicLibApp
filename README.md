# Music Library Manager

A modern web application for organizing and managing your music library with playlist support.

## 🚀 Quick Start

### For Windows Users:
1. **Double-click** `start.bat` to launch the application
2. The launcher will automatically:
   - Check Python installation
   - Create virtual environment
   - Install dependencies
   - Start the application
   - Open your browser

### For Linux/macOS Users:
1. **Double-click** `start.sh` or run `./start.sh` in terminal
2. The launcher will handle everything automatically

### Manual Start:
1. Run `python launcher.py` in the project directory
2. Follow the prompts

## 📋 Requirements

- **Python 3.8 or higher**
- **Internet connection** (for first-time dependency installation)

## 🎯 Features

- **Music Organization**: Automatically organize songs by artist/album
- **Playlist Management**: Create and manage playlists
- **Duplicate Detection**: Smart duplicate checking
- **Download Integration**: Works with spotdl for music downloads
- **Modern UI**: Clean, responsive interface with dark mode
- **Settings Management**: Comprehensive configuration options
- **Search Functionality**: Search your music library

## 🔧 Configuration

The application includes a comprehensive settings page where you can configure:

- **Application Mode**: Debug or deployed mode
- **Download Settings**: Retries, timeouts, file retention
- **Library Organization**: Auto-organize, duplicate checking
- **UI Preferences**: Dark mode, progress bars, search limits
- **Performance**: Concurrent downloads, metadata caching

## 📁 File Structure

```
MusicLibApp/
├── launcher.py          # Main launcher script
├── start.bat           # Windows launcher
├── start.sh            # Linux/macOS launcher
├── requirements.txt    # Python dependencies
├── config_sample.env   # Sample configuration
├── app/
│   ├── main.py        # Flask application
│   ├── config.py      # Configuration management
│   ├── services/      # Business logic
│   ├── templates/     # HTML templates
│   └── static/        # CSS, JS, assets
└── venv/              # Virtual environment (created automatically)
```

## 🎨 User Interface

- **Modern Design**: Clean, professional interface
- **Dark Mode**: Toggle between light and dark themes
- **Responsive**: Works on desktop and mobile
- **Intuitive**: Easy-to-use forms and controls

## 🔍 Search Features

- **Library Search**: Search by song title, artist, or album
- **Real-time Results**: Instant search results
- **Smart Filtering**: Intelligent result ranking

## 📊 Progress Tracking

- **Download Progress**: Real-time download status
- **Processing Status**: Track song organization
- **Visual Feedback**: Progress bars and counters

## 🛠️ Troubleshooting

### Common Issues:

1. **Python not found**: Install Python 3.8+ from python.org
2. **Permission errors**: Run as administrator (Windows) or use sudo (Linux)
3. **Port already in use**: Close other applications using port 5000
4. **Dependencies failed**: Check internet connection and try again

### Getting Help:

- Check the console output for error messages
- Ensure all required files are present
- Verify Python version is 3.8 or higher

## 🚀 Advanced Usage

### Development Mode:
- Set `APP_MODE=debug` in settings for full feature access
- Shows additional download options and debug information

### Production Mode:
- Set `APP_MODE=deployed` for clean, user-friendly interface
- Hides technical options for end users

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

**Made with ❤️ for music lovers everywhere**