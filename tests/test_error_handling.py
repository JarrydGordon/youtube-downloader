"""Tests for error handling and edge cases."""

import pytest
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path
import sys

# Handle missing tkinter in headless environments
try:
    import tkinter as tk
except (ImportError, ModuleNotFoundError):
    if 'tkinter' in sys.modules:
        tk = sys.modules['tkinter']
    else:
        tk = MagicMock()
        tk.TclError = type('TclError', (Exception,), {})

from youtube_downloader.base_gui import BaseYouTubeDownloaderGUI
from youtube_downloader.audio_downloader import YouTubeAudioDownloaderGUI
from youtube_downloader.video_downloader import YouTubeVideoDownloaderGUI
from youtube_downloader.config import Config


class TestURLValidationErrors:
    """Test URL validation error scenarios."""

    @pytest.fixture
    def base_gui(self, mock_tk_root, temp_dir):
        """Create base GUI for testing."""
        with patch('youtube_downloader.base_gui.ttk'):
            gui = BaseYouTubeDownloaderGUI(mock_tk_root, "Test", temp_dir)
            return gui

    @pytest.mark.parametrize("invalid_url,error_message", [
        ("", "Please enter a valid YouTube URL"),
        ("   ", "Please enter a valid YouTube URL"),
        ("not a url", "Please enter a valid YouTube URL"),
        ("https://google.com", "Not a YouTube URL"),
        ("http://example.com", "Not a YouTube URL"),
        ("ftp://youtube.com", "Please enter a valid YouTube URL"),
    ])
    def test_invalid_url_errors(self, base_gui, invalid_url, error_message):
        """Test various invalid URL formats."""
        with pytest.raises(ValueError) as exc_info:
            base_gui.validate_url(invalid_url)
        assert error_message in str(exc_info.value)

    def test_none_url(self, base_gui):
        """Test None URL handling."""
        with pytest.raises(ValueError):
            base_gui.validate_url(None)

    def test_special_characters_in_url(self, base_gui):
        """Test URL with special characters."""
        # Valid YouTube URL with special characters should pass
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=youtu.be"
        base_gui.validate_url(url)  # Should not raise

    def test_url_with_newlines(self, base_gui):
        """Test URL with newline characters."""
        url = "https://www.youtube.com/watch?v=test\n"
        # Should be handled by strip() in actual usage
        base_gui.validate_url(url.strip())

    def test_youtube_short_url(self, base_gui):
        """Test YouTube short URL format."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        base_gui.validate_url(url)  # Should not raise


class TestDownloadErrors:
    """Test download error scenarios."""

    @pytest.fixture
    def audio_gui(self, mock_tk_root, temp_dir):
        """Create audio GUI for error testing."""
        with patch('youtube_downloader.audio_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                mock_config = MagicMock()
                mock_config.get_default_music_dir.return_value = temp_dir
                mock_config.get_ffmpeg_path.return_value = "ffmpeg"
                mock_config_class.return_value = mock_config

                gui = YouTubeAudioDownloaderGUI(mock_tk_root)
                gui.url_entry = MagicMock()
                gui.download_btn = MagicMock()
                gui.playlist_var = MagicMock()
                return gui

    def test_network_error(self, audio_gui, mock_messagebox):
        """Test handling of network errors."""
        url = "https://www.youtube.com/watch?v=test"
        audio_gui.download_btn = MagicMock()

        with patch('youtube_downloader.base_gui.yt_dlp.YoutubeDL') as mock_ydl:
            mock_ydl.return_value.__enter__.return_value.download.side_effect = \
                RuntimeError("Unable to download: Network error")

            with patch('youtube_downloader.base_gui.messagebox', mock_messagebox):
                ydl_opts = {}
                audio_gui.download_worker(url, ydl_opts)

                # Should show error message
                mock_messagebox.showerror.assert_called_once()
                error_args = mock_messagebox.showerror.call_args[0]
                assert "Network error" in error_args[1]

    def test_video_unavailable_error(self, audio_gui, mock_messagebox):
        """Test handling when video is unavailable."""
        url = "https://www.youtube.com/watch?v=test"
        audio_gui.download_btn = MagicMock()

        with patch('youtube_downloader.base_gui.yt_dlp.YoutubeDL') as mock_ydl:
            mock_ydl.return_value.__enter__.return_value.download.side_effect = \
                RuntimeError("Video unavailable")

            with patch('youtube_downloader.base_gui.messagebox', mock_messagebox):
                ydl_opts = {}
                audio_gui.download_worker(url, ydl_opts)

                mock_messagebox.showerror.assert_called_once()

    def test_ffmpeg_missing_error(self, audio_gui, mock_messagebox):
        """Test handling when FFmpeg is missing."""
        url = "https://www.youtube.com/watch?v=test"
        audio_gui.download_btn = MagicMock()
        audio_gui.config.get_ffmpeg_path = MagicMock(return_value="./ffmpeg/ffmpeg.exe")

        with patch('youtube_downloader.base_gui.messagebox', mock_messagebox):
            with patch('pathlib.Path.exists', return_value=False):
                ydl_opts = {}
                audio_gui.download_worker(url, ydl_opts)

                mock_messagebox.showerror.assert_called_once()
                error_args = mock_messagebox.showerror.call_args[0]
                assert "FFmpeg" in error_args[1]

    def test_disk_space_error(self, audio_gui, mock_messagebox):
        """Test handling of disk space errors."""
        url = "https://www.youtube.com/watch?v=test"
        audio_gui.download_btn = MagicMock()

        with patch('youtube_downloader.base_gui.yt_dlp.YoutubeDL') as mock_ydl:
            mock_ydl.return_value.__enter__.return_value.download.side_effect = \
                OSError("No space left on device")

            with patch('youtube_downloader.base_gui.messagebox', mock_messagebox):
                with patch('pathlib.Path.exists', return_value=True):
                    ydl_opts = {}
                    audio_gui.download_worker(url, ydl_opts)

                    mock_messagebox.showerror.assert_called_once()

    def test_permission_error(self, audio_gui, mock_messagebox):
        """Test handling of permission errors."""
        url = "https://www.youtube.com/watch?v=test"
        audio_gui.download_btn = MagicMock()

        with patch('youtube_downloader.base_gui.yt_dlp.YoutubeDL') as mock_ydl:
            mock_ydl.return_value.__enter__.return_value.download.side_effect = \
                PermissionError("Permission denied")

            with patch('youtube_downloader.base_gui.messagebox', mock_messagebox):
                with patch('pathlib.Path.exists', return_value=True):
                    ydl_opts = {}
                    audio_gui.download_worker(url, ydl_opts)

                    mock_messagebox.showerror.assert_called_once()


class TestPlaylistErrors:
    """Test playlist-specific error scenarios."""

    @pytest.fixture
    def audio_gui(self, mock_tk_root, temp_dir):
        """Create audio GUI for playlist testing."""
        with patch('youtube_downloader.audio_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                mock_config = MagicMock()
                mock_config.get_default_music_dir.return_value = temp_dir
                mock_config_class.return_value = mock_config

                gui = YouTubeAudioDownloaderGUI(mock_tk_root)
                gui.url_entry = MagicMock()
                gui.download_btn = MagicMock()
                gui.playlist_var = MagicMock()
                return gui

    def test_playlist_url_without_playlist_mode(self, audio_gui):
        """Test playlist URL when playlist mode is disabled."""
        audio_gui.playlist_var.get.return_value = False
        url = "https://www.youtube.com/playlist?list=PLtest"

        # Should not raise - playlist mode disabled means it's OK
        audio_gui.validate_url(url)

    def test_single_video_url_with_playlist_mode(self, audio_gui):
        """Test single video URL when playlist mode is enabled."""
        audio_gui.playlist_var.get.return_value = True
        url = "https://www.youtube.com/watch?v=test"

        with pytest.raises(ValueError, match="Not a valid YouTube playlist URL"):
            audio_gui.validate_url(url)

    def test_invalid_playlist_url(self, audio_gui):
        """Test invalid playlist URL format."""
        audio_gui.playlist_var.get.return_value = True
        url = "https://www.youtube.com/playlist?id=invalid"

        with pytest.raises(ValueError):
            audio_gui.validate_url(url)


class TestClipboardErrors:
    """Test clipboard-related errors."""

    @pytest.fixture
    def base_gui(self, mock_tk_root, temp_dir):
        """Create base GUI for clipboard testing."""
        with patch('youtube_downloader.base_gui.ttk'):
            gui = BaseYouTubeDownloaderGUI(mock_tk_root, "Test", temp_dir)
            gui.url_entry = MagicMock()
            return gui

    def test_empty_clipboard(self, base_gui, mock_messagebox):
        """Test pasting from empty clipboard."""
        base_gui.root.clipboard_get = MagicMock(side_effect=tk.TclError("no selection"))

        with patch('youtube_downloader.base_gui.messagebox', mock_messagebox):
            base_gui.paste_url()

            mock_messagebox.showwarning.assert_called_once()

    def test_clipboard_access_denied(self, base_gui, mock_messagebox):
        """Test clipboard access denied."""
        base_gui.root.clipboard_get = MagicMock(side_effect=tk.TclError("access denied"))

        with patch('youtube_downloader.base_gui.messagebox', mock_messagebox):
            base_gui.paste_url()

            mock_messagebox.showwarning.assert_called_once()


class TestProgressUpdateErrors:
    """Test progress update error scenarios."""

    @pytest.fixture
    def video_gui(self, mock_tk_root, temp_dir):
        """Create video GUI for progress testing."""
        with patch('youtube_downloader.video_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                with patch('youtube_downloader.video_downloader.logging'):
                    mock_config = MagicMock()
                    mock_config.get_default_video_dir.return_value = temp_dir
                    mock_config_class.return_value = mock_config

                    gui = YouTubeVideoDownloaderGUI(mock_tk_root)
                    gui.url_entry = MagicMock()
                    gui.download_btn = MagicMock()
                    gui.progress_var = MagicMock()
                    gui.status_label = MagicMock()
                    return gui

    def test_progress_with_invalid_data_types(self, video_gui):
        """Test progress hook with invalid data types."""
        progress_data = {
            'status': 'downloading',
            'total_bytes': 'invalid',  # Should be int
            'downloaded_bytes': 'invalid',  # Should be int
        }

        with patch('youtube_downloader.video_downloader.logging') as mock_logging:
            # Should not crash
            video_gui.download_hook(progress_data)
            # Should log error
            assert mock_logging.error.called

    def test_progress_with_missing_fields(self, video_gui):
        """Test progress hook with missing fields."""
        progress_data = {
            'status': 'downloading',
            # Missing total_bytes and downloaded_bytes
        }

        with patch('youtube_downloader.video_downloader.logging'):
            # Should not crash
            video_gui.download_hook(progress_data)

    def test_progress_with_zero_total_bytes(self, video_gui):
        """Test progress calculation with zero total bytes."""
        progress_data = {
            'status': 'downloading',
            'total_bytes': 0,
            'downloaded_bytes': 1000,
        }

        with patch('youtube_downloader.video_downloader.logging'):
            # Should not crash (division by zero)
            video_gui.download_hook(progress_data)

    def test_progress_with_negative_values(self, video_gui):
        """Test progress with negative values."""
        progress_data = {
            'status': 'downloading',
            'total_bytes': -1000,
            'downloaded_bytes': -500,
        }

        with patch('youtube_downloader.video_downloader.logging'):
            # Should not crash
            video_gui.download_hook(progress_data)

    def test_progress_hook_unknown_status(self, video_gui):
        """Test progress hook with unknown status."""
        progress_data = {
            'status': 'unknown_status',
        }

        with patch('youtube_downloader.video_downloader.logging'):
            # Should not crash
            video_gui.download_hook(progress_data)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def config(self):
        """Create config for edge case testing."""
        return Config()

    def test_very_long_url(self):
        """Test handling of very long URLs."""
        with patch('youtube_downloader.base_gui.ttk'):
            gui = BaseYouTubeDownloaderGUI(
                MagicMock(spec=tk.Tk),
                "Test",
                Path("/tmp")
            )
            # Create a very long but valid URL
            long_url = "https://www.youtube.com/watch?v=" + "a" * 1000
            # Should not crash even with long URL
            try:
                gui.validate_url(long_url)
            except ValueError:
                pass  # Expected if validator rejects it

    def test_url_with_unicode_characters(self):
        """Test URL with unicode characters."""
        with patch('youtube_downloader.base_gui.ttk'):
            gui = BaseYouTubeDownloaderGUI(
                MagicMock(spec=tk.Tk),
                "Test",
                Path("/tmp")
            )
            url = "https://www.youtube.com/watch?v=test&title=测试"
            # Should handle unicode gracefully
            try:
                gui.validate_url(url)
            except ValueError:
                pass

    def test_concurrent_downloads_attempt(self, mock_tk_root, temp_dir):
        """Test attempting multiple downloads simultaneously."""
        with patch('youtube_downloader.audio_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                mock_config = MagicMock()
                mock_config.get_default_music_dir.return_value = temp_dir
                mock_config_class.return_value = mock_config

                gui = YouTubeAudioDownloaderGUI(mock_tk_root)
                gui.url_entry = MagicMock()
                gui.download_btn = MagicMock()
                gui.playlist_var = MagicMock()

                gui.url_entry.get.return_value = "https://www.youtube.com/watch?v=test"
                gui.playlist_var.get.return_value = False

                # First download
                with patch('youtube_downloader.audio_downloader.threading.Thread'):
                    gui.download()
                    first_call = gui.download_btn.config.call_args_list[0]

                    # Second download attempt
                    gui.download()
                    second_call = gui.download_btn.config.call_args_list[1]

                    # Both should disable button
                    assert first_call == second_call

    def test_output_directory_with_spaces(self, mock_tk_root):
        """Test output directory path with spaces."""
        with patch('youtube_downloader.base_gui.ttk'):
            output_dir = Path("/tmp/test dir with spaces")
            gui = BaseYouTubeDownloaderGUI(mock_tk_root, "Test", output_dir)

            assert gui.output_dir == output_dir

    def test_output_directory_special_chars(self, mock_tk_root):
        """Test output directory with special characters."""
        with patch('youtube_downloader.base_gui.ttk'):
            output_dir = Path("/tmp/test-dir_123")
            gui = BaseYouTubeDownloaderGUI(mock_tk_root, "Test", output_dir)

            assert gui.output_dir == output_dir

    @pytest.mark.parametrize("platform_name", ["Windows", "Darwin", "Linux", "FreeBSD"])
    def test_config_on_different_platforms(self, platform_name):
        """Test config behavior on different platforms."""
        with patch('platform.system', return_value=platform_name):
            config = Config()
            music_dir = config.get_default_music_dir()
            video_dir = config.get_default_video_dir()
            ffmpeg_path = config.get_ffmpeg_path()

            assert isinstance(music_dir, Path)
            assert isinstance(video_dir, Path)
            assert isinstance(ffmpeg_path, str)

    def test_empty_url_entry(self, mock_tk_root, temp_dir):
        """Test download with empty URL entry."""
        with patch('youtube_downloader.audio_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                mock_config = MagicMock()
                mock_config.get_default_music_dir.return_value = temp_dir
                mock_config_class.return_value = mock_config

                gui = YouTubeAudioDownloaderGUI(mock_tk_root)
                gui.url_entry = MagicMock()
                gui.download_btn = MagicMock()
                gui.playlist_var = MagicMock()

                gui.url_entry.get.return_value = ""

                with patch('youtube_downloader.base_gui.messagebox') as mock_mb:
                    ydl_opts = {}
                    gui.download_worker("", ydl_opts)

                    # Should show error
                    mock_mb.showerror.assert_called_once()

    def test_whitespace_only_url(self, mock_tk_root, temp_dir):
        """Test download with whitespace-only URL."""
        with patch('youtube_downloader.audio_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                mock_config = MagicMock()
                mock_config.get_default_music_dir.return_value = temp_dir
                mock_config_class.return_value = mock_config

                gui = YouTubeAudioDownloaderGUI(mock_tk_root)
                gui.url_entry = MagicMock()
                gui.download_btn = MagicMock()

                with patch('youtube_downloader.base_gui.messagebox') as mock_mb:
                    ydl_opts = {}
                    gui.download_worker("   ", ydl_opts)

                    # Should show error
                    mock_mb.showerror.assert_called_once()


class TestButtonStateManagement:
    """Test button state management during errors."""

    @pytest.fixture
    def audio_gui(self, mock_tk_root, temp_dir):
        """Create audio GUI for button state testing."""
        with patch('youtube_downloader.audio_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                mock_config = MagicMock()
                mock_config.get_default_music_dir.return_value = temp_dir
                mock_config.get_ffmpeg_path.return_value = "ffmpeg"
                mock_config_class.return_value = mock_config

                gui = YouTubeAudioDownloaderGUI(mock_tk_root)
                gui.url_entry = MagicMock()
                gui.download_btn = MagicMock()
                gui.playlist_var = MagicMock()
                return gui

    def test_button_re_enabled_after_error(self, audio_gui):
        """Test that button is re-enabled after download error."""
        url = "https://www.youtube.com/watch?v=test"

        with patch('youtube_downloader.base_gui.yt_dlp.YoutubeDL') as mock_ydl:
            mock_ydl.return_value.__enter__.return_value.download.side_effect = \
                RuntimeError("Download failed")

            with patch('youtube_downloader.base_gui.messagebox'):
                with patch('pathlib.Path.exists', return_value=True):
                    ydl_opts = {}
                    audio_gui.download_worker(url, ydl_opts)

                    # Button should be re-enabled via root.after
                    assert audio_gui.root.after.called

    def test_button_re_enabled_after_validation_error(self, audio_gui):
        """Test that button is re-enabled after validation error."""
        with patch('youtube_downloader.base_gui.messagebox'):
            ydl_opts = {}
            audio_gui.download_worker("invalid url", ydl_opts)

            # Button should be re-enabled
            assert audio_gui.root.after.called
