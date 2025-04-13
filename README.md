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

- Python 3.x
- FFmpeg (included in repository)
- Required Python packages:
  - yt-dlp
  - tkinter
  - validators

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jarrydgordon/youtube-downloader.git
cd youtube-downloader
```

2. Install required Python packages:
```bash
pip install yt-dlp validators
```

## Usage

### Video Downloader
Run `YT_Video.py` to start the video downloader:
```bash
python YT_Video.py
```

### Audio Downloader
Run `YT_Audio.py` to start the audio downloader:
```bash
python YT_Audio.py
```

## Default Save Locations

- Videos: `C:/Users/[Username]/Videos`
- Audio: `C:/Users/[Username]/Music`

## Features

- Clean, modern dark theme interface
- Progress tracking for downloads
- Support for both video and audio downloads
- Playlist support for audio downloads
- Built-in logging system
- FFmpeg integration for high-quality audio extraction

## License

This project is licensed under the MIT License - see the LICENSE file for details.