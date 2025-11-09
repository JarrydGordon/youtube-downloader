"""Backward compatibility wrapper for video downloader.

DEPRECATED: This file is kept for backward compatibility.
Please use 'python -m youtube_downloader.video_downloader' or 'yt-video' instead.
"""

import sys
import tkinter as tk
from youtube_downloader.video_downloader import YouTubeVideoDownloaderGUI


def main():
    """Main entry point for backward compatibility."""
    print("Warning: YT_Video.py is deprecated. Please use 'yt-video' command instead.")
    root = tk.Tk()
    app = YouTubeVideoDownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
