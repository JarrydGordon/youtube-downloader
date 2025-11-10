"""Audio downloader GUI for YouTube."""

from typing import Any, Dict
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
from pathlib import Path
import re

from .base_gui import BaseYouTubeDownloaderGUI
from .config import Config
from .constants import (
    WINDOW_HEIGHT_AUDIO,
    WINDOW_WIDTH,
    AUDIO_FORMATS,
    DEFAULT_AUDIO_FORMAT,
    PADDING_LARGE,
    PADDING_MEDIUM,
    PADDING_SMALL
)

# Configure logging for security events
logger = logging.getLogger(__name__)

# Security constants for audio downloads
MAX_PLAYLIST_SIZE = 500  # Maximum number of videos in a playlist
ALLOWED_AUDIO_CODECS = {'mp3', 'aac', 'opus', 'vorbis', 'flac', 'wav', 'm4a'}
MAX_AUDIO_QUALITY = 320  # Maximum bitrate for audio


class YouTubeAudioDownloaderGUI(BaseYouTubeDownloaderGUI):
    """GUI application for downloading YouTube audio.

    Extends the base downloader with audio-specific features including:
    - Audio format selection (MP3, AAC, OPUS, M4A)
    - Quality/bitrate selection
    - Playlist download support with size limits
    - Progress tracking for audio extraction
    - Security validations for codec and quality settings

    The application includes comprehensive security measures including
    codec whitelisting, quality validation, and playlist size limits
    to prevent abuse and command injection.

    Attributes:
        playlist_var: Boolean variable for playlist download option.
        playlist_check: Checkbox widget for playlist download.
        format_var: String variable holding selected audio format.
        progress_var: Variable for progress bar percentage.
        progress_bar: Progress bar widget for download progress.
        status_label: Label displaying download status.
        cancel_btn: Button to cancel ongoing downloads.
    """

    def __init__(self, root: tk.Tk) -> None:
        """Initialize the audio downloader GUI.

        Sets up the audio downloader with format selection, playlist
        support, and progress tracking. Loads user preferences for
        directory and audio format.

        Args:
            root: The main tkinter window instance.
        """
        config: Config = Config()
        # Load last used directory or default
        output_dir = config.get_default_music_dir()
        super().__init__(root, "YouTube Audio Downloader", output_dir)

        # Check for saved directory preference
        saved_dir = self.user_config.get_last_audio_dir()
        if saved_dir:
            self.output_dir = Path(saved_dir)

        # Instance variables
        self.playlist_var: tk.BooleanVar
        self.playlist_check: ttk.Checkbutton
        self.format_var: tk.StringVar
        self.progress_var: tk.DoubleVar
        self.progress_bar: ttk.Progressbar
        self.status_label: ttk.Label
        self.cancel_btn: ttk.Button

        self.create_widgets()

    def create_widgets(self) -> None:
        """Create all widgets for the audio downloader.

        Creates and configures audio-specific UI components including:
        - Audio format selection dropdown (MP3, AAC, OPUS, M4A)
        - Playlist download checkbox
        - Progress bar with percentage display
        - Status label for download progress
        - Download and Cancel buttons

        Loads saved format preference and applies it to the format selector.
        Adjusts window size to accommodate all audio downloader widgets.
        """
        self.create_base_widgets()

        # Format Selection
        format_frame: ttk.Frame = ttk.Frame(self.root)
        format_frame.pack(padx=PADDING_LARGE, pady=(0, PADDING_MEDIUM), fill=tk.X)

        ttk.Label(format_frame, text="Format:").pack(side=tk.LEFT)

        # Get saved format preference or use default
        saved_format = self.user_config.get_audio_format()
        self.format_var = tk.StringVar(value=saved_format)

        format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.format_var,
            values=list(AUDIO_FORMATS.keys()),
            state='readonly',
            width=15
        )
        format_combo.pack(side=tk.LEFT, padx=(PADDING_MEDIUM, 0))
        format_combo.bind('<<ComboboxSelected>>', self.on_format_change)

        # Playlist checkbox
        self.playlist_var = tk.BooleanVar()
        self.playlist_check = ttk.Checkbutton(
            self.root,
            text="Download Playlist",
            variable=self.playlist_var,
            style="TCheckbutton"
        )
        self.playlist_check.pack(pady=(0, PADDING_MEDIUM))

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

        self.download_btn = ttk.Button(button_frame, text="Download Audio",
                                      command=self.download)
        self.download_btn.pack(side=tk.LEFT, padx=(0, PADDING_MEDIUM))

        self.cancel_btn = ttk.Button(button_frame, text="Cancel",
                                    command=self.cancel_download,
                                    state='disabled')
        self.cancel_btn.pack(side=tk.LEFT)

        # Adjust window size
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT_AUDIO}")

    def on_format_change(self, event: Any = None) -> None:
        """Save format preference when changed.

        Called automatically when the user selects a different audio
        format from the dropdown. Persists the selection to user preferences.

        Args:
            event: Tkinter event object (unused but required by event binding).
        """
        audio_format = self.format_var.get()
        self.user_config.set_audio_format(audio_format)

    def save_directory_preference(self, directory: str) -> None:
        """Save audio directory preference.

        Overrides base class method to save audio-specific directory
        preference to user configuration.

        Args:
            directory: The directory path to save as audio output preference.
        """
        self.user_config.set_last_audio_dir(directory)

    def _validate_audio_codec(self, codec: str) -> str:
        """
        Validate audio codec to prevent command injection.

        Args:
            codec: Audio codec string to validate

        Returns:
            Validated codec string

        Raises:
            ValueError: If codec is invalid or not allowed
        """
        # Sanitize codec string
        codec = codec.strip().lower()

        # Check against whitelist
        if codec not in ALLOWED_AUDIO_CODECS:
            logger.warning(f"Invalid audio codec requested: {codec}")
            raise ValueError(f"Unsupported audio codec. Allowed codecs: {', '.join(ALLOWED_AUDIO_CODECS)}")

        # Additional check: ensure no special characters that could enable injection
        if not re.match(r'^[a-z0-9]+$', codec):
            logger.warning(f"Audio codec contains invalid characters: {codec}")
            raise ValueError("Invalid codec format")

        logger.info(f"Audio codec validated: {codec}")
        return codec

    def _validate_audio_quality(self, quality: str) -> str:
        """
        Validate audio quality setting.

        Args:
            quality: Quality string (bitrate)

        Returns:
            Validated quality string

        Raises:
            ValueError: If quality is invalid
        """
        try:
            # Attempt to parse as integer
            quality_int = int(quality)

            # Check reasonable bounds (8 kbps to 320 kbps)
            if quality_int < 8 or quality_int > MAX_AUDIO_QUALITY:
                logger.warning(f"Audio quality out of bounds: {quality_int}")
                raise ValueError(f"Audio quality must be between 8 and {MAX_AUDIO_QUALITY} kbps")

            logger.info(f"Audio quality validated: {quality_int}")
            return str(quality_int)

        except ValueError:
            logger.warning(f"Invalid audio quality value: {quality}")
            raise ValueError("Audio quality must be a number")

    def _sanitize_download_options(self, ydl_opts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize yt-dlp download options to prevent command injection.

        Args:
            ydl_opts: Dictionary of yt-dlp options

        Returns:
            Sanitized options dictionary
        """
        # Validate postprocessor settings
        if 'postprocessors' in ydl_opts:
            for pp in ydl_opts['postprocessors']:
                if 'preferredcodec' in pp:
                    pp['preferredcodec'] = self._validate_audio_codec(pp['preferredcodec'])

                if 'preferredquality' in pp:
                    pp['preferredquality'] = self._validate_audio_quality(pp['preferredquality'])

        # Security: Limit playlist size to prevent DoS
        if not ydl_opts.get('noplaylist', True):
            ydl_opts['playlistend'] = MAX_PLAYLIST_SIZE
            logger.info(f"Playlist download limited to {MAX_PLAYLIST_SIZE} items")

        # Security: Add timeout if not present
        if 'socket_timeout' not in ydl_opts:
            ydl_opts['socket_timeout'] = 30

        # Security: Prevent dangerous options
        dangerous_opts = ['exec', 'external_downloader_args']
        for opt in dangerous_opts:
            if opt in ydl_opts:
                logger.warning(f"Removing dangerous option: {opt}")
                del ydl_opts[opt]

        return ydl_opts

    def validate_url(self, url: str) -> None:
        """
        Validate URL and check for playlist if playlist mode is enabled.

        Args:
            url: URL to validate

        Raises:
            ValueError: If URL validation fails
        """
        # Call parent validation (includes sanitization)
        super().validate_url(url)

        # Verify playlist URL if playlist mode is selected
        if self.playlist_var.get() and "list=" not in url:
            logger.warning("Playlist mode enabled but URL is not a playlist")
            raise ValueError("Not a valid YouTube playlist URL. Playlist URLs must contain 'list=' parameter.")

        # Security logging: Log download initiation (without full URL to avoid log injection)
        url_domain = url.split('/')[2] if len(url.split('/')) > 2 else 'unknown'
        logger.info(f"Audio download validation passed for domain: {url_domain}, playlist={self.playlist_var.get()}")

    def download_hook(self, d: dict[str, Any]) -> None:
        """Hook for download progress updates.

        Called by yt-dlp during download to provide progress information.
        Updates the progress bar and status label with download statistics
        including percentage, speed, and estimated time remaining.

        When download finishes, shows "Processing audio..." status to
        indicate the audio extraction and conversion phase.

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
            self.root.after(0, lambda: self.update_progress(100, "Processing audio..."))

    def update_progress(self, progress: float, status_text: str) -> None:
        """Update the progress bar and status label.

        Safely updates UI elements from the download worker thread by
        using the main thread. Forces UI refresh to ensure smooth
        progress display.

        Args:
            progress: Progress percentage (0-100).
            status_text: Status message to display (e.g., download speed,
                audio processing status).
        """
        self.progress_var.set(progress)
        self.status_label.config(text=status_text)
        self.root.update_idletasks()

    def download(self) -> None:
        """
        Start the audio download process with security validations.

        Applies input sanitization, validates download options, and starts
        the download worker thread with sanitized parameters.
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

            # Get selected format
            selected_format = self.format_var.get()
            format_config = AUDIO_FORMATS.get(selected_format, AUDIO_FORMATS[DEFAULT_AUDIO_FORMAT])

            # Build download options
            ydl_opts: dict[str, Any] = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': format_config['codec'],
                    'preferredquality': format_config['quality'],
                }],
                'progress_hooks': [self.download_hook],
                'noplaylist': not self.playlist_var.get()
            }

            # Security: Sanitize download options to prevent command injection
            ydl_opts = self._sanitize_download_options(ydl_opts)

            # Log download initiation
            logger.info(f"Starting audio download - Format: {selected_format}, Playlist: {not ydl_opts['noplaylist']}")

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
    """Main entry point for audio downloader.

    Creates the tkinter root window, initializes the audio downloader
    GUI, and starts the main event loop. This function is called when
    the module is run directly or via the yt-audio console script.
    """
    root: tk.Tk = tk.Tk()
    app: YouTubeAudioDownloaderGUI = YouTubeAudioDownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
