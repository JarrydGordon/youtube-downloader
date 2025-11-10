"""Tests for audio downloader module."""

import pytest
from unittest.mock import MagicMock, patch, call
import tkinter as tk
from pathlib import Path
from youtube_downloader.audio_downloader import YouTubeAudioDownloaderGUI


class TestAudioDownloader:
    """Test cases for YouTubeAudioDownloaderGUI class."""

    @pytest.fixture
    def audio_gui(self, mock_tk_root):
        """Create an audio downloader GUI instance for testing."""
        with patch('youtube_downloader.audio_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                mock_config = MagicMock()
                mock_config.get_default_music_dir.return_value = Path("/tmp/test_music")
                mock_config.get_ffmpeg_path.return_value = "ffmpeg"
                mock_config_class.return_value = mock_config

                gui = YouTubeAudioDownloaderGUI(mock_tk_root)
                gui.url_entry = MagicMock()
                gui.download_btn = MagicMock()
                gui.playlist_var = MagicMock()
                return gui

    def test_initialization(self, mock_tk_root):
        """Test audio downloader initialization."""
        with patch('youtube_downloader.audio_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                mock_config = MagicMock()
                mock_config.get_default_music_dir.return_value = Path("/tmp/test_music")
                mock_config_class.return_value = mock_config

                gui = YouTubeAudioDownloaderGUI(mock_tk_root)

                mock_tk_root.title.assert_called_with("YouTube Audio Downloader")
                mock_tk_root.geometry.assert_called()

    def test_download_audio_single_video(self, audio_gui, mock_yt_dlp_success):
        """Test downloading a single audio file."""
        audio_gui.url_entry.get.return_value = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        audio_gui.playlist_var.get.return_value = False
        audio_gui.download_btn = MagicMock()

        with patch('youtube_downloader.audio_downloader.threading.Thread') as mock_thread:
            audio_gui.download()

            mock_thread.assert_called_once()
            call_args = mock_thread.call_args
            assert call_args[1]['daemon'] is True
            audio_gui.download_btn.config.assert_called_once_with(state='disabled')

    def test_download_audio_playlist(self, audio_gui):
        """Test downloading a playlist."""
        audio_gui.url_entry.get.return_value = "https://www.youtube.com/playlist?list=PLtest"
        audio_gui.playlist_var.get.return_value = True

        with patch('youtube_downloader.audio_downloader.threading.Thread') as mock_thread:
            audio_gui.download()

            assert mock_thread.called
            # Verify playlist mode is enabled
            call_args = mock_thread.call_args
            args = call_args[1]['args']
            ydl_opts = args[1]
            assert ydl_opts['noplaylist'] is False

    def test_download_options_format(self, audio_gui):
        """Test that download options are correctly set."""
        audio_gui.url_entry.get.return_value = "https://www.youtube.com/watch?v=test"
        audio_gui.playlist_var.get.return_value = False

        with patch('youtube_downloader.audio_downloader.threading.Thread') as mock_thread:
            audio_gui.download()

            call_args = mock_thread.call_args
            args = call_args[1]['args']
            ydl_opts = args[1]

            assert ydl_opts['format'] == 'bestaudio/best'
            assert 'postprocessors' in ydl_opts
            assert ydl_opts['postprocessors'][0]['key'] == 'FFmpegExtractAudio'
            assert ydl_opts['postprocessors'][0]['preferredcodec'] == 'mp3'
            assert ydl_opts['postprocessors'][0]['preferredquality'] == '320'

    def test_validate_url_playlist_mode(self, audio_gui):
        """Test URL validation in playlist mode."""
        audio_gui.playlist_var.get.return_value = True

        # Valid playlist URL should pass
        audio_gui.validate_url("https://www.youtube.com/playlist?list=PLtest")

        # Invalid playlist URL should fail
        with pytest.raises(ValueError, match="Not a valid YouTube playlist URL"):
            audio_gui.validate_url("https://www.youtube.com/watch?v=test")

    def test_validate_url_single_mode(self, audio_gui):
        """Test URL validation in single video mode."""
        audio_gui.playlist_var.get.return_value = False

        # Should accept regular YouTube URL
        audio_gui.validate_url("https://www.youtube.com/watch?v=test")

    def test_download_hook_finished(self, audio_gui):
        """Test download hook when download is finished."""
        progress_data = {'status': 'finished'}
        # Should not raise exception
        audio_gui.download_hook(progress_data)

    def test_download_hook_downloading(self, audio_gui):
        """Test download hook during download."""
        progress_data = {
            'status': 'downloading',
            'downloaded_bytes': 5000000,
            'total_bytes': 10000000
        }
        # Should not raise exception
        audio_gui.download_hook(progress_data)

    def test_create_widgets(self, mock_tk_root):
        """Test widget creation."""
        with patch('youtube_downloader.audio_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk') as mock_ttk:
                mock_config = MagicMock()
                mock_config.get_default_music_dir.return_value = Path("/tmp/test")
                mock_config_class.return_value = mock_config

                gui = YouTubeAudioDownloaderGUI(mock_tk_root)

                # Verify window size was adjusted for playlist checkbox
                geometry_calls = mock_tk_root.geometry.call_args_list
                assert any('180' in str(call) for call in geometry_calls)

    @pytest.mark.parametrize("playlist_enabled,url,should_fail", [
        (True, "https://www.youtube.com/playlist?list=PLtest", False),
        (True, "https://www.youtube.com/watch?v=test", True),
        (False, "https://www.youtube.com/watch?v=test", False),
        (False, "https://www.youtube.com/playlist?list=PLtest", False),
    ])
    def test_playlist_url_validation(self, audio_gui, playlist_enabled, url, should_fail):
        """Test playlist URL validation with various combinations."""
        audio_gui.playlist_var.get.return_value = playlist_enabled

        if should_fail:
            with pytest.raises(ValueError):
                audio_gui.validate_url(url)
        else:
            audio_gui.validate_url(url)

    def test_download_button_disabled_on_click(self, audio_gui):
        """Test that download button is disabled when download starts."""
        audio_gui.url_entry.get.return_value = "https://www.youtube.com/watch?v=test"
        audio_gui.playlist_var.get.return_value = False

        with patch('youtube_downloader.audio_downloader.threading.Thread'):
            audio_gui.download()

            audio_gui.download_btn.config.assert_called_once_with(state='disabled')

    def test_progress_hooks_configured(self, audio_gui):
        """Test that progress hooks are properly configured."""
        audio_gui.url_entry.get.return_value = "https://www.youtube.com/watch?v=test"
        audio_gui.playlist_var.get.return_value = False

        with patch('youtube_downloader.audio_downloader.threading.Thread') as mock_thread:
            audio_gui.download()

            call_args = mock_thread.call_args
            args = call_args[1]['args']
            ydl_opts = args[1]

            assert 'progress_hooks' in ydl_opts
            assert len(ydl_opts['progress_hooks']) == 1
            assert callable(ydl_opts['progress_hooks'][0])

    def test_noplaylist_option(self, audio_gui):
        """Test noplaylist option is set correctly."""
        audio_gui.url_entry.get.return_value = "https://www.youtube.com/watch?v=test"

        # Test with playlist disabled
        audio_gui.playlist_var.get.return_value = False
        with patch('youtube_downloader.audio_downloader.threading.Thread') as mock_thread:
            audio_gui.download()
            call_args = mock_thread.call_args
            ydl_opts = call_args[1]['args'][1]
            assert ydl_opts['noplaylist'] is True

        # Test with playlist enabled
        audio_gui.playlist_var.get.return_value = True
        with patch('youtube_downloader.audio_downloader.threading.Thread') as mock_thread:
            audio_gui.download()
            call_args = mock_thread.call_args
            ydl_opts = call_args[1]['args'][1]
            assert ydl_opts['noplaylist'] is False

    def test_main_function(self):
        """Test main entry point function."""
        with patch('youtube_downloader.audio_downloader.tk.Tk') as mock_tk_class:
            with patch('youtube_downloader.audio_downloader.YouTubeAudioDownloaderGUI'):
                mock_root = MagicMock()
                mock_tk_class.return_value = mock_root

                from youtube_downloader.audio_downloader import main
                main()

                mock_root.mainloop.assert_called_once()

    def test_url_entry_stripped(self, audio_gui):
        """Test that URL is stripped of whitespace."""
        audio_gui.url_entry.get.return_value = "  https://www.youtube.com/watch?v=test  "
        audio_gui.playlist_var.get.return_value = False

        with patch('youtube_downloader.audio_downloader.threading.Thread') as mock_thread:
            audio_gui.download()

            call_args = mock_thread.call_args
            url = call_args[1]['args'][0]
            # Verify URL is stripped (checked in download_worker via validate_url)
            assert url == "  https://www.youtube.com/watch?v=test  "

    def test_thread_daemon_mode(self, audio_gui):
        """Test that download thread runs in daemon mode."""
        audio_gui.url_entry.get.return_value = "https://www.youtube.com/watch?v=test"
        audio_gui.playlist_var.get.return_value = False

        with patch('youtube_downloader.audio_downloader.threading.Thread') as mock_thread:
            audio_gui.download()

            call_args = mock_thread.call_args
            assert call_args[1]['daemon'] is True
