"""Video downloader GUI for YouTube."""

from typing import Any, Dict, List
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
from datetime import datetime
from pathlib import Path
import re

from .base_gui import BaseYouTubeDownloaderGUI
from .config import Config
from .constants import (
    WINDOW_HEIGHT_VIDEO,
    VIDEO_QUALITIES,
    DEFAULT_VIDEO_QUALITY,
    CONCURRENT_FRAGMENTS,
    LOG_DIR,
    LOG_DATE_FORMAT,
    LOG_FORMAT,
    PADDING_LARGE,
    PADDING_MEDIUM,
    PADDING_SMALL,
    WINDOW_WIDTH
)

# Configure logging for security events
logger = logging.getLogger(__name__)

# Security constants for video downloads
ALLOWED_VIDEO_FORMATS = {'mp4', 'webm', 'mkv'}
ALLOWED_VIDEO_CODECS = {'h264', 'vp9', 'av1'}
ALLOWED_AUDIO_CODECS = {'aac', 'opus', 'vorbis'}
MAX_CONCURRENT_FRAGMENTS = 10  # Limit concurrent downloads to prevent resource exhaustion
MAX_VIDEO_HEIGHT = 4320  # 8K max


class YouTubeVideoDownloaderGUI(BaseYouTubeDownloaderGUI):
    """GUI application for downloading YouTube videos.

    Extends the base downloader with video-specific features including:
    - Quality selection (720p, 1080p, 4K, Best)
    - Real-time progress tracking with speed and ETA
    - Concurrent fragment downloads for faster speeds
    - Automatic format merging to MP4
    - Comprehensive logging system

    The application saves user preferences including selected quality
    and last used output directory.

    Attributes:
        progress_var: Variable for progress bar percentage.
        progress_bar: Progress bar widget for download progress.
        status_label: Label displaying download status and statistics.
        quality_var: Variable holding selected video quality.
        cancel_btn: Button to cancel ongoing downloads.
    """

    def __init__(self, root: tk.Tk) -> None:
        """Initialize the video downloader GUI.

        Sets up the video downloader with quality selection, progress
        tracking, and loads user preferences for directory and quality.

        Args:
            root: The main tkinter window instance.
        """
        config: Config = Config()
        # Load last used directory or default
        output_dir = config.get_default_video_dir()
        super().__init__(root, "YouTube Video Downloader", output_dir)

        # Check for saved directory preference
        saved_dir = self.user_config.get_last_video_dir()
        if saved_dir:
            self.output_dir = Path(saved_dir)

        # Instance variables
        self.progress_var: tk.DoubleVar
        self.progress_bar: ttk.Progressbar
        self.status_label: ttk.Label
        self.quality_var: tk.StringVar
        self.cancel_btn: ttk.Button

        self.setup_logging()
        self.create_widgets()

    def setup_logging(self) -> None:
        """Set up logging for the application.

        Creates a logs directory and configures file-based logging
        with timestamps. Each day creates a new log file named with
        the date format YYYYMMDD.

        Log files include INFO level messages and above, with timestamps
        and detailed formatting for troubleshooting.
        """
        log_dir: Path = Path(LOG_DIR)
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=log_dir / f"downloader_{datetime.now():{LOG_DATE_FORMAT}}.log",
            level=logging.INFO,
            format=LOG_FORMAT
        )

    def create_widgets(self) -> None:
        """Create all widgets for the video downloader.

        Creates and configures video-specific UI components including:
        - Quality selection dropdown with user preferences
        - Progress bar with percentage display
        - Status label for download statistics (speed, ETA)
        - Download and Cancel buttons

        Loads saved quality preference and applies it to the quality selector.
        Adjusts window size to accommodate all video downloader widgets.
        """
        self.create_base_widgets()

        # Quality Selection
        quality_frame: ttk.Frame = ttk.Frame(self.root)
        quality_frame.pack(padx=PADDING_LARGE, pady=(0, PADDING_MEDIUM), fill=tk.X)

        ttk.Label(quality_frame, text="Quality:").pack(side=tk.LEFT)

        # Get saved quality preference or use default
        saved_quality = self.user_config.get_video_quality()
        self.quality_var = tk.StringVar(value=saved_quality)

        quality_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.quality_var,
            values=list(VIDEO_QUALITIES.keys()),
            state='readonly',
            width=15
        )
        quality_combo.pack(side=tk.LEFT, padx=(PADDING_MEDIUM, 0))
        quality_combo.bind('<<ComboboxSelected>>', self.on_quality_change)

        # Progress Bar
        progress_frame: ttk.Frame = ttk.Frame(self.root)
        progress_frame.pack(fill=tk.X, padx=PADDING_LARGE, pady=(PADDING_MEDIUM, 0))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           mode='determinate')
        self.progress_bar.pack(fill=tk.X)

        self.status_label = ttk.Label(progress_frame, text="")
        self.status_label.pack(fill=tk.X, pady=(PADDING_SMALL, 0))

        # Button Frame with Download and Cancel buttons
        button_frame: ttk.Frame = ttk.Frame(self.root)
        button_frame.pack(pady=PADDING_LARGE)

        self.download_btn = ttk.Button(button_frame, text="Download Video",
                                      command=self.download)
        self.download_btn.pack(side=tk.LEFT, padx=(0, PADDING_MEDIUM))

        self.cancel_btn = ttk.Button(button_frame, text="Cancel",
                                    command=self.cancel_download,
                                    state='disabled')
        self.cancel_btn.pack(side=tk.LEFT)

        # Adjust window size for all widgets
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT_VIDEO}")

    def on_quality_change(self, event: Any = None) -> None:
        """Save quality preference when changed.

        Called automatically when the user selects a different quality
        from the dropdown. Persists the selection to user preferences.

        Args:
            event: Tkinter event object (unused but required by event binding).
        """
        quality = self.quality_var.get()
        self.user_config.set_video_quality(quality)

    def save_directory_preference(self, directory: str) -> None:
        """Save video directory preference.

        Overrides base class method to save video-specific directory
        preference to user configuration.

        Args:
            directory: The directory path to save as video output preference.
        """
        self.user_config.set_last_video_dir(directory)

    def _validate_video_format(self, fmt: str) -> str:
        """
        Validate video output format to prevent command injection.

        Args:
            fmt: Video format string to validate

        Returns:
            Validated format string

        Raises:
            ValueError: If format is invalid or not allowed
        """
        fmt = fmt.strip().lower()
        if fmt not in ALLOWED_VIDEO_FORMATS:
            logger.warning(f"Invalid video format requested: {fmt}")
            raise ValueError(f"Unsupported video format. Allowed formats: {', '.join(ALLOWED_VIDEO_FORMATS)}")
        if not re.match(r'^[a-z0-9]+$', fmt):
            logger.warning(f"Video format contains invalid characters: {fmt}")
            raise ValueError("Invalid format string")
        logger.info(f"Video format validated: {fmt}")
        return fmt

    def _validate_concurrent_fragments(self, count: int) -> int:
        """
        Validate concurrent fragment download count.

        Args:
            count: Number of concurrent fragments

        Returns:
            Validated count

        Raises:
            ValueError: If count is invalid
        """
        if count < 1 or count > MAX_CONCURRENT_FRAGMENTS:
            logger.warning(f"Invalid concurrent fragment count: {count}")
            raise ValueError(f"Concurrent fragments must be between 1 and {MAX_CONCURRENT_FRAGMENTS}")
        logger.info(f"Concurrent fragments validated: {count}")
        return count

    def _sanitize_postprocessor_args(self, args: List[str]) -> List[str]:
        """
        Sanitize postprocessor arguments to prevent command injection.

        Args:
            args: List of postprocessor arguments

        Returns:
            Sanitized argument list
        """
        allowed_args = {'-c:v', '-c:a', 'copy', '-preset', 'fast', 'medium', 'slow',
                       '-crf', '18', '20', '22', '23', '24', '-b:v', '-b:a', '-vf', '-af'}
        sanitized_args = []
        for arg in args:
            if arg in allowed_args or re.match(r'^\d+[kKmM]?$', arg):
                sanitized_args.append(arg)
            else:
                logger.warning(f"Removing potentially dangerous postprocessor arg: {arg}")
        logger.info(f"Postprocessor args sanitized: {len(args)} -> {len(sanitized_args)}")
        return sanitized_args

    def _sanitize_download_options(self, ydl_opts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize yt-dlp download options to prevent command injection.

        Args:
            ydl_opts: Dictionary of yt-dlp options

        Returns:
            Sanitized options dictionary
        """
        if 'merge_output_format' in ydl_opts:
            ydl_opts['merge_output_format'] = self._validate_video_format(ydl_opts['merge_output_format'])
        if 'concurrent_fragment_downloads' in ydl_opts:
            ydl_opts['concurrent_fragment_downloads'] = self._validate_concurrent_fragments(
                ydl_opts['concurrent_fragment_downloads'])
        if 'postprocessor_args' in ydl_opts:
            ydl_opts['postprocessor_args'] = self._sanitize_postprocessor_args(ydl_opts['postprocessor_args'])
        if 'socket_timeout' not in ydl_opts:
            ydl_opts['socket_timeout'] = 30
        ydl_opts['noplaylist'] = True
        dangerous_opts = ['exec', 'external_downloader_args']
        for opt in dangerous_opts:
            if opt in ydl_opts:
                logger.warning(f"Removing dangerous option: {opt}")
                del ydl_opts[opt]
        return ydl_opts

    def download_hook(self, d: dict[str, Any]) -> None:
        """Hook for download progress updates.

        Called by yt-dlp during download to provide progress information.
        Updates the progress bar and status label with download statistics
        including percentage, speed, and estimated time remaining.

        Args:
            d: Dictionary containing download progress information from yt-dlp.
                Expected keys: 'status', 'total_bytes', 'downloaded_bytes',
                'speed', 'eta'.
        """
        if d['status'] == 'downloading':
            try:
                # Calculate progress percentage
                total_bytes: int = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded: int = d.get('downloaded_bytes', 0)
                if total_bytes:
                    progress: float = (downloaded / total_bytes) * 100
                    speed: int = d.get('speed', 0)
                    if speed:
                        speed_mb: float = speed / 1024 / 1024  # Convert to MB/s
                        eta: int = d.get('eta', 0)
                        status_text: str = f'Downloading: {progress:.1f}% (Speed: {speed_mb:.1f} MB/s, ETA: {eta}s)'
                    else:
                        status_text: str = f'Downloading: {progress:.1f}%'

                    # Update progress bar in main thread
                    self.root.after(0, lambda: self.update_progress(progress, status_text))
            except Exception as e:
                logging.error(f"Error updating progress: {str(e)}")
        elif d['status'] == 'finished':
            logging.info("Download completed!")
            self.root.after(0, lambda: self.update_progress(100, "Download complete!"))

    def update_progress(self, progress: float, status_text: str) -> None:
        """Update the progress bar and status label.

        Safely updates UI elements from the download worker thread by
        using the main thread. Forces UI refresh to ensure smooth
        progress display.

        Args:
            progress: Progress percentage (0-100).
            status_text: Status message to display (e.g., download speed, ETA).
        """
        self.progress_var.set(progress)
        self.status_label.config(text=status_text)
        self.root.update_idletasks()

    def download(self) -> None:
        """Start the video download process with security validations.

        Initiates video download in a background thread with the selected
        quality settings. Applies comprehensive security validations including:
        - URL sanitization and validation
        - Download option sanitization
        - Input length limits
        - Security logging

        Configures yt-dlp options for optimal download:
        - Selected quality format (720p/1080p/4K/Best)
        - MP4 output with merged audio/video
        - Concurrent fragment downloads (validated and limited)
        - Progress hooks for UI updates

        Disables the download button and enables the cancel button while
        downloading. All download work happens in a daemon thread to
        prevent blocking the UI.
        """
        try:
            # Security: Get and strip URL (further validation in worker)
            url: str = self.url_entry.get().strip()

            # Security: Validate URL length before processing
            if len(url) > 2048:
                raise ValueError("URL is too long")

            if not url:
                raise ValueError("Please enter a URL")

            self.download_btn.config(state='disabled')
            self.cancel_btn.config(state='normal')

            # Get selected quality
            selected_quality = self.quality_var.get()
            quality_format = VIDEO_QUALITIES.get(selected_quality, VIDEO_QUALITIES[DEFAULT_VIDEO_QUALITY])

            # Build download options
            ydl_opts: dict[str, Any] = {
                'format': quality_format,
                'progress_hooks': [self.download_hook],
                'noplaylist': True,
                'merge_output_format': 'mp4',
                'concurrent_fragment_downloads': CONCURRENT_FRAGMENTS,
                'postprocessor_args': ['-c:v', 'copy', '-c:a', 'copy'],
            }

            # Security: Sanitize download options to prevent command injection
            ydl_opts = self._sanitize_download_options(ydl_opts)

            # Security logging: Log download initiation (without full URL to avoid log injection)
            url_domain = url.split('/')[2] if len(url.split('/')) > 2 else 'unknown'
            logger.info(f"Starting video download - Quality: {selected_quality}, Domain: {url_domain}")
            logging.info(f"Video download initiated - Quality: {selected_quality}")

            # Start download thread
            self.download_thread = threading.Thread(
                target=self.download_worker,
                args=(url, ydl_opts),
                daemon=True
            )
            self.download_thread.start()

        except ValueError as e:
            # Show validation errors to user
            messagebox.showerror("Validation Error", str(e))
            self.download_btn.config(state='normal')
            self.cancel_btn.config(state='disabled')
            logger.warning(f"Download validation failed: {e}")
        except Exception as e:
            # Catch any unexpected errors
            messagebox.showerror("Error", "An unexpected error occurred. Please try again.")
            self.download_btn.config(state='normal')
            self.cancel_btn.config(state='disabled')
            logger.error(f"Unexpected error in download initiation: {e}", exc_info=True)


def main() -> None:
    """Main entry point for video downloader.

    Creates the tkinter root window, initializes the video downloader
    GUI, and starts the main event loop. This function is called when
    the module is run directly or via the yt-video console script.
    """
    root: tk.Tk = tk.Tk()
    app: YouTubeVideoDownloaderGUI = YouTubeVideoDownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
