"""Main entry point for the youtube_downloader package.

This module allows running the youtube_downloader package as a module
using the command: python -m youtube_downloader

This will launch the YouTube Video Downloader GUI application.
"""

from .video_downloader import main


if __name__ == "__main__":
    main()
