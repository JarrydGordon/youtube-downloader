"""Shared pytest fixtures for YouTube Downloader tests."""

from typing import Any, Generator, Iterator
import pytest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch
import tempfile
import shutil
import io
import sys

# Mock tkinter if not available (for headless environments)
try:
    import tkinter as tk
except ImportError:
    # Create comprehensive tkinter mock
    tk = MagicMock()
    tk.Tk = MagicMock
    tk.TclError = type('TclError', (Exception,), {})
    tk.END = 'end'
    tk.X = 'x'
    tk.LEFT = 'left'
    tk.BooleanVar = MagicMock
    tk.DoubleVar = MagicMock
    tk.Entry = MagicMock

    # Mock ttk
    ttk = MagicMock()
    ttk.Style = MagicMock
    ttk.Frame = MagicMock
    ttk.Label = MagicMock
    ttk.Button = MagicMock
    ttk.Checkbutton = MagicMock
    ttk.Progressbar = MagicMock

    # Mock messagebox
    messagebox = MagicMock()
    messagebox.showinfo = MagicMock()
    messagebox.showerror = MagicMock()
    messagebox.showwarning = MagicMock()

    # Mock validators
    validators = MagicMock()
    validators.url = MagicMock(return_value=True)

    # Inject mocks into sys.modules
    sys.modules['tkinter'] = tk
    sys.modules['tkinter.ttk'] = ttk
    sys.modules['tkinter.messagebox'] = messagebox
    if 'validators' not in sys.modules:
        sys.modules['validators'] = validators


@pytest.fixture
def mock_tk_root() -> MagicMock:
    """Create a mock Tk root for testing without displaying windows."""
    root: MagicMock = MagicMock(spec=tk.Tk)
    root.clipboard_get = MagicMock(return_value="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    root.after = MagicMock(side_effect=lambda delay, func: func())
    root.update_idletasks = MagicMock()
    root.configure = MagicMock()
    root.title = MagicMock()
    root.geometry = MagicMock()
    return root


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_path: Path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup after test
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def mock_yt_dlp_success() -> MagicMock:
    """Mock successful yt-dlp download."""
    def mock_download_impl(urls: list[str]) -> None:
        """Simulate successful download."""
        return None

    mock_ydl: MagicMock = MagicMock()
    mock_ydl.download = MagicMock(side_effect=mock_download_impl)
    mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
    mock_ydl.__exit__ = MagicMock(return_value=None)

    return mock_ydl


@pytest.fixture
def mock_yt_dlp_error() -> MagicMock:
    """Mock yt-dlp download with error."""
    def mock_download_impl(urls: list[str]) -> None:
        """Simulate download error."""
        raise RuntimeError("Download failed: Video unavailable")

    mock_ydl: MagicMock = MagicMock()
    mock_ydl.download = MagicMock(side_effect=mock_download_impl)
    mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
    mock_ydl.__exit__ = MagicMock(return_value=None)

    return mock_ydl


@pytest.fixture
def mock_download_progress() -> dict[str, Any]:
    """Mock download progress data."""
    return {
        'status': 'downloading',
        'total_bytes': 10485760,  # 10 MB
        'downloaded_bytes': 5242880,  # 5 MB
        'speed': 1048576,  # 1 MB/s
        'eta': 5
    }


@pytest.fixture
def mock_download_finished() -> dict[str, int]:
    """Mock download finished data."""
    return {
        'status': 'finished',
        'total_bytes': 10485760,
        'downloaded_bytes': 10485760,
    }


@pytest.fixture
def valid_youtube_urls() -> list[str]:
    """Return list of valid YouTube URLs for testing."""
    return [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s",
    ]


@pytest.fixture
def valid_playlist_urls() -> list[str]:
    """Return list of valid YouTube playlist URLs."""
    return [
        "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
    ]


@pytest.fixture
def invalid_urls() -> list[str]:
    """Return list of invalid URLs for testing."""
    return [
        "not a url",
        "https://www.google.com",
        "http://example.com",
        "",
        "   ",
    ]


@pytest.fixture
def mock_config() -> Any:
    """Mock Config object with predefined paths."""
    from youtube_downloader.config import Config

    config: Config = Config()
    # Override paths for testing
    config.get_default_music_dir = MagicMock(return_value=Path("/tmp/test_music"))
    config.get_default_video_dir = MagicMock(return_value=Path("/tmp/test_videos"))
    config.get_ffmpeg_path = MagicMock(return_value="ffmpeg")

    return config


@pytest.fixture
def mock_messagebox() -> Generator[MagicMock, None, None]:
    """Mock tkinter messagebox."""
    with patch('youtube_downloader.base_gui.messagebox') as mock_mb:
        mock_mb.showinfo = MagicMock()
        mock_mb.showerror = MagicMock()
        mock_mb.showwarning = MagicMock()
        yield mock_mb


@pytest.fixture
def mock_threading() -> Generator[MagicMock, None, None]:
    """Mock threading to run synchronously in tests."""
    def mock_thread_run(target: Any = None, args: tuple[Any, ...] = (), daemon: bool = False) -> None:
        """Execute target immediately instead of in a thread."""
        if target:
            target(*args)

    with patch('threading.Thread') as mock_thread:
        mock_thread.return_value.start = MagicMock()
        mock_thread.side_effect = lambda target, args, daemon: type('Thread', (), {
            'start': lambda self: target(*args)
        })()
        yield mock_thread


@pytest.fixture
def mock_validators_valid() -> Generator[MagicMock, None, None]:
    """Mock validators to always return True."""
    with patch('youtube_downloader.base_gui.validators.url') as mock_val:
        mock_val.return_value = True
        yield mock_val


@pytest.fixture
def mock_validators_invalid() -> Generator[MagicMock, None, None]:
    """Mock validators to always return False."""
    with patch('youtube_downloader.base_gui.validators.url') as mock_val:
        mock_val.return_value = False
        yield mock_val


@pytest.fixture
def mock_path_exists_true() -> Generator[MagicMock, None, None]:
    """Mock Path.exists() to return True."""
    with patch('pathlib.Path.exists') as mock_exists:
        mock_exists.return_value = True
        yield mock_exists


@pytest.fixture
def mock_path_exists_false() -> Generator[MagicMock, None, None]:
    """Mock Path.exists() to return False."""
    with patch('pathlib.Path.exists') as mock_exists:
        mock_exists.return_value = False
        yield mock_exists


@pytest.fixture
def capture_logs(monkeypatch: pytest.MonkeyPatch) -> Generator[io.StringIO, None, None]:
    """Capture logging output for testing."""
    import logging

    log_capture: io.StringIO = io.StringIO()
    handler: logging.StreamHandler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.INFO)

    logger: logging.Logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    yield log_capture

    logger.removeHandler(handler)
