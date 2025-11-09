"""Tests for configuration module."""

import unittest
from pathlib import Path
from youtube_downloader.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for Config class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()

    def test_music_dir_is_path(self):
        """Test that music directory returns a Path object."""
        music_dir = self.config.get_default_music_dir()
        self.assertIsInstance(music_dir, Path)

    def test_video_dir_is_path(self):
        """Test that video directory returns a Path object."""
        video_dir = self.config.get_default_video_dir()
        self.assertIsInstance(video_dir, Path)

    def test_ffmpeg_path_is_string(self):
        """Test that ffmpeg path returns a string."""
        ffmpeg_path = self.config.get_ffmpeg_path()
        self.assertIsInstance(ffmpeg_path, str)


if __name__ == "__main__":
    unittest.main()
