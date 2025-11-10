"""User configuration management with persistent storage."""

from typing import Any, Optional
import json
from pathlib import Path

from .constants import (
    CONFIG_FILENAME,
    DEFAULT_VIDEO_QUALITY,
    DEFAULT_AUDIO_FORMAT
)


class UserConfig:
    """Manages user preferences with JSON persistence."""

    def __init__(self) -> None:
        """Initialize user config with default values."""
        self.config_dir: Path = Path.home() / ".youtube_downloader"
        self.config_file: Path = self.config_dir / CONFIG_FILENAME
        self.config: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from JSON file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                # Initialize with defaults
                self.config = self._get_defaults()
                self.save()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}. Using defaults.")
            self.config = self._get_defaults()

    def save(self) -> None:
        """Save configuration to JSON file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")

    def _get_defaults(self) -> dict[str, Any]:
        """Get default configuration values."""
        return {
            'last_video_dir': None,
            'last_audio_dir': None,
            'video_quality': DEFAULT_VIDEO_QUALITY,
            'audio_format': DEFAULT_AUDIO_FORMAT,
            'window_positions': {},
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save."""
        self.config[key] = value
        self.save()

    def get_last_video_dir(self) -> Optional[str]:
        """Get the last used video directory."""
        return self.config.get('last_video_dir')

    def set_last_video_dir(self, directory: str) -> None:
        """Set the last used video directory."""
        self.set('last_video_dir', directory)

    def get_last_audio_dir(self) -> Optional[str]:
        """Get the last used audio directory."""
        return self.config.get('last_audio_dir')

    def set_last_audio_dir(self, directory: str) -> None:
        """Set the last used audio directory."""
        self.set('last_audio_dir', directory)

    def get_video_quality(self) -> str:
        """Get preferred video quality."""
        return self.config.get('video_quality', DEFAULT_VIDEO_QUALITY)

    def set_video_quality(self, quality: str) -> None:
        """Set preferred video quality."""
        self.set('video_quality', quality)

    def get_audio_format(self) -> str:
        """Get preferred audio format."""
        return self.config.get('audio_format', DEFAULT_AUDIO_FORMAT)

    def set_audio_format(self, format_name: str) -> None:
        """Set preferred audio format."""
        self.set('audio_format', format_name)

    def get_window_position(self, window_name: str) -> Optional[str]:
        """Get saved window position for a specific window."""
        positions: dict[str, str] = self.config.get('window_positions', {})
        return positions.get(window_name)

    def set_window_position(self, window_name: str, geometry: str) -> None:
        """Save window position for a specific window."""
        if 'window_positions' not in self.config:
            self.config['window_positions'] = {}
        self.config['window_positions'][window_name] = geometry
        self.save()
