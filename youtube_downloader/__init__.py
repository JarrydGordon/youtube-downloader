"""YouTube Downloader - A simple GUI application for downloading YouTube videos and audio."""

__version__ = "1.0.0"

# Export main classes
from .video_downloader import YouTubeVideoDownloaderGUI
from .audio_downloader import YouTubeAudioDownloaderGUI
from .config import Config
from .user_config import UserConfig

__all__ = [
    'YouTubeVideoDownloaderGUI',
    'YouTubeAudioDownloaderGUI',
    'Config',
    'UserConfig',
]
