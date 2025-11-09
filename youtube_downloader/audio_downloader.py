"""Audio downloader GUI for YouTube."""

import tkinter as tk
from tkinter import ttk
import threading

from .base_gui import BaseYouTubeDownloaderGUI
from .config import Config


class YouTubeAudioDownloaderGUI(BaseYouTubeDownloaderGUI):
    """GUI application for downloading YouTube audio."""

    def __init__(self, root):
        config = Config()
        super().__init__(root, "YouTube Audio Downloader", config.get_default_music_dir())
        self.create_widgets()

    def create_widgets(self):
        """Create all widgets for the audio downloader."""
        self.create_base_widgets()

        # Playlist checkbox
        self.playlist_var = tk.BooleanVar()
        self.playlist_check = ttk.Checkbutton(
            self.root,
            text="Download Playlist",
            variable=self.playlist_var,
            style="TCheckbutton"
        )
        self.playlist_check.pack(pady=(0,5))

        # Download Button
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=5)
        self.download_btn = ttk.Button(button_frame, text="Download Audio",
                                      command=self.download)
        self.download_btn.pack()

        # Adjust window size
        self.root.geometry("600x180")

    def validate_url(self, url):
        """Validate URL and check for playlist if playlist mode is enabled."""
        super().validate_url(url)

        # Verify playlist URL if playlist mode is selected
        if self.playlist_var.get() and "list=" not in url:
            raise ValueError("Not a valid YouTube playlist URL")

    def download_hook(self, d):
        """Hook for download progress updates."""
        if d['status'] == 'finished':
            pass

    def download(self):
        """Start the audio download process."""
        url = self.url_entry.get().strip()
        self.download_btn.config(state='disabled')

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'progress_hooks': [self.download_hook],
            'noplaylist': not self.playlist_var.get()
        }

        threading.Thread(target=self.download_worker, args=(url, ydl_opts),
                        daemon=True).start()


def main():
    """Main entry point for audio downloader."""
    root = tk.Tk()
    app = YouTubeAudioDownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
