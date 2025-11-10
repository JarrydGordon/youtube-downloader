"""Tests for configuration module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from youtube_downloader.config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_music_dir_is_path(self):
        """Test that music directory returns a Path object."""
        config = Config()
        music_dir = config.get_default_music_dir()
        assert isinstance(music_dir, Path)

    def test_video_dir_is_path(self):
        """Test that video directory returns a Path object."""
        config = Config()
        video_dir = config.get_default_video_dir()
        assert isinstance(video_dir, Path)

    def test_ffmpeg_path_is_string(self):
        """Test that ffmpeg path returns a string."""
        config = Config()
        ffmpeg_path = config.get_ffmpeg_path()
        assert isinstance(ffmpeg_path, str)

    @pytest.mark.parametrize("platform_name,expected_music_dir", [
        ("Windows", Path.home() / "Music"),
        ("Darwin", Path.home() / "Music"),
        ("Linux", Path.home() / "Music"),
    ])
    def test_music_dir_by_platform(self, platform_name, expected_music_dir):
        """Test music directory path for different platforms."""
        with patch('platform.system', return_value=platform_name):
            config = Config()
            music_dir = config.get_default_music_dir()
            assert music_dir == expected_music_dir

    @pytest.mark.parametrize("platform_name,expected_video_dir", [
        ("Windows", Path.home() / "Videos"),
        ("Darwin", Path.home() / "Movies"),
        ("Linux", Path.home() / "Videos"),
    ])
    def test_video_dir_by_platform(self, platform_name, expected_video_dir):
        """Test video directory path for different platforms."""
        with patch('platform.system', return_value=platform_name):
            config = Config()
            video_dir = config.get_default_video_dir()
            assert video_dir == expected_video_dir

    def test_ffmpeg_path_windows(self):
        """Test FFmpeg path on Windows."""
        with patch('platform.system', return_value='Windows'):
            config = Config()
            ffmpeg_path = config.get_ffmpeg_path()
            assert ffmpeg_path.endswith('ffmpeg.exe')
            assert './ffmpeg' in ffmpeg_path

    def test_ffmpeg_path_unix(self):
        """Test FFmpeg path on Unix-like systems."""
        with patch('platform.system', return_value='Linux'):
            config = Config()
            ffmpeg_path = config.get_ffmpeg_path()
            assert ffmpeg_path == 'ffmpeg'

    def test_ffmpeg_path_macos(self):
        """Test FFmpeg path on macOS."""
        with patch('platform.system', return_value='Darwin'):
            config = Config()
            ffmpeg_path = config.get_ffmpeg_path()
            assert ffmpeg_path == 'ffmpeg'

    def test_platform_detection(self):
        """Test that platform is correctly detected."""
        config = Config()
        assert config.platform in ['Windows', 'Linux', 'Darwin']

    def test_music_dir_in_home(self):
        """Test that music directory is within home directory."""
        config = Config()
        music_dir = config.get_default_music_dir()
        assert str(music_dir).startswith(str(Path.home()))

    def test_video_dir_in_home(self):
        """Test that video directory is within home directory."""
        config = Config()
        video_dir = config.get_default_video_dir()
        assert str(video_dir).startswith(str(Path.home()))

    def test_config_initialization(self):
        """Test Config object initialization."""
        config = Config()
        assert hasattr(config, 'platform')
        assert hasattr(config, 'get_default_music_dir')
        assert hasattr(config, 'get_default_video_dir')
        assert hasattr(config, 'get_ffmpeg_path')

    def test_multiple_instances(self):
        """Test that multiple Config instances work independently."""
        config1 = Config()
        config2 = Config()

        assert config1.get_default_music_dir() == config2.get_default_music_dir()
        assert config1.get_default_video_dir() == config2.get_default_video_dir()
        assert config1.get_ffmpeg_path() == config2.get_ffmpeg_path()
