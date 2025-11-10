"""Base GUI class with shared functionality for YouTube downloaders."""

from typing import Any, Optional
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import validators
from pathlib import Path
import yt_dlp
import re
import urllib.parse
import shutil
import time
import logging

from .config import Config
from .user_config import UserConfig
from .constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT_BASE,
    BG_COLOR_DARK, BG_COLOR_DARKER, FG_COLOR, FG_COLOR_DARK,
    HIGHLIGHT_COLOR, SELECT_BG_COLOR,
    PADDING_LARGE, PADDING_MEDIUM,
    FONT_DEFAULT, FONT_ENTRY
)

# Configure logging
logger = logging.getLogger(__name__)

# Security constants
MAX_URL_LENGTH = 2048
MAX_FILENAME_LENGTH = 255
ALLOWED_FILENAME_CHARS = re.compile(r'^[a-zA-Z0-9_\-\.\s\(\)\[\]]+$')
MIN_FREE_SPACE_BYTES = 500 * 1024 * 1024  # 500MB minimum free space
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 2  # seconds


class BaseYouTubeDownloaderGUI:
    """Base class for YouTube downloader GUI applications.

    Provides shared functionality and UI components for both video and audio
    downloaders, including URL validation, clipboard integration, FFmpeg
    configuration, download management, and security features.

    This class implements a dark-themed GUI with robust error handling,
    retry logic, and comprehensive security measures including URL sanitization,
    path traversal prevention, and disk space checking.

    Attributes:
        root: The main tkinter window instance.
        style: ttk.Style instance for dark theme configuration.
        config: Config instance for platform-specific settings.
        user_config: UserConfig instance for user preferences.
        output_dir: Path object representing the output directory.
        download_thread: Thread instance for download operations.
        cancel_flag: Threading event for download cancellation.
        url_entry: Entry widget for URL input.
        dir_label: Label widget displaying the current output directory.
        download_btn: Button widget to trigger downloads.
    """

    def __init__(self, root: tk.Tk, title: str, output_dir: Path) -> None:
        """Initialize the base YouTube downloader GUI.

        Args:
            root: The main tkinter window instance.
            title: Window title to display.
            output_dir: Default output directory path for downloads.
        """
        self.root: tk.Tk = root
        self.root.title(title)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT_BASE}")

        # Configure dark theme
        self.style: ttk.Style = ttk.Style()
        self.style.configure(".", background=BG_COLOR_DARK, foreground=FG_COLOR)
        self.style.configure("TFrame", background=BG_COLOR_DARK)
        self.style.configure("TLabel", background=BG_COLOR_DARK, foreground=FG_COLOR)
        self.style.configure("TButton", background=FG_COLOR, foreground=FG_COLOR_DARK,
                           padding=PADDING_MEDIUM, font=FONT_DEFAULT)
        self.style.configure("TCheckbutton", background=BG_COLOR_DARK, foreground=FG_COLOR)

        self.root.configure(bg=BG_COLOR_DARK)

        self.config: Config = Config()
        self.user_config: UserConfig = UserConfig()
        self.output_dir: Path = output_dir

        # Thread management for cancellation
        self.download_thread: Optional[threading.Thread] = None
        self.cancel_flag: threading.Event = threading.Event()

        # Widgets that will be created by subclasses
        self.url_entry: tk.Entry
        self.dir_label: ttk.Label
        self.download_btn: ttk.Button

    def _sanitize_url(self, url: str) -> str:
        """
        Sanitize and validate URL to prevent security issues.

        Args:
            url: The URL to sanitize

        Returns:
            Sanitized URL string

        Raises:
            ValueError: If URL fails security checks
        """
        # Strip whitespace
        url = url.strip()

        # Check length to prevent DoS
        if len(url) > MAX_URL_LENGTH:
            logger.warning(f"URL exceeds maximum length: {len(url)} > {MAX_URL_LENGTH}")
            raise ValueError("URL is too long")

        # Parse URL to validate structure
        try:
            parsed = urllib.parse.urlparse(url)
        except Exception as e:
            logger.warning(f"URL parsing failed: {e}")
            raise ValueError("Invalid URL format")

        # Ensure scheme is http or https
        if parsed.scheme not in ('http', 'https'):
            logger.warning(f"Invalid URL scheme: {parsed.scheme}")
            raise ValueError("URL must use http or https")

        # Check for potentially dangerous characters
        dangerous_chars = ['<', '>', '"', '{', '}', '|', '\\', '^', '`']
        if any(char in url for char in dangerous_chars):
            logger.warning("URL contains dangerous characters")
            raise ValueError("URL contains invalid characters")

        logger.info(f"URL sanitized successfully")
        return url

    def _sanitize_output_dir(self, output_dir: Path) -> Path:
        """
        Sanitize output directory to prevent path traversal attacks.

        Args:
            output_dir: The output directory path

        Returns:
            Sanitized and resolved Path object
        """
        try:
            # Resolve to absolute path and eliminate any .. or symlinks
            resolved_path = output_dir.resolve()

            # Security check: ensure path doesn't escape to system directories
            # Allow only paths under home, current working dir, or temp
            import tempfile
            allowed_roots = [Path.home(), Path.cwd(), Path(tempfile.gettempdir())]

            is_allowed = False
            for root in allowed_roots:
                try:
                    resolved_path.relative_to(root.resolve())
                    is_allowed = True
                    break
                except ValueError:
                    continue

            if not is_allowed:
                logger.warning(f"Output directory outside allowed paths: {resolved_path}")
                # Fallback to safe default
                safe_default = Path.home() / "Downloads"
                logger.info(f"Using safe fallback directory: {safe_default}")
                return safe_default.resolve()

            logger.info(f"Output directory sanitized: {resolved_path}")
            return resolved_path

        except Exception as e:
            logger.error(f"Error sanitizing output directory: {e}")
            # Return safe fallback
            return (Path.home() / "Downloads").resolve()

    def _check_disk_space(self, directory: Path, required_bytes: int = MIN_FREE_SPACE_BYTES) -> bool:
        """
        Check if there's sufficient disk space before download.

        Args:
            directory: Directory to check space for
            required_bytes: Minimum required bytes (default 500MB)

        Returns:
            True if sufficient space, False otherwise
        """
        try:
            stat = shutil.disk_usage(directory)
            free_space_mb = stat.free / (1024 * 1024)
            required_mb = required_bytes / (1024 * 1024)

            if stat.free < required_bytes:
                logger.warning(f"Insufficient disk space: {free_space_mb:.1f}MB free, {required_mb:.1f}MB required")
                return False

            logger.info(f"Disk space check passed: {free_space_mb:.1f}MB available")
            return True

        except Exception as e:
            logger.error(f"Error checking disk space: {e}")
            # On error, allow operation but log warning
            return True

    def _validate_ffmpeg_path(self, ffmpeg_path: str) -> None:
        """
        Thoroughly validate FFmpeg path for security.

        Args:
            ffmpeg_path: Path to FFmpeg executable

        Raises:
            RuntimeError: If FFmpeg validation fails
        """
        # Use config's validation method
        validated_path = self.config.validate_ffmpeg_executable(ffmpeg_path)

        if not validated_path:
            logger.error("FFmpeg validation failed")
            raise RuntimeError(
                "FFmpeg not found or not executable. "
                "Please install FFmpeg and ensure it's in your system PATH."
            )

        logger.info(f"FFmpeg validated: {validated_path}")

    def _sanitize_generic_error(self, error: Exception) -> str:
        """
        Sanitize error messages to avoid exposing system internals.

        Args:
            error: The exception to sanitize

        Returns:
            User-friendly error message
        """
        error_str = str(error).lower()

        # Map specific errors to user-friendly messages
        if 'network' in error_str or 'connection' in error_str or 'timeout' in error_str:
            return "Network error occurred. Please check your internet connection and try again."

        if 'permission' in error_str or 'access denied' in error_str:
            return "Permission error. Please check that you have write access to the output directory."

        if 'disk' in error_str or 'space' in error_str or 'no space' in error_str:
            return "Insufficient disk space. Please free up space and try again."

        if 'ffmpeg' in error_str:
            return "FFmpeg error. Please ensure FFmpeg is properly installed."

        if 'video unavailable' in error_str or 'private video' in error_str:
            return "Video is unavailable or private. Please check the URL."

        if 'age' in error_str and 'restricted' in error_str:
            return "Video is age-restricted and cannot be downloaded."

        # Generic fallback without system details
        logger.error(f"Download error: {error}")
        return "Download failed. Please check the URL and try again."

    def create_base_widgets(self) -> None:
        """Create the base widgets shared by all downloaders.

        Creates and configures the following UI components:
        - URL input field with dark theme styling
        - Paste URL button for clipboard integration
        - Output directory label and browse button

        All widgets are configured with the dark theme color scheme
        and proper layout using tkinter pack geometry manager.
        """
        # URL Input
        input_frame: ttk.Frame = ttk.Frame(self.root)
        input_frame.pack(padx=PADDING_LARGE, pady=(PADDING_LARGE, 0), fill=tk.X)

        ttk.Label(input_frame, text="YouTube URL:").pack(side=tk.LEFT)

        # Custom Entry widget with dark theme
        self.url_entry = tk.Entry(
            input_frame,
            bg=BG_COLOR_DARKER,
            fg=FG_COLOR,
            insertbackground=FG_COLOR,
            selectbackground=SELECT_BG_COLOR,
            selectforeground=FG_COLOR_DARK,
            relief="flat",
            highlightthickness=1,
            highlightcolor=HIGHLIGHT_COLOR,
            highlightbackground=HIGHLIGHT_COLOR,
            font=FONT_ENTRY
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(PADDING_MEDIUM, PADDING_MEDIUM))

        # Paste URL button
        paste_btn: ttk.Button = ttk.Button(input_frame, text="Paste URL", command=self.paste_url)
        paste_btn.pack(side=tk.LEFT)

        # Output Directory Frame with Browse button
        dir_frame: ttk.Frame = ttk.Frame(self.root)
        dir_frame.pack(padx=PADDING_LARGE, pady=PADDING_MEDIUM, fill=tk.X)

        self.dir_label = ttk.Label(dir_frame, text=f"Output: {self.output_dir}")
        self.dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_btn: ttk.Button = ttk.Button(dir_frame, text="Browse", command=self.browse_directory)
        browse_btn.pack(side=tk.LEFT, padx=(PADDING_MEDIUM, 0))

    def validate_url(self, url: str) -> None:
        """
        Validate that the URL is a valid YouTube URL.

        Args:
            url: URL to validate

        Raises:
            ValueError: If URL is invalid or fails security checks
        """
        # First sanitize the URL
        url = self._sanitize_url(url)

        # Then validate with validators library
        if not url or not validators.url(url):
            raise ValueError("Please enter a valid YouTube URL")

        # Check it's actually a YouTube URL
        if "youtube.com" not in url and "youtu.be" not in url:
            raise ValueError("Not a YouTube URL")

        logger.info("URL validation successful")

    def paste_url(self) -> None:
        """Paste URL from clipboard into the entry field.

        Retrieves text from the system clipboard and inserts it into
        the URL entry field, replacing any existing content.

        Displays a warning message if the clipboard is empty or
        contains no text.
        """
        try:
            clipboard_text: str = self.root.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard_text)
        except tk.TclError:
            messagebox.showwarning("Paste Error", "No text found in clipboard")

    def browse_directory(self) -> None:
        """Open directory browser to select output directory.

        Displays a native directory selection dialog allowing users to
        choose a custom output location for downloads. Updates the
        output directory label and saves the preference if a directory
        is selected.

        The dialog opens at the current output directory as the initial
        location for convenience.
        """
        selected_dir = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=str(self.output_dir)
        )
        if selected_dir:
            self.output_dir = Path(selected_dir)
            self.dir_label.config(text=f"Output: {self.output_dir}")
            # Save the preference (to be overridden by subclasses for specific dir types)
            self.save_directory_preference(selected_dir)

    def save_directory_preference(self, directory: str) -> None:
        """Save directory preference to user configuration.

        This method is intended to be overridden by subclasses to
        save type-specific directory preferences (e.g., separate
        preferences for video and audio directories).

        Args:
            directory: The directory path to save as a preference.
        """
        pass

    def cancel_download(self) -> None:
        """Cancel the ongoing download.

        Sets the cancellation flag to stop the current download operation.
        The download worker thread checks this flag and stops gracefully.

        Displays an informational message to the user confirming the
        cancellation request. Note that due to yt-dlp's architecture,
        the cancellation may not be immediate.
        """
        if self.download_thread and self.download_thread.is_alive():
            self.cancel_flag.set()
            messagebox.showinfo("Canceling", "Download cancellation requested...")
            # Note: yt-dlp doesn't have built-in cancellation, but the flag
            # prevents success message and can be checked by progress hooks

    def download_worker(self, url: str, ydl_opts: dict[str, Any]) -> None:
        """
        Worker thread for downloading content with retry logic and security checks.

        Args:
            url: URL to download
            ydl_opts: yt-dlp options dictionary
        """
        retry_count = 0
        last_error = None

        try:
            # Clear cancel flag at start
            self.cancel_flag.clear()

            # Security: Validate and sanitize URL
            self.validate_url(url)

            # Security: Sanitize output directory to prevent path traversal
            self.output_dir = self._sanitize_output_dir(self.output_dir)

            # Security: Check disk space before download
            if not self._check_disk_space(self.output_dir):
                raise RuntimeError(
                    "Insufficient disk space. Please free up at least 500MB and try again."
                )

            # Security: Validate FFmpeg executable
            ffmpeg_path: str = self.config.get_ffmpeg_path()
            self._validate_ffmpeg_path(ffmpeg_path)

            # Security: Sanitize output template to prevent path traversal
            # Use only filename portion, discard any path components
            safe_template = '%(title).200s.%(ext)s'  # Limit title length
            output_template = str(self.output_dir / safe_template)

            # Add security options to yt-dlp
            ydl_opts['ffmpeg_location'] = ffmpeg_path
            ydl_opts['outtmpl'] = output_template

            # Security: Set socket timeout to prevent hanging
            if 'socket_timeout' not in ydl_opts:
                ydl_opts['socket_timeout'] = 30

            # Security: Limit file size to prevent DoS (10GB default)
            if 'max_filesize' not in ydl_opts:
                ydl_opts['max_filesize'] = 10 * 1024 * 1024 * 1024

            # Retry logic with exponential backoff
            while retry_count < MAX_RETRIES:
                try:
                    # Check if download was canceled
                    if self.cancel_flag.is_set():
                        logger.info("Download canceled by user")
                        break

                    logger.info(f"Download attempt {retry_count + 1}/{MAX_RETRIES}")

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])

                    # Success - break retry loop
                    logger.info("Download completed successfully")
                    break

                except Exception as e:
                    last_error = e
                    retry_count += 1
                    error_str = str(e).lower()

                    # Don't retry on certain errors
                    non_retryable = [
                        'video unavailable',
                        'private video',
                        'age-restricted',
                        'invalid url',
                        'not a youtube url',
                        'permission denied',
                        'disk space'
                    ]

                    if any(err in error_str for err in non_retryable):
                        logger.warning(f"Non-retryable error: {e}")
                        raise

                    if retry_count < MAX_RETRIES:
                        # Exponential backoff: 2s, 4s, 8s
                        delay = INITIAL_RETRY_DELAY * (2 ** (retry_count - 1))
                        logger.info(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        logger.error(f"Max retries reached: {e}")
                        raise

            # Only show success if not canceled and download succeeded
            if not self.cancel_flag.is_set() and retry_count < MAX_RETRIES:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success",
                    "Download completed successfully!"
                ))
            elif self.cancel_flag.is_set():
                self.root.after(0, lambda: messagebox.showinfo(
                    "Canceled",
                    "Download was canceled."
                ))

        except Exception as e:
            # Security: Sanitize error messages to avoid exposing system details
            error_msg = self._sanitize_generic_error(e)

            if not self.cancel_flag.is_set():
                self.root.after(0, lambda msg=error_msg: messagebox.showerror("Error", msg))

            # Log the actual error for debugging (not shown to user)
            logger.error(f"Download failed: {e}", exc_info=True)

        finally:
            self.root.after(0, lambda: self.download_btn.config(state='normal'))
            if hasattr(self, 'cancel_btn'):
                self.root.after(0, lambda: self.cancel_btn.config(state='disabled'))
