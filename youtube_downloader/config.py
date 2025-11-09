"""Configuration management for YouTube Downloader."""

from pathlib import Path
import os
import platform


class Config:
    """Configuration class for managing user-specific settings."""

    def __init__(self):
        self.platform = platform.system()

    def get_default_music_dir(self):
        """Get the default music directory based on the operating system."""
        if self.platform == "Windows":
            return Path.home() / "Music"
        elif self.platform == "Darwin":  # macOS
            return Path.home() / "Music"
        else:  # Linux and others
            return Path.home() / "Music"

    def get_default_video_dir(self):
        """Get the default video directory based on the operating system."""
        if self.platform == "Windows":
            return Path.home() / "Videos"
        elif self.platform == "Darwin":  # macOS
            return Path.home() / "Movies"
        else:  # Linux and others
            return Path.home() / "Videos"

    def get_ffmpeg_path(self):
        """Get the FFmpeg path based on the operating system."""
        if self.platform == "Windows":
            return str(Path("./ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe"))
        else:
            # On Linux/Mac, assume ffmpeg is in PATH or use local install
            return "ffmpeg"
