"""Configuration management for YouTube Downloader."""

from pathlib import Path
import os
import platform
import shutil
import stat
import logging
import tempfile
from typing import Optional

# Configure logging for security events
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Config:
    """Configuration class for managing user-specific settings.

    Provides platform-specific configuration for YouTube Downloader,
    including default directories for downloads and FFmpeg path resolution.

    This class implements robust directory validation with security checks,
    fallback mechanisms, and comprehensive FFmpeg detection across
    multiple common installation locations.

    Attributes:
        platform: String identifier for the current OS (Windows, Darwin, Linux).
    """

    def __init__(self) -> None:
        """Initialize the configuration manager.

        Detects the current platform/operating system for platform-specific
        configuration decisions.
        """
        self.platform: str = platform.system()

    def _validate_directory(self, directory: Path) -> Optional[Path]:
        """
        Validate that a directory exists and is writable.

        Args:
            directory: Path object to validate

        Returns:
            Path object if valid and writable, None otherwise
        """
        try:
            # Resolve to absolute path to prevent path traversal
            resolved_path = directory.resolve()

            # Security check: ensure resolved path is not outside expected areas
            # This prevents path traversal attacks
            try:
                resolved_path.relative_to(Path.home())
            except ValueError:
                # Not under home directory, check if under temp or cwd
                try:
                    resolved_path.relative_to(Path(tempfile.gettempdir()))
                except ValueError:
                    try:
                        resolved_path.relative_to(Path.cwd())
                    except ValueError:
                        logger.warning(f"Directory path outside allowed locations: {resolved_path}")
                        return None

            # Check if path exists
            if not resolved_path.exists():
                logger.info(f"Directory does not exist, attempting to create: {resolved_path}")
                try:
                    resolved_path.mkdir(parents=True, exist_ok=True)
                    # Set secure permissions (owner read/write/execute only)
                    if self.platform != "Windows":
                        resolved_path.chmod(stat.S_IRWXU)
                except Exception as e:
                    logger.warning(f"Failed to create directory {resolved_path}: {e}")
                    return None

            # Verify it's actually a directory
            if not resolved_path.is_dir():
                logger.warning(f"Path exists but is not a directory: {resolved_path}")
                return None

            # Check if writable by attempting to create a test file
            test_file = resolved_path / ".write_test"
            try:
                test_file.touch()
                test_file.unlink()
            except Exception as e:
                logger.warning(f"Directory is not writable: {resolved_path}: {e}")
                return None

            logger.info(f"Directory validated successfully: {resolved_path}")
            return resolved_path

        except Exception as e:
            logger.error(f"Error validating directory {directory}: {e}")
            return None

    def get_default_music_dir(self) -> Path:
        """Get the default music directory based on the operating system.

        Returns the platform-appropriate music directory with validation
        and fallback mechanisms. Attempts multiple locations in order:
        1. Primary OS-specific music directory
        2. Downloads/Music subdirectory
        3. Custom youtube_downloads/music directory
        4. Current working directory/downloads/music
        5. Temporary directory as last resort

        Returns:
            Path object for a validated, writable music directory.
        """
        # Primary directories based on OS
        if self.platform == "Windows":
            primary_dir = Path.home() / "Music"
        elif self.platform == "Darwin":  # macOS
            primary_dir = Path.home() / "Music"
        else:  # Linux and others
            primary_dir = Path.home() / "Music"

        # Try primary directory
        validated_dir = self._validate_directory(primary_dir)
        if validated_dir:
            return validated_dir

        # Fallback options
        fallback_dirs = [
            Path.home() / "Downloads" / "Music",
            Path.home() / "youtube_downloads" / "music",
            Path.cwd() / "downloads" / "music"
        ]

        for fallback in fallback_dirs:
            logger.info(f"Trying fallback directory: {fallback}")
            validated_dir = self._validate_directory(fallback)
            if validated_dir:
                return validated_dir

        # Last resort: use temp directory
        temp_dir = Path(tempfile.gettempdir()) / "youtube_music"
        logger.warning(f"All fallbacks failed, using temporary directory: {temp_dir}")
        return self._validate_directory(temp_dir) or temp_dir

    def get_default_video_dir(self) -> Path:
        """Get the default video directory based on the operating system.

        Returns the platform-appropriate video directory with validation
        and fallback mechanisms. Attempts multiple locations in order:
        1. Primary OS-specific video directory (Videos on Windows/Linux, Movies on macOS)
        2. Downloads/Videos subdirectory
        3. Custom youtube_downloads/videos directory
        4. Current working directory/downloads/videos
        5. Temporary directory as last resort

        Returns:
            Path object for a validated, writable video directory.
        """
        # Primary directories based on OS
        if self.platform == "Windows":
            primary_dir = Path.home() / "Videos"
        elif self.platform == "Darwin":  # macOS
            primary_dir = Path.home() / "Movies"
        else:  # Linux and others
            primary_dir = Path.home() / "Videos"

        # Try primary directory
        validated_dir = self._validate_directory(primary_dir)
        if validated_dir:
            return validated_dir

        # Fallback options
        fallback_dirs = [
            Path.home() / "Downloads" / "Videos",
            Path.home() / "youtube_downloads" / "videos",
            Path.cwd() / "downloads" / "videos"
        ]

        for fallback in fallback_dirs:
            logger.info(f"Trying fallback directory: {fallback}")
            validated_dir = self._validate_directory(fallback)
            if validated_dir:
                return validated_dir

        # Last resort: use temp directory
        temp_dir = Path(tempfile.gettempdir()) / "youtube_videos"
        logger.warning(f"All fallbacks failed, using temporary directory: {temp_dir}")
        return self._validate_directory(temp_dir) or temp_dir

    def validate_ffmpeg_executable(self, ffmpeg_path: str) -> Optional[str]:
        """
        Validate that FFmpeg executable exists and is actually executable.

        Args:
            ffmpeg_path: String or Path to FFmpeg executable

        Returns:
            Validated path as string if valid, None otherwise
        """
        try:
            # Try to find in PATH first
            which_result = shutil.which(ffmpeg_path)
            if which_result:
                path_obj = Path(which_result).resolve()

                # Verify it's a file
                if not path_obj.is_file():
                    logger.warning(f"FFmpeg path is not a file: {path_obj}")
                    return None

                # Check if executable
                if not os.access(path_obj, os.X_OK):
                    logger.warning(f"FFmpeg file is not executable: {path_obj}")
                    return None

                logger.info(f"FFmpeg validated in PATH: {path_obj}")
                return str(path_obj)

            # If not in PATH, try direct path
            path_obj = Path(ffmpeg_path).resolve()

            # Check if file exists
            if not path_obj.exists():
                logger.warning(f"FFmpeg not found at path: {path_obj}")
                return None

            # Verify it's a file
            if not path_obj.is_file():
                logger.warning(f"FFmpeg path is not a file: {path_obj}")
                return None

            # Check if executable (on Unix-like systems)
            if self.platform != "Windows" and not os.access(path_obj, os.X_OK):
                logger.warning(f"FFmpeg file is not executable: {path_obj}")
                return None

            logger.info(f"FFmpeg validated at direct path: {path_obj}")
            return str(path_obj)

        except Exception as e:
            logger.error(f"Error validating FFmpeg path {ffmpeg_path}: {e}")
            return None

    def get_ffmpeg_path(self) -> str:
        """Get the FFmpeg path based on the operating system.

        Searches for FFmpeg in multiple locations with validation:
        - Windows: Local installation, PATH, common install directories
        - Linux/macOS: System PATH, /usr/bin, /usr/local/bin, Homebrew locations

        All paths are validated to ensure the executable exists and is
        actually executable before being returned.

        Returns:
            String path to validated FFmpeg executable, or default name
            if not found (validation will occur at usage time).
        """
        if self.platform == "Windows":
            # Try local installation first
            local_path = Path("./ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe")
            validated = self.validate_ffmpeg_executable(str(local_path))
            if validated:
                return validated

            # Try PATH
            validated = self.validate_ffmpeg_executable("ffmpeg.exe")
            if validated:
                return validated

            # Try common installation locations
            common_paths = [
                Path("C:/ffmpeg/bin/ffmpeg.exe"),
                Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
            ]
            for path in common_paths:
                validated = self.validate_ffmpeg_executable(str(path))
                if validated:
                    return validated
        else:
            # On Linux/Mac, check PATH first
            validated = self.validate_ffmpeg_executable("ffmpeg")
            if validated:
                return validated

            # Try common installation locations
            common_paths = [
                Path("/usr/bin/ffmpeg"),
                Path("/usr/local/bin/ffmpeg"),
                Path("/opt/homebrew/bin/ffmpeg"),  # macOS Homebrew on Apple Silicon
                Path("/usr/local/Cellar/ffmpeg"),   # macOS Homebrew
            ]
            for path in common_paths:
                validated = self.validate_ffmpeg_executable(str(path))
                if validated:
                    return validated

        # Return default and let validation happen at usage time
        logger.warning("FFmpeg not found in standard locations")
        return "ffmpeg" if self.platform != "Windows" else "ffmpeg.exe"
