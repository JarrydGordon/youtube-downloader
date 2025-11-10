# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Quality selection dropdown for video downloads
- Cancel button for in-progress downloads
- Directory browser for output location selection
- Batch download support for multiple URLs
- Download history and favorites

## [1.1.0] - Upcoming

### Added
- **Quality Selection**: Choose video quality (720p, 1080p, 4K) before downloading
- **Cancel Functionality**: Ability to cancel in-progress downloads
- **Directory Browser**: Browse and select custom output directories
- **Enhanced Progress Tracking**: More detailed download statistics
- **Comprehensive Documentation**: Added CONTRIBUTING.md and expanded README
- **Improved Error Handling**: Better error messages and recovery options
- **Code Documentation**: Complete docstrings for all public methods
- **Testing Infrastructure**: Expanded test coverage and test utilities

### Changed
- Refactored project structure for better maintainability
- Improved GUI responsiveness and user feedback
- Updated dependencies to latest stable versions
- Enhanced cross-platform compatibility
- Modernized code formatting with Black and isort

### Fixed
- URL validation for shortened YouTube links (youtu.be)
- FFmpeg path detection on Linux/macOS
- Progress bar accuracy for large files
- Memory usage optimization for long downloads
- Thread safety improvements in GUI updates

### Security
- Input validation for all user-provided URLs
- Sanitized file paths to prevent directory traversal
- Updated dependencies to address security vulnerabilities

## [1.0.0] - 2025-01-15

### Added
- **Video Downloader**: Download YouTube videos up to 1080p quality
  - Real-time progress tracking with speed and ETA
  - Automatic format selection and merging
  - Concurrent fragment downloads for faster speeds
  - Built-in logging system
- **Audio Downloader**: Extract high-quality audio (320kbps MP3)
  - Support for individual videos
  - Playlist download capability
  - Automatic audio extraction and conversion
- **Dark Theme Interface**: Clean, modern dark-themed GUI using tkinter
- **Cross-Platform Support**: Windows, macOS, and Linux compatibility
- **Configuration Management**: Automatic detection of default directories
  - Platform-specific default locations for videos and music
  - FFmpeg path configuration
- **URL Validation**: Comprehensive URL validation for YouTube links
- **Paste from Clipboard**: Quick URL pasting functionality
- **Package Installation**: Console scripts for easy launching
  - `yt-video` command for video downloads
  - `yt-audio` command for audio downloads
- **Base GUI Framework**: Shared components for consistent UI
- **Error Handling**: User-friendly error messages and validation
- **Progress Indicators**: Visual feedback during downloads

### Technical Features
- Modular architecture with base class inheritance
- Threading for non-blocking downloads
- Integration with yt-dlp for robust downloading
- FFmpeg integration for media processing
- Logging system for troubleshooting
- Unit tests for core functionality

### Documentation
- Comprehensive README with installation and usage instructions
- MIT License
- Setup.py for package distribution
- Requirements.txt for dependency management

### Dependencies
- yt-dlp >= 2023.0.0
- validators >= 0.20.0
- tkinter (included with Python)
- FFmpeg (external dependency)

## Version History Summary

- **1.0.0**: Initial release with video and audio download functionality
- **1.1.0**: Enhanced features including quality selection, cancel functionality, and improved UX

## Migration Guides

### Upgrading from 1.0.0 to 1.1.0

No breaking changes. Simply update the package:

```bash
pip install --upgrade youtube-downloader
```

Or if installed in editable mode:

```bash
git pull origin main
pip install -e .
```

All existing functionality remains compatible. New features are additive only.

## Support

For issues, feature requests, or questions:
- GitHub Issues: https://github.com/JarrydGordon/youtube-downloader/issues
- Documentation: See README.md and CONTRIBUTING.md

## Links

- [PyPI Package](https://pypi.org/project/youtube-downloader/)
- [GitHub Repository](https://github.com/JarrydGordon/youtube-downloader)
- [Issue Tracker](https://github.com/JarrydGordon/youtube-downloader/issues)
- [Changelog](https://github.com/JarrydGordon/youtube-downloader/blob/main/CHANGELOG.md)
