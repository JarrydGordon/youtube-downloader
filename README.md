# YouTube Downloader

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/JarrydGordon/youtube-downloader/releases)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/JarrydGordon/youtube-downloader/graphs/commit-activity)

A desktop application for downloading YouTube videos and audio using a clean, dark-themed GUI interface. Built with Python and tkinter.

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Documentation](#documentation)
- [New Features (v1.1.0)](#new-features-v110)
- [Project Structure](#project-structure)
- [Default Save Locations](#default-save-locations)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

## Features

### Video Downloader
- Download YouTube videos in up to 1080p quality
- Real-time progress tracking with speed and ETA
- Dark theme interface
- Automatic video format selection and merging
- Concurrent fragment downloads for faster speeds
- Built-in logging system

### Audio Downloader
- Extract high-quality audio (320kbps MP3)
- Playlist support
- Dark theme interface
- Simple one-click download
- Automatic audio conversion

### General Features
- Cross-platform support (Windows, macOS, Linux)
- URL validation for YouTube links
- Paste from clipboard functionality
- Platform-specific default save locations
- User-friendly error messages

## Screenshots

> Screenshots coming soon

*The application features a clean, dark-themed interface with intuitive controls.*

## Requirements

- **Python 3.8+**
- **FFmpeg** (required for video/audio processing)
- **Python packages** (automatically installed):
  - yt-dlp >= 2023.0.0
  - validators >= 0.20.0

## Installation

### Option 1: Install as a Package (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jarrydgordon/youtube-downloader.git
   cd youtube-downloader
   ```

2. **Install the package**:
   ```bash
   pip install -e .
   ```

   Or using the setup.py directly:
   ```bash
   python setup.py install
   ```

3. **Install FFmpeg**:

   - **Windows**:
     1. Download from [FFmpeg official website](https://ffmpeg.org/download.html)
     2. Extract the archive
     3. Place in `ffmpeg/ffmpeg-master-latest-win64-gpl/bin/` directory
     4. Or add FFmpeg to your system PATH

   - **Linux**:
     ```bash
     # Debian/Ubuntu
     sudo apt update
     sudo apt install ffmpeg

     # RHEL/CentOS
     sudo yum install ffmpeg

     # Fedora
     sudo dnf install ffmpeg
     ```

   - **macOS**:
     ```bash
     brew install ffmpeg
     ```

### Option 2: Run Without Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jarrydgordon/youtube-downloader.git
   cd youtube-downloader
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg** (see instructions above)

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

### Basic Workflow

1. **Launch the application** using one of the methods above
2. **Enter a YouTube URL** or click "Paste URL" to paste from clipboard
3. **Configure options** (if applicable):
   - For audio: Check "Download Playlist" if downloading a playlist
   - For video: Monitor the progress bar for download status
4. **Click Download** and wait for completion
5. **Find your file** in the default save location

## Documentation

Complete documentation is available in the [`docs/`](./docs/) directory:

- **[Documentation Index](./docs/README.md)** - Overview of all documentation
- **[Contributing Guide](./docs/CONTRIBUTING.md)** - How to contribute to the project and set up development environment
- **[Testing Guide](./docs/TESTING.md)** - How to run tests and understand test structure
- **[Changelog](./docs/CHANGELOG.md)** - Version history and planned features
- **[CI/CD Setup](./docs/CICD_SETUP.md)** - Setting up continuous integration pipelines
- **[GitHub Workflows](./docs/WORKFLOWS.md)** - Documentation on automated CI/CD workflows

For a complete overview of all documentation, visit the [Documentation Index](./docs/README.md).

## New Features (v1.1.0)

The upcoming version 1.1.0 includes several exciting improvements:

- **Quality Selection**: Choose between different video qualities (720p, 1080p, 4K) before downloading
- **Cancel Downloads**: Stop in-progress downloads with a cancel button
- **Directory Browser**: Browse and select custom output directories instead of using defaults
- **Enhanced Progress Tracking**: More detailed download statistics and better progress visualization
- **Improved Error Handling**: Better error messages and recovery options

See [CHANGELOG.md](docs/CHANGELOG.md) for a complete list of changes.

## Project Structure

```
youtube-downloader/
├── docs/                     # Documentation directory
│   ├── README.md            # Documentation index
│   ├── CONTRIBUTING.md      # Contribution guidelines
│   ├── TESTING.md           # Testing guide
│   ├── CHANGELOG.md         # Version history
│   ├── CICD_SETUP.md        # CI/CD setup guide
│   └── WORKFLOWS.md         # GitHub workflows reference
├── youtube_downloader/       # Main package directory
│   ├── __init__.py          # Package initialization
│   ├── base_gui.py          # Shared GUI components
│   ├── config.py            # Configuration management
│   ├── audio_downloader.py  # Audio downloader GUI
│   └── video_downloader.py  # Video downloader GUI
├── tests/                    # Test directory
│   ├── __init__.py
│   ├── test_config.py       # Configuration tests
│   └── test_base_gui.py     # GUI component tests
├── .github/                 # GitHub configuration
│   ├── workflows/           # CI/CD workflows
│   └── ISSUE_TEMPLATE/      # Issue templates
├── YT_Audio.py              # Legacy wrapper (deprecated)
├── YT_Video.py              # Legacy wrapper (deprecated)
├── setup.py                 # Package setup file
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Default Save Locations

The application automatically detects your operating system and uses appropriate default directories:

### Videos
- **Windows**: `C:/Users/[Username]/Videos`
- **macOS**: `/Users/[Username]/Movies`
- **Linux**: `/home/[Username]/Videos`

### Audio
- **Windows**: `C:/Users/[Username]/Music`
- **macOS**: `/Users/[Username]/Music`
- **Linux**: `/home/[Username]/Music`

## Development

### Setting Up Development Environment

1. **Clone and install in editable mode**:
   ```bash
   git clone https://github.com/jarrydgordon/youtube-downloader.git
   cd youtube-downloader
   pip install -e .
   ```

2. **Install development dependencies**:
   ```bash
   pip install pytest black isort
   ```

### Running Tests

```bash
# Run all tests with pytest
pytest tests/

# Run with verbose output
pytest -v tests/

# Run with coverage
pytest --cov=youtube_downloader tests/

# Run specific test file
pytest tests/test_config.py

# Using unittest
python -m unittest tests.test_config
python -m unittest tests.test_base_gui
```

### Code Formatting

```bash
# Format code with Black
black youtube_downloader/ tests/

# Sort imports with isort
isort youtube_downloader/ tests/

# Check formatting without making changes
black --check youtube_downloader/ tests/
isort --check youtube_downloader/ tests/
```

### Code Quality

The codebase follows these principles:
- **Clean Architecture**: Shared base classes and modular design
- **Cross-Platform Compatibility**: Works on Windows, macOS, and Linux
- **Error Handling**: Comprehensive validation and user-friendly error messages
- **Documentation**: Complete docstrings for all public methods
- **Testing**: Unit tests for core functionality
- **Code Style**: PEP 8 compliance with Black formatting

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed development guidelines.

## Troubleshooting

### FFmpeg Not Found

**Problem**: Error message "FFmpeg not found - please check installation"

**Solution**:
- **Windows**: Ensure FFmpeg is either in the `ffmpeg/ffmpeg-master-latest-win64-gpl/bin/` directory or added to your system PATH
- **Linux/macOS**: Install FFmpeg using your package manager:
  ```bash
  # Ubuntu/Debian
  sudo apt install ffmpeg

  # macOS
  brew install ffmpeg
  ```
- Verify installation: `ffmpeg -version`

### Download Fails or Stalls

**Problem**: Downloads fail to start or stop mid-way

**Solution**:
- Check your internet connection
- Verify the YouTube URL is valid and the video is accessible
- Try downloading a different video to isolate the issue
- Check the logs in the `logs/` directory for detailed error messages
- Update yt-dlp: `pip install --upgrade yt-dlp`

### Invalid URL Error

**Problem**: "Not a YouTube URL" error appears

**Solution**:
- Ensure you're using a valid YouTube URL (youtube.com or youtu.be)
- Copy the URL directly from the browser address bar
- For playlists, make sure the URL contains `list=` parameter

### Playlist Download Not Working

**Problem**: Only one video downloads instead of the entire playlist

**Solution**:
- Make sure "Download Playlist" checkbox is checked
- Verify the URL contains the playlist ID (look for `list=` in the URL)
- Try copying the playlist URL from the playlist page, not an individual video

### Permission Errors

**Problem**: "Permission denied" when saving files

**Solution**:
- Ensure you have write permissions to the output directory
- Try running the application with administrator/sudo privileges (not recommended long-term)
- Change the output directory to a location where you have write access

### GUI Not Appearing

**Problem**: Application starts but no window appears

**Solution**:
- Ensure tkinter is installed: `python -m tkinter`
- Check if the window is appearing on a different monitor
- Try reinstalling Python with tkinter support
- On Linux, you may need to install: `sudo apt install python3-tk`

### Video Quality Lower Than Expected

**Problem**: Downloaded video quality is lower than 1080p

**Solution**:
- Not all YouTube videos are available in 1080p
- Check if the video supports the desired quality on YouTube
- The application automatically selects the best available quality up to 1080p
- For 4K support, wait for version 1.1.0 with quality selection

### Audio Quality Issues

**Problem**: Audio quality seems low or distorted

**Solution**:
- The application downloads at 320kbps MP3 by default (highest quality)
- Check if the source audio on YouTube is high quality
- Ensure FFmpeg is properly installed and up to date
- Try downloading the video first, then extracting audio separately

## FAQ

### General Questions

**Q: Is this application free to use?**

A: Yes, this application is open-source and free to use under the MIT License.

**Q: Can I download videos from sites other than YouTube?**

A: Currently, only YouTube is officially supported. However, yt-dlp (the underlying library) supports many sites. We may add support for other platforms in future versions.

**Q: Is it legal to download YouTube videos?**

A: This depends on your jurisdiction and the video's license. Generally, downloading copyrighted content without permission may violate YouTube's Terms of Service or copyright laws. Use this tool responsibly and only for content you have the right to download.

**Q: Does this work with age-restricted or private videos?**

A: No, the application cannot download age-restricted videos requiring login or private videos you don't have access to.

### Technical Questions

**Q: What video formats are supported?**

A: The application downloads videos and automatically merges them into MP4 format using FFmpeg.

**Q: What audio formats are supported?**

A: Audio is extracted and converted to MP3 format at 320kbps quality.

**Q: Can I download 4K videos?**

A: Currently, the maximum resolution is 1080p. Support for 4K and quality selection is planned for version 1.1.0.

**Q: How do I download an entire playlist?**

A: Use the audio downloader (`yt-audio`), check the "Download Playlist" checkbox, and enter a playlist URL.

**Q: Can I choose where to save downloads?**

A: Currently, files are saved to default OS-specific directories. A directory browser feature is coming in version 1.1.0.

**Q: Why does the application need FFmpeg?**

A: FFmpeg is required for merging video and audio streams, converting audio formats, and processing media files.

**Q: Can I run multiple downloads simultaneously?**

A: Currently, one download at a time is supported. Batch download support is planned for a future release.

**Q: How can I see download history?**

A: Download history is not currently tracked. This feature is planned for a future version.

### Troubleshooting Questions

**Q: Why is my download so slow?**

A: Download speed depends on your internet connection and YouTube's servers. The application uses concurrent fragment downloads to optimize speed.

**Q: What do I do if I encounter a bug?**

A: Please report bugs on our [GitHub Issues page](https://github.com/JarrydGordon/youtube-downloader/issues) with detailed information about the error.

**Q: How do I update to the latest version?**

A: Run `pip install --upgrade youtube-downloader` or `git pull` if installed from source.

**Q: Where are the log files stored?**

A: Log files are stored in the `logs/` directory in the application root folder (video downloader only).

## Security

### Security Considerations

This application takes security seriously. Here are some important security considerations:

### Input Validation

- All YouTube URLs are validated before processing
- Invalid or malicious URLs are rejected
- Playlist URLs are verified to contain proper playlist identifiers

### File System Safety

- Output file paths are sanitized to prevent directory traversal attacks
- Files are saved only to designated output directories
- No arbitrary code execution from downloaded content

### Dependencies

- We regularly update dependencies to address security vulnerabilities
- All dependencies are sourced from trusted repositories (PyPI)
- See `requirements.txt` for the list of dependencies

### Data Privacy

- **No data collection**: This application does not collect, store, or transmit any user data
- **No tracking**: No analytics or tracking of any kind
- **Local operation**: All processing happens locally on your machine
- **No authentication**: The application does not require or store any credentials

### Best Practices

When using this application:
- Only download content you have the right to download
- Keep your Python and dependencies up to date
- Review the code if you have security concerns (it's open source!)
- Report security vulnerabilities privately to the maintainers

### Reporting Security Issues

If you discover a security vulnerability, please report it by emailing the maintainers directly rather than creating a public issue. Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Permissions

The application requires:
- **Network access**: To download content from YouTube
- **File system access**: To save downloads to your chosen directory
- **No admin/root access required**: Runs with normal user privileges

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines on:
- Setting up your development environment
- Running tests
- Code style guidelines
- Submitting pull requests
- Reporting issues

Quick start:
```bash
# Fork the repo, clone it, then:
cd youtube-downloader
pip install -e .
pip install pytest black isort
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [yt-dlp](https://github.com/yt-dlp/yt-dlp) for robust YouTube downloading
- Uses [FFmpeg](https://ffmpeg.org/) for media processing
- GUI built with Python's tkinter

## Links

- [GitHub Repository](https://github.com/JarrydGordon/youtube-downloader)
- [Issue Tracker](https://github.com/JarrydGordon/youtube-downloader/issues)
- [Documentation](docs/README.md)
- [Changelog](docs/CHANGELOG.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)

---

**Note**: This tool is for personal use only. Respect copyright laws and YouTube's Terms of Service.
