# YouTube Downloader

A desktop application for downloading YouTube videos and audio using a clean, dark-themed GUI interface. Built with Python and tkinter.

## Features

- **Video Downloader**
  - Download YouTube videos in up to 1080p quality
  - Real-time progress tracking with speed and ETA
  - Dark theme interface
  - Automatic video format selection
  - Built-in logging system

- **Audio Downloader**
  - Extract high-quality audio (320kbps MP3)
  - Playlist support
  - Dark theme interface
  - Simple one-click download

## Requirements

- Python 3.8+
- FFmpeg
- Required Python packages (automatically installed):
  - yt-dlp
  - validators

## Installation

### Option 1: Install as a Package (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/jarrydgordon/youtube-downloader.git
cd youtube-downloader
```

2. Install the package:
```bash
pip install -e .
```

3. Install FFmpeg:
   - **Windows**: Download from [official website](https://ffmpeg.org/download.html), extract, and place in `ffmpeg/ffmpeg-master-latest-win64-gpl/bin/` directory
   - **Linux**: `sudo apt install ffmpeg` (Debian/Ubuntu) or `sudo yum install ffmpeg` (RHEL/CentOS)
   - **macOS**: `brew install ffmpeg`

### Option 2: Run Without Installation

1. Clone the repository:
```bash
git clone https://github.com/jarrydgordon/youtube-downloader.git
cd youtube-downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg (see above)

## Usage

### After Package Installation

```bash
# Run video downloader
yt-video

# Run audio downloader
yt-audio
```

### Without Package Installation

```bash
# Run video downloader
python YT_Video.py

# Run audio downloader
python YT_Audio.py
```

Or use the module directly:
```bash
python -m youtube_downloader.video_downloader
python -m youtube_downloader.audio_downloader
```

## Project Structure

```
youtube-downloader/
├── youtube_downloader/        # Main package directory
│   ├── __init__.py           # Package initialization
│   ├── base_gui.py           # Shared GUI components
│   ├── config.py             # Configuration management
│   ├── audio_downloader.py   # Audio downloader GUI
│   └── video_downloader.py   # Video downloader GUI
├── tests/                    # Test directory
│   ├── __init__.py
│   ├── test_config.py
│   └── test_base_gui.py
├── YT_Audio.py              # Legacy wrapper (deprecated)
├── YT_Video.py              # Legacy wrapper (deprecated)
├── setup.py                 # Package setup file
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Default Save Locations

The application automatically detects your operating system and uses appropriate default directories:

- **Videos**:
  - Windows: `C:/Users/[Username]/Videos`
  - macOS: `/Users/[Username]/Movies`
  - Linux: `/home/[Username]/Videos`

- **Audio**:
  - Windows: `C:/Users/[Username]/Music`
  - macOS: `/Users/[Username]/Music`
  - Linux: `/home/[Username]/Music`

## Development

### Running Tests

```bash
python -m pytest tests/
```

Or run individual test files:
```bash
python -m unittest tests.test_config
python -m unittest tests.test_base_gui
```

### Code Quality

The codebase follows these principles:
- Clean code architecture with shared base classes
- Cross-platform compatibility
- Proper error handling and validation
- Comprehensive documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.