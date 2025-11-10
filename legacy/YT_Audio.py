"""Backward compatibility wrapper for audio downloader.

DEPRECATED: This file is kept for backward compatibility.
Please use 'python -m youtube_downloader.audio_downloader' or 'yt-audio' instead.
"""

import sys
import tkinter as tk
from youtube_downloader.audio_downloader import YouTubeAudioDownloaderGUI


def main():
    """Main entry point for backward compatibility."""
    print("Warning: YT_Audio.py is deprecated. Please use 'yt-audio' command instead.")
    root = tk.Tk()
    app = YouTubeAudioDownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
