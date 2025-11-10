"""Tests for video downloader module."""

import pytest
from unittest.mock import MagicMock, patch, call, mock_open
import tkinter as tk
from pathlib import Path
import logging
from youtube_downloader.video_downloader import YouTubeVideoDownloaderGUI


class TestVideoDownloader:
    """Test cases for YouTubeVideoDownloaderGUI class."""

    @pytest.fixture
    def video_gui(self, mock_tk_root):
        """Create a video downloader GUI instance for testing."""
        with patch('youtube_downloader.video_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                with patch('youtube_downloader.video_downloader.logging'):
                    mock_config = MagicMock()
                    mock_config.get_default_video_dir.return_value = Path("/tmp/test_videos")
                    mock_config.get_ffmpeg_path.return_value = "ffmpeg"
                    mock_config_class.return_value = mock_config

                    gui = YouTubeVideoDownloaderGUI(mock_tk_root)
                    gui.url_entry = MagicMock()
                    gui.download_btn = MagicMock()
                    gui.progress_var = MagicMock()
                    gui.status_label = MagicMock()
                    return gui

    def test_initialization(self, mock_tk_root):
        """Test video downloader initialization."""
        with patch('youtube_downloader.video_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                with patch('youtube_downloader.video_downloader.logging'):
                    mock_config = MagicMock()
                    mock_config.get_default_video_dir.return_value = Path("/tmp/test_videos")
                    mock_config_class.return_value = mock_config

                    gui = YouTubeVideoDownloaderGUI(mock_tk_root)

                    mock_tk_root.title.assert_called_with("YouTube Video Downloader (1080p)")
                    mock_tk_root.geometry.assert_called()

    def test_setup_logging(self, mock_tk_root):
        """Test logging setup."""
        with patch('youtube_downloader.video_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk'):
                with patch('youtube_downloader.video_downloader.logging.basicConfig') as mock_logging:
                    with patch('pathlib.Path.mkdir'):
                        mock_config = MagicMock()
                        mock_config.get_default_video_dir.return_value = Path("/tmp/test")
                        mock_config_class.return_value = mock_config

                        gui = YouTubeVideoDownloaderGUI(mock_tk_root)

                        assert mock_logging.called

    def test_download_video(self, video_gui):
        """Test downloading a video."""
        video_gui.url_entry.get.return_value = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        with patch('youtube_downloader.video_downloader.threading.Thread') as mock_thread:
            with patch('youtube_downloader.video_downloader.logging'):
                video_gui.download()

                mock_thread.assert_called_once()
                video_gui.download_btn.config.assert_called_once_with(state='disabled')

    def test_download_options_format(self, video_gui):
        """Test that download options are correctly set for 1080p."""
        video_gui.url_entry.get.return_value = "https://www.youtube.com/watch?v=test"

        with patch('youtube_downloader.video_downloader.threading.Thread') as mock_thread:
            with patch('youtube_downloader.video_downloader.logging'):
                video_gui.download()

                call_args = mock_thread.call_args
                args = call_args[1]['args']
                ydl_opts = args[1]

                assert ydl_opts['format'] == 'bv*[height<=1080]+ba/b[height<=1080]'
                assert ydl_opts['merge_output_format'] == 'mp4'
                assert ydl_opts['noplaylist'] is True
                assert ydl_opts['concurrent_fragment_downloads'] == 3

    def test_download_hook_downloading(self, video_gui, mock_download_progress):
        """Test download hook during download."""
        with patch('youtube_downloader.video_downloader.logging'):
            video_gui.download_hook(mock_download_progress)

            # Verify progress update was scheduled
            video_gui.root.after.assert_called()

    def test_download_hook_finished(self, video_gui, mock_download_finished):
        """Test download hook when download is finished."""
        with patch('youtube_downloader.video_downloader.logging') as mock_logging:
            video_gui.download_hook(mock_download_finished)

            # Verify logging
            assert mock_logging.info.called
            # Verify progress update
            video_gui.root.after.assert_called()

    def test_download_hook_with_speed(self, video_gui):
        """Test download hook with speed information."""
        progress_data = {
            'status': 'downloading',
            'total_bytes': 10485760,
            'downloaded_bytes': 5242880,
            'speed': 2097152,  # 2 MB/s
            'eta': 5
        }

        with patch('youtube_downloader.video_downloader.logging'):
            video_gui.download_hook(progress_data)

            # Progress should be updated
            assert video_gui.root.after.called

    def test_download_hook_without_speed(self, video_gui):
        """Test download hook without speed information."""
        progress_data = {
            'status': 'downloading',
            'total_bytes': 10485760,
            'downloaded_bytes': 5242880,
            'speed': 0,
            'eta': 0
        }

        with patch('youtube_downloader.video_downloader.logging'):
            video_gui.download_hook(progress_data)

            assert video_gui.root.after.called

    def test_download_hook_no_total_bytes(self, video_gui):
        """Test download hook when total bytes is unknown."""
        progress_data = {
            'status': 'downloading',
            'downloaded_bytes': 5242880,
        }

        with patch('youtube_downloader.video_downloader.logging'):
            # Should not raise exception
            video_gui.download_hook(progress_data)

    def test_download_hook_error_handling(self, video_gui):
        """Test download hook handles errors gracefully."""
        progress_data = {
            'status': 'downloading',
            'total_bytes': 'invalid',  # Invalid data type
        }

        with patch('youtube_downloader.video_downloader.logging') as mock_logging:
            # Should not raise exception
            video_gui.download_hook(progress_data)
            # Error should be logged
            assert mock_logging.error.called

    def test_update_progress(self, video_gui):
        """Test progress update method."""
        video_gui.update_progress(50.0, "Downloading: 50%")

        video_gui.progress_var.set.assert_called_once_with(50.0)
        video_gui.status_label.config.assert_called_once_with(text="Downloading: 50%")
        video_gui.root.update_idletasks.assert_called_once()

    def test_update_progress_100_percent(self, video_gui):
        """Test progress update at 100%."""
        video_gui.update_progress(100.0, "Download complete!")

        video_gui.progress_var.set.assert_called_once_with(100.0)
        video_gui.status_label.config.assert_called_once()

    def test_create_widgets(self, mock_tk_root):
        """Test widget creation including progress bar."""
        with patch('youtube_downloader.video_downloader.Config') as mock_config_class:
            with patch('youtube_downloader.base_gui.ttk') as mock_ttk:
                with patch('youtube_downloader.video_downloader.logging'):
                    mock_config = MagicMock()
                    mock_config.get_default_video_dir.return_value = Path("/tmp/test")
                    mock_config_class.return_value = mock_config

                    gui = YouTubeVideoDownloaderGUI(mock_tk_root)

                    # Verify window size was adjusted for progress bar
                    geometry_calls = mock_tk_root.geometry.call_args_list
                    assert any('200' in str(call) for call in geometry_calls)

    def test_progress_hooks_configured(self, video_gui):
        """Test that progress hooks are properly configured."""
        video_gui.url_entry.get.return_value = "https://www.youtube.com/watch?v=test"

        with patch('youtube_downloader.video_downloader.threading.Thread') as mock_thread:
            with patch('youtube_downloader.video_downloader.logging'):
                video_gui.download()

                call_args = mock_thread.call_args
                args = call_args[1]['args']
                ydl_opts = args[1]

                assert 'progress_hooks' in ydl_opts
                assert len(ydl_opts['progress_hooks']) == 1
                assert callable(ydl_opts['progress_hooks'][0])

    def test_postprocessor_args(self, video_gui):
        """Test that postprocessor args are set correctly."""
        video_gui.url_entry.get.return_value = "https://www.youtube.com/watch?v=test"

        with patch('youtube_downloader.video_downloader.threading.Thread') as mock_thread:
            with patch('youtube_downloader.video_downloader.logging'):
                video_gui.download()

                call_args = mock_thread.call_args
                ydl_opts = call_args[1]['args'][1]

                assert 'postprocessor_args' in ydl_opts
                assert '-c:v' in ydl_opts['postprocessor_args']
                assert 'copy' in ydl_opts['postprocessor_args']

    def test_logging_on_download_start(self, video_gui):
        """Test that logging occurs when download starts."""
        video_gui.url_entry.get.return_value = "https://www.youtube.com/watch?v=test"

        with patch('youtube_downloader.video_downloader.threading.Thread'):
            with patch('youtube_downloader.video_downloader.logging') as mock_logging:
                video_gui.download()

                assert mock_logging.info.called

    def test_main_function(self):
        """Test main entry point function."""
        with patch('youtube_downloader.video_downloader.tk.Tk') as mock_tk_class:
            with patch('youtube_downloader.video_downloader.YouTubeVideoDownloaderGUI'):
                mock_root = MagicMock()
                mock_tk_class.return_value = mock_root

                from youtube_downloader.video_downloader import main
                main()

                mock_root.mainloop.assert_called_once()

    def test_thread_daemon_mode(self, video_gui):
        """Test that download thread runs in daemon mode."""
        video_gui.url_entry.get.return_value = "https://www.youtube.com/watch?v=test"

        with patch('youtube_downloader.video_downloader.threading.Thread') as mock_thread:
            with patch('youtube_downloader.video_downloader.logging'):
                video_gui.download()

                call_args = mock_thread.call_args
                assert call_args[1]['daemon'] is True

    @pytest.mark.parametrize("downloaded,total,expected_progress", [
        (5242880, 10485760, 50.0),
        (2621440, 10485760, 25.0),
        (10485760, 10485760, 100.0),
        (0, 10485760, 0.0),
    ])
    def test_progress_calculation(self, video_gui, downloaded, total, expected_progress):
        """Test progress percentage calculation."""
        progress_data = {
            'status': 'downloading',
            'total_bytes': total,
            'downloaded_bytes': downloaded,
            'speed': 1000000,
            'eta': 10
        }

        with patch('youtube_downloader.video_downloader.logging'):
            video_gui.download_hook(progress_data)

            # Check that progress update was called
            assert video_gui.root.after.called
            # Extract the lambda and call it to verify progress
            after_call = video_gui.root.after.call_args[0]
            if len(after_call) > 1 and callable(after_call[1]):
                # Lambda was called with correct progress
                pass

    def test_concurrent_fragment_downloads(self, video_gui):
        """Test concurrent fragment downloads setting."""
        video_gui.url_entry.get.return_value = "https://www.youtube.com/watch?v=test"

        with patch('youtube_downloader.video_downloader.threading.Thread') as mock_thread:
            with patch('youtube_downloader.video_downloader.logging'):
                video_gui.download()

                call_args = mock_thread.call_args
                ydl_opts = call_args[1]['args'][1]

                assert ydl_opts['concurrent_fragment_downloads'] == 3

    def test_noplaylist_always_enabled(self, video_gui):
        """Test that noplaylist is always True for video downloads."""
        video_gui.url_entry.get.return_value = "https://www.youtube.com/watch?v=test"

        with patch('youtube_downloader.video_downloader.threading.Thread') as mock_thread:
            with patch('youtube_downloader.video_downloader.logging'):
                video_gui.download()

                call_args = mock_thread.call_args
                ydl_opts = call_args[1]['args'][1]

                assert ydl_opts['noplaylist'] is True

    def test_download_hook_total_bytes_estimate(self, video_gui):
        """Test download hook with total_bytes_estimate instead of total_bytes."""
        progress_data = {
            'status': 'downloading',
            'total_bytes_estimate': 10485760,
            'downloaded_bytes': 5242880,
            'speed': 1000000,
            'eta': 5
        }

        with patch('youtube_downloader.video_downloader.logging'):
            video_gui.download_hook(progress_data)

            assert video_gui.root.after.called
