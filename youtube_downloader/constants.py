"""Constants for YouTube Downloader application."""

from typing import Final

# Window dimensions
WINDOW_WIDTH: Final[int] = 600
WINDOW_HEIGHT_BASE: Final[int] = 150
WINDOW_HEIGHT_VIDEO: Final[int] = 250
WINDOW_HEIGHT_AUDIO: Final[int] = 280

# Colors - Dark Theme
BG_COLOR_DARK: Final[str] = "#2b2b2b"
BG_COLOR_DARKER: Final[str] = "#1e1e1e"
FG_COLOR: Final[str] = "#ffffff"
FG_COLOR_DARK: Final[str] = "#000000"
HIGHLIGHT_COLOR: Final[str] = "#404040"
SELECT_BG_COLOR: Final[str] = "#ff0000"

# Padding values
PADDING_LARGE: Final[int] = 10
PADDING_MEDIUM: Final[int] = 5
PADDING_SMALL: Final[int] = 2

# Font configurations
FONT_DEFAULT: Final[tuple[str, int, str]] = ("TkDefaultFont", 9, "bold")
FONT_ENTRY: Final[tuple[str, int]] = ("Segoe UI", 10)

# Video quality options
VIDEO_QUALITIES: Final[dict[str, str]] = {
    "360p": "bv*[height<=360]+ba/b[height<=360]",
    "480p": "bv*[height<=480]+ba/b[height<=480]",
    "720p": "bv*[height<=720]+ba/b[height<=720]",
    "1080p": "bv*[height<=1080]+ba/b[height<=1080]",
    "1440p (2K)": "bv*[height<=1440]+ba/b[height<=1440]",
    "2160p (4K)": "bv*[height<=2160]+ba/b[height<=2160]",
}

# Audio format options
AUDIO_FORMATS: Final[dict[str, dict[str, str]]] = {
    "MP3": {"codec": "mp3", "quality": "320"},
    "M4A": {"codec": "m4a", "quality": "320"},
    "FLAC": {"codec": "flac", "quality": "0"},
    "WAV": {"codec": "wav", "quality": "0"},
    "OPUS": {"codec": "opus", "quality": "320"},
}

# Default quality settings
DEFAULT_VIDEO_QUALITY: Final[str] = "1080p"
DEFAULT_AUDIO_FORMAT: Final[str] = "MP3"

# Thread settings
CONCURRENT_FRAGMENTS: Final[int] = 3

# Logging
LOG_DIR: Final[str] = "logs"
LOG_DATE_FORMAT: Final[str] = "%Y%m%d"
LOG_FORMAT: Final[str] = "%(asctime)s - %(levelname)s - %(message)s"

# Config file
CONFIG_FILENAME: Final[str] = "yt_downloader_config.json"
