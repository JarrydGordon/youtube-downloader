"""Tests for base GUI module."""

import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from youtube_downloader.base_gui import BaseYouTubeDownloaderGUI


class TestBaseGUI(unittest.TestCase):
    """Test cases for BaseYouTubeDownloaderGUI class."""

    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.gui = BaseYouTubeDownloaderGUI(self.root, "Test GUI", "/tmp/test")

    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()

    def test_validate_url_valid_youtube(self):
        """Test URL validation with valid YouTube URL."""
        # Should not raise exception
        try:
            self.gui.validate_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        except ValueError:
            self.fail("validate_url raised ValueError unexpectedly")

    def test_validate_url_invalid(self):
        """Test URL validation with invalid URL."""
        with self.assertRaises(ValueError):
            self.gui.validate_url("not a url")

    def test_validate_url_non_youtube(self):
        """Test URL validation with non-YouTube URL."""
        with self.assertRaises(ValueError):
            self.gui.validate_url("https://www.google.com")


if __name__ == "__main__":
    unittest.main()
