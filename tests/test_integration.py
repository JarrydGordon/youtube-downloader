"""Integration tests for complete workflows."""

import pytest
from unittest.mock import MagicMock, patch, mock_open
import tkinter as tk
from pathlib import Path
import threading
import time
from youtube_downloader.audio_downloader import YouTubeAudioDownloaderGUI
from youtube_downloader.video_downloader import YouTubeVideoDownloaderGUI
from youtube_downloader.config import Config


class TestAudioDownloadWorkflow:
    """Integration tests for audio download workflow."""

    @pytest.fixture
    def audio_app(self, mock_tk_root, temp_dir):
        """Create a complete audio downloader application."""
        with patch('youtube_downloader.audio_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                mock_config = MagicMock()
                mock_config.get_default_music_dir.return_value = temp_dir
                mock_config.get_ffmpeg_path.return_value = "ffmpeg"
                mock_config_class.return_value = mock_config

                app = YouTubeAudioDownloaderGUI(mock_tk_root)
                app.url_entry = MagicMock()
                app.download_btn = MagicMock()
                app.playlist_var = MagicMock()
                return app

    def test_complete_audio_download_workflow(self, audio_app, mock_yt_dlp_success, temp_dir):
        """Test complete audio download workflow from start to finish."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        audio_app.url_entry.get.return_value = url
        audio_app.playlist_var.get.return_value = False

        with patch('youtube_downloader.base_gui.yt_dlp.YoutubeDL', return_value=mock_yt_dlp_success):
            with patch('youtube_downloader.base_gui.messagebox') as mock_mb:
                with patch('pathlib.Path.exists', return_value=True):
                    # Start download
                    audio_app.download()

                    # Verify button was disabled
                    audio_app.download_btn.config.assert_called_with(state='disabled')

                    # Simulate download completion by calling worker directly
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '320',
                        }],
                        'noplaylist': True
                    }
                    audio_app.download_worker(url, ydl_opts)

                    # Verify download was called
                    mock_yt_dlp_success.download.assert_called_with([url])
                    # Verify success message
                    mock_mb.showinfo.assert_called_once()

    def test_audio_playlist_download_workflow(self, audio_app, mock_yt_dlp_success):
        """Test downloading a complete playlist."""
        url = "https://www.youtube.com/playlist?list=PLtest123"
        audio_app.url_entry.get.return_value = url
        audio_app.playlist_var.get.return_value = True

        with patch('youtube_downloader.base_gui.yt_dlp.YoutubeDL', return_value=mock_yt_dlp_success):
            with patch('youtube_downloader.base_gui.messagebox') as mock_mb:
                with patch('pathlib.Path.exists', return_value=True):
                    # Execute workflow
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '320',
                        }],
                        'noplaylist': False
                    }
                    audio_app.download_worker(url, ydl_opts)

                    mock_yt_dlp_success.download.assert_called_once()
                    mock_mb.showinfo.assert_called_once()


class TestVideoDownloadWorkflow:
    """Integration tests for video download workflow."""

    @pytest.fixture
    def video_app(self, mock_tk_root, temp_dir):
        """Create a complete video downloader application."""
        with patch('youtube_downloader.video_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                with patch('youtube_downloader.video_downloader.logging'):
                    mock_config = MagicMock()
                    mock_config.get_default_video_dir.return_value = temp_dir
                    mock_config.get_ffmpeg_path.return_value = "ffmpeg"
                    mock_config_class.return_value = mock_config

                    app = YouTubeVideoDownloaderGUI(mock_tk_root)
                    app.url_entry = MagicMock()
                    app.download_btn = MagicMock()
                    app.progress_var = MagicMock()
                    app.status_label = MagicMock()
                    return app

    def test_complete_video_download_workflow(self, video_app, mock_yt_dlp_success, temp_dir):
        """Test complete video download workflow with progress updates."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_app.url_entry.get.return_value = url

        with patch('youtube_downloader.base_gui.yt_dlp.YoutubeDL', return_value=mock_yt_dlp_success):
            with patch('youtube_downloader.base_gui.messagebox') as mock_mb:
                with patch('pathlib.Path.exists', return_value=True):
                    with patch('youtube_downloader.video_downloader.logging'):
                        # Start download
                        video_app.download()

                        # Verify button was disabled
                        video_app.download_btn.config.assert_called_with(state='disabled')

                        # Simulate download with progress
                        ydl_opts = {
                            'format': 'bv*[height<=1080]+ba/b[height<=1080]',
                            'noplaylist': True,
                            'merge_output_format': 'mp4',
                        }

                        # Simulate progress updates
                        progress_data = {
                            'status': 'downloading',
                            'total_bytes': 10485760,
                            'downloaded_bytes': 5242880,
                            'speed': 1048576,
                            'eta': 5
                        }
                        video_app.download_hook(progress_data)

                        # Simulate completion
                        finished_data = {'status': 'finished'}
                        video_app.download_hook(finished_data)

                        # Execute download
                        video_app.download_worker(url, ydl_opts)

                        # Verify download completed
                        mock_yt_dlp_success.download.assert_called_with([url])
                        mock_mb.showinfo.assert_called_once()


class TestConfigIntegration:
    """Integration tests for configuration across components."""

    def test_config_consistency_across_components(self):
        """Test that config provides consistent paths across components."""
        config = Config()

        music_dir = config.get_default_music_dir()
        video_dir = config.get_default_video_dir()
        ffmpeg_path = config.get_ffmpeg_path()

        # Verify paths are valid
        assert isinstance(music_dir, Path)
        assert isinstance(video_dir, Path)
        assert isinstance(ffmpeg_path, str)

        # Verify paths are under home directory
        assert str(music_dir).startswith(str(Path.home()))
        assert str(video_dir).startswith(str(Path.home()))

    def test_audio_and_video_use_different_dirs(self, mock_tk_root):
        """Test that audio and video use different output directories."""
        with patch('youtube_downloader.base_gui.ttk'):
            with patch('youtube_downloader.video_downloader.logging'):
                audio_app = YouTubeAudioDownloaderGUI(mock_tk_root)
                video_app = YouTubeVideoDownloaderGUI(mock_tk_root)

                # Directories should be different
                assert audio_app.output_dir != video_app.output_dir


class TestErrorRecoveryWorkflow:
    """Integration tests for error recovery scenarios."""

    @pytest.fixture
    def audio_app(self, mock_tk_root, temp_dir):
        """Create audio app for error testing."""
        with patch('youtube_downloader.audio_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                mock_config = MagicMock()
                mock_config.get_default_music_dir.return_value = temp_dir
                mock_config.get_ffmpeg_path.return_value = "ffmpeg"
                mock_config_class.return_value = mock_config

                app = YouTubeAudioDownloaderGUI(mock_tk_root)
                app.url_entry = MagicMock()
                app.download_btn = MagicMock()
                app.playlist_var = MagicMock()
                return app

    def test_download_failure_recovery(self, audio_app, mock_yt_dlp_error):
        """Test that app recovers gracefully from download failure."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        audio_app.url_entry.get.return_value = url
        audio_app.playlist_var.get.return_value = False

        with patch('youtube_downloader.base_gui.yt_dlp.YoutubeDL', return_value=mock_yt_dlp_error):
            with patch('youtube_downloader.base_gui.messagebox') as mock_mb:
                with patch('pathlib.Path.exists', return_value=True):
                    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True}
                    audio_app.download_worker(url, ydl_opts)

                    # Verify error message was shown
                    mock_mb.showerror.assert_called_once()
                    # Verify button was re-enabled
                    audio_app.download_btn.config.assert_called()

    def test_invalid_url_recovery(self, audio_app):
        """Test recovery from invalid URL."""
        audio_app.url_entry.get.return_value = "not a valid url"
        audio_app.download_btn = MagicMock()

        with patch('youtube_downloader.base_gui.messagebox') as mock_mb:
            ydl_opts = {'format': 'bestaudio/best'}
            audio_app.download_worker("not a valid url", ydl_opts)

            # Should show error and re-enable button
            mock_mb.showerror.assert_called_once()
            audio_app.download_btn.config.assert_called()


class TestThreadSafety:
    """Integration tests for thread safety."""

    @pytest.fixture
    def video_app(self, mock_tk_root, temp_dir):
        """Create video app for thread testing."""
        with patch('youtube_downloader.video_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                with patch('youtube_downloader.video_downloader.logging'):
                    mock_config = MagicMock()
                    mock_config.get_default_video_dir.return_value = temp_dir
                    mock_config.get_ffmpeg_path.return_value = "ffmpeg"
                    mock_config_class.return_value = mock_config

                    app = YouTubeVideoDownloaderGUI(mock_tk_root)
                    app.url_entry = MagicMock()
                    app.download_btn = MagicMock()
                    app.progress_var = MagicMock()
                    app.status_label = MagicMock()
                    return app

    def test_progress_updates_use_after(self, video_app):
        """Test that progress updates use root.after for thread safety."""
        progress_data = {
            'status': 'downloading',
            'total_bytes': 10485760,
            'downloaded_bytes': 5242880,
            'speed': 1048576,
            'eta': 5
        }

        with patch('youtube_downloader.video_downloader.logging'):
            video_app.download_hook(progress_data)

            # Verify root.after was called (thread-safe update)
            assert video_app.root.after.called

    def test_error_messages_use_after(self, video_app):
        """Test that error messages are scheduled via root.after."""
        with patch('youtube_downloader.base_gui.messagebox') as mock_mb:
            with patch('youtube_downloader.base_gui.yt_dlp.YoutubeDL') as mock_ydl:
                mock_ydl.return_value.__enter__.return_value.download.side_effect = Exception("Test error")

                ydl_opts = {'format': 'bestaudio'}
                video_app.download_worker("https://www.youtube.com/watch?v=test", ydl_opts)

                # Error should be shown via root.after
                assert video_app.root.after.called


class TestClipboardIntegration:
    """Integration tests for clipboard functionality."""

    @pytest.fixture
    def audio_app(self, mock_tk_root, temp_dir):
        """Create audio app with clipboard support."""
        with patch('youtube_downloader.audio_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                mock_config = MagicMock()
                mock_config.get_default_music_dir.return_value = temp_dir
                mock_config_class.return_value = mock_config

                app = YouTubeAudioDownloaderGUI(mock_tk_root)
                app.url_entry = MagicMock()
                app.download_btn = MagicMock()
                return app

    def test_paste_url_workflow(self, audio_app):
        """Test complete paste URL workflow."""
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        audio_app.root.clipboard_get.return_value = test_url

        # Paste URL
        audio_app.paste_url()

        # Verify entry was updated
        audio_app.url_entry.delete.assert_called_once()
        audio_app.url_entry.insert.assert_called_once_with(0, test_url)

    def test_paste_empty_clipboard(self, audio_app):
        """Test pasting with empty clipboard."""
        audio_app.root.clipboard_get.side_effect = tk.TclError("no selection")

        with patch('youtube_downloader.base_gui.messagebox') as mock_mb:
            audio_app.paste_url()

            # Should show warning
            mock_mb.showwarning.assert_called_once()


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_audio_app_full_lifecycle(self, mock_tk_root, temp_dir, mock_yt_dlp_success):
        """Test complete lifecycle of audio downloader."""
        with patch('youtube_downloader.audio_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                mock_config = MagicMock()
                mock_config.get_default_music_dir.return_value = temp_dir
                mock_config.get_ffmpeg_path.return_value = "ffmpeg"
                mock_config_class.return_value = mock_config

                # Create app
                app = YouTubeAudioDownloaderGUI(mock_tk_root)
                app.url_entry = MagicMock()
                app.download_btn = MagicMock()
                app.playlist_var = MagicMock()

                # Set URL
                url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                app.url_entry.get.return_value = url
                app.playlist_var.get.return_value = False

                # Download
                with patch('youtube_downloader.base_gui.yt_dlp.YoutubeDL', return_value=mock_yt_dlp_success):
                    with patch('youtube_downloader.base_gui.messagebox') as mock_mb:
                        with patch('pathlib.Path.exists', return_value=True):
                            ydl_opts = {
                                'format': 'bestaudio/best',
                                'postprocessors': [{
                                    'key': 'FFmpegExtractAudio',
                                    'preferredcodec': 'mp3',
                                    'preferredquality': '320',
                                }],
                                'noplaylist': True
                            }
                            app.download_worker(url, ydl_opts)

                            # Verify success
                            mock_yt_dlp_success.download.assert_called_once()
                            mock_mb.showinfo.assert_called_once()

    def test_video_app_full_lifecycle(self, mock_tk_root, temp_dir, mock_yt_dlp_success):
        """Test complete lifecycle of video downloader."""
        with patch('youtube_downloader.video_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                with patch('youtube_downloader.video_downloader.logging'):
                    mock_config = MagicMock()
                    mock_config.get_default_video_dir.return_value = temp_dir
                    mock_config.get_ffmpeg_path.return_value = "ffmpeg"
                    mock_config_class.return_value = mock_config

                    # Create app
                    app = YouTubeVideoDownloaderGUI(mock_tk_root)
                    app.url_entry = MagicMock()
                    app.download_btn = MagicMock()
                    app.progress_var = MagicMock()
                    app.status_label = MagicMock()

                    # Set URL and download
                    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                    app.url_entry.get.return_value = url

                    with patch('youtube_downloader.base_gui.yt_dlp.YoutubeDL', return_value=mock_yt_dlp_success):
                        with patch('youtube_downloader.base_gui.messagebox') as mock_mb:
                            with patch('pathlib.Path.exists', return_value=True):
                                ydl_opts = {
                                    'format': 'bv*[height<=1080]+ba/b[height<=1080]',
                                    'merge_output_format': 'mp4',
                                    'noplaylist': True,
                                }
                                app.download_worker(url, ydl_opts)

                                # Verify success
                                mock_yt_dlp_success.download.assert_called_once()
                                mock_mb.showinfo.assert_called_once()
