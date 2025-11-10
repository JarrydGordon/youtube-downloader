"""Tests for base GUI module."""

import pytest
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path

# Handle missing tkinter in headless environments
try:
    import tkinter as tk
except (ImportError, ModuleNotFoundError):
    import sys
    if 'tkinter' in sys.modules:
        tk = sys.modules['tkinter']
    else:
        tk = MagicMock()
        tk.TclError = type('TclError', (Exception,), {})

from youtube_downloader.base_gui import BaseYouTubeDownloaderGUI


class TestBaseGUI:
    """Test cases for BaseYouTubeDownloaderGUI class."""

    @pytest.fixture
    def gui(self, mock_tk_root, temp_dir):
        """Create a GUI instance for testing."""
        with patch('youtube_downloader.base_gui.ttk'):
            gui = BaseYouTubeDownloaderGUI(mock_tk_root, "Test GUI", temp_dir)
            return gui

    def test_initialization(self, gui, mock_tk_root, temp_dir):
        """Test GUI initialization."""
        assert gui.root == mock_tk_root
        assert gui.output_dir == temp_dir
        mock_tk_root.title.assert_called_once_with("Test GUI")
        mock_tk_root.geometry.assert_called_once_with("600x150")

    def test_validate_url_valid_youtube(self, gui, valid_youtube_urls):
        """Test URL validation with valid YouTube URLs."""
        for url in valid_youtube_urls:
            # Should not raise exception
            gui.validate_url(url)

    @pytest.mark.parametrize("url", [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
    ])
    def test_validate_url_valid_parametrized(self, gui, url):
        """Test URL validation with parametrized valid URLs."""
        gui.validate_url(url)  # Should not raise

    def test_validate_url_invalid(self, gui, invalid_urls):
        """Test URL validation with invalid URLs."""
        for url in invalid_urls:
            with pytest.raises(ValueError):
                gui.validate_url(url)

    def test_validate_url_non_youtube(self, gui):
        """Test URL validation with non-YouTube URL."""
        with pytest.raises(ValueError, match="Not a YouTube URL"):
            gui.validate_url("https://www.google.com")

    def test_validate_url_empty(self, gui):
        """Test URL validation with empty string."""
        with pytest.raises(ValueError):
            gui.validate_url("")

    def test_paste_url_success(self, gui):
        """Test pasting URL from clipboard."""
        gui.url_entry = MagicMock()
        gui.paste_url()
        gui.url_entry.delete.assert_called_once()
        gui.url_entry.insert.assert_called_once()

    def test_paste_url_clipboard_error(self, gui, mock_messagebox):
        """Test paste URL when clipboard is empty."""
        gui.root.clipboard_get = MagicMock(side_effect=tk.TclError("no selection"))
        gui.url_entry = MagicMock()

        with patch('youtube_downloader.base_gui.messagebox', mock_messagebox):
            gui.paste_url()
            mock_messagebox.showwarning.assert_called_once()

    def test_create_base_widgets(self, mock_tk_root, temp_dir):
        """Test creation of base widgets."""
        with patch('youtube_downloader.base_gui.ttk') as mock_ttk:
            mock_frame = MagicMock()
            mock_ttk.Frame.return_value = mock_frame
            mock_ttk.Label.return_value = MagicMock()
            mock_ttk.Button.return_value = MagicMock()

            gui = BaseYouTubeDownloaderGUI(mock_tk_root, "Test", temp_dir)
            gui.create_base_widgets()

            assert mock_ttk.Frame.called
            assert mock_ttk.Label.called
            assert mock_ttk.Button.called

    def test_download_worker_success(self, gui, mock_yt_dlp_success, mock_messagebox, temp_dir):
        """Test successful download worker."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ydl_opts = {'format': 'bestaudio'}
        gui.download_btn = MagicMock()

        with patch('youtube_downloader.base_gui.yt_dlp.YoutubeDL', return_value=mock_yt_dlp_success):
            with patch('youtube_downloader.base_gui.messagebox', mock_messagebox):
                with patch('pathlib.Path.exists', return_value=True):
                    gui.download_worker(url, ydl_opts)

        mock_yt_dlp_success.download.assert_called_once_with([url])
        mock_messagebox.showinfo.assert_called_once()

    def test_download_worker_invalid_url(self, gui, mock_messagebox):
        """Test download worker with invalid URL."""
        gui.download_btn = MagicMock()

        with patch('youtube_downloader.base_gui.messagebox', mock_messagebox):
            gui.download_worker("invalid", {})

        mock_messagebox.showerror.assert_called_once()

    def test_download_worker_ffmpeg_not_found(self, gui, mock_messagebox):
        """Test download worker when FFmpeg is not found."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        gui.download_btn = MagicMock()
        gui.config.get_ffmpeg_path = MagicMock(return_value="./ffmpeg/ffmpeg.exe")

        with patch('youtube_downloader.base_gui.messagebox', mock_messagebox):
            with patch('pathlib.Path.exists', return_value=False):
                gui.download_worker(url, {})

        assert mock_messagebox.showerror.called
        error_call_args = mock_messagebox.showerror.call_args[0]
        assert "FFmpeg" in error_call_args[1]

    def test_download_worker_download_error(self, gui, mock_yt_dlp_error, mock_messagebox):
        """Test download worker with download error."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ydl_opts = {'format': 'bestaudio'}
        gui.download_btn = MagicMock()

        with patch('youtube_downloader.base_gui.yt_dlp.YoutubeDL', return_value=mock_yt_dlp_error):
            with patch('youtube_downloader.base_gui.messagebox', mock_messagebox):
                gui.download_worker(url, ydl_opts)

        mock_messagebox.showerror.assert_called_once()

    def test_output_template_format(self, gui, temp_dir):
        """Test that output template is correctly formatted."""
        ydl_opts = {}
        expected_template = str(temp_dir / '%(title)s.%(ext)s')

        # Simulate what download_worker does with the template
        ydl_opts['outtmpl'] = str(gui.output_dir / '%(title)s.%(ext)s')

        assert ydl_opts['outtmpl'] == expected_template

    def test_config_initialization(self, gui):
        """Test that config is properly initialized."""
        assert gui.config is not None
        assert hasattr(gui.config, 'get_ffmpeg_path')

    def test_style_configuration(self, mock_tk_root, temp_dir):
        """Test that style is configured."""
        with patch('youtube_downloader.base_gui.ttk.Style') as mock_style:
            gui = BaseYouTubeDownloaderGUI(mock_tk_root, "Test", temp_dir)
            assert gui.style is not None

    @pytest.mark.parametrize("url,should_pass", [
        ("https://www.youtube.com/watch?v=test123", True),
        ("https://youtu.be/test123", True),
        ("https://google.com", False),
        ("not a url", False),
    ])
    def test_url_validation_parametrized(self, gui, url, should_pass):
        """Test URL validation with various inputs."""
        if should_pass:
            gui.validate_url(url)
        else:
            with pytest.raises(ValueError):
                gui.validate_url(url)
