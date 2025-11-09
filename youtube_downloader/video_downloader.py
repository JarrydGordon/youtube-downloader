"""Video downloader GUI for YouTube."""

import tkinter as tk
from tkinter import ttk
import threading
import logging
from datetime import datetime
from pathlib import Path

from .base_gui import BaseYouTubeDownloaderGUI
from .config import Config


class YouTubeVideoDownloaderGUI(BaseYouTubeDownloaderGUI):
    """GUI application for downloading YouTube videos."""

    def __init__(self, root):
        config = Config()
        super().__init__(root, "YouTube Video Downloader (1080p)", config.get_default_video_dir())
        self.setup_logging()
        self.create_widgets()

    def setup_logging(self):
        """Set up logging for the application."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=log_dir / f"downloader_{datetime.now():%Y%m%d}.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def create_widgets(self):
        """Create all widgets for the video downloader."""
        self.create_base_widgets()

        # Progress Bar
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(fill=tk.X, padx=10, pady=(5,0))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           mode='determinate')
        self.progress_bar.pack(fill=tk.X)

        self.status_label = ttk.Label(progress_frame, text="")
        self.status_label.pack(fill=tk.X, pady=(2,0))

        # Download Button
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        self.download_btn = ttk.Button(button_frame, text="Download Video (1080p)",
                                      command=self.download)
        self.download_btn.pack()

        # Adjust window size for progress bar
        self.root.geometry("600x200")

    def download_hook(self, d):
        """Hook for download progress updates."""
        if d['status'] == 'downloading':
            try:
                # Calculate progress percentage
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total_bytes:
                    progress = (downloaded / total_bytes) * 100
                    speed = d.get('speed', 0)
                    if speed:
                        speed_mb = speed / 1024 / 1024  # Convert to MB/s
                        eta = d.get('eta', 0)
                        status_text = f'Downloading: {progress:.1f}% (Speed: {speed_mb:.1f} MB/s, ETA: {eta}s)'
                    else:
                        status_text = f'Downloading: {progress:.1f}%'

                    # Update progress bar in main thread
                    self.root.after(0, lambda: self.update_progress(progress, status_text))
            except Exception as e:
                logging.error(f"Error updating progress: {str(e)}")
        elif d['status'] == 'finished':
            logging.info("Download completed!")
            self.root.after(0, lambda: self.update_progress(100, "Download complete!"))

    def update_progress(self, progress, status_text):
        """Update the progress bar and status label."""
        self.progress_var.set(progress)
        self.status_label.config(text=status_text)
        self.root.update_idletasks()

    def download(self):
        """Start the video download process."""
        url = self.url_entry.get().strip()
        self.download_btn.config(state='disabled')
        logging.info("Starting download...")

        ydl_opts = {
            'format': 'bv*[height<=1080]+ba/b[height<=1080]',
            'progress_hooks': [self.download_hook],
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'concurrent_fragment_downloads': 3,
            'postprocessor_args': ['-c:v', 'copy', '-c:a', 'copy'],
        }

        threading.Thread(target=self.download_worker, args=(url, ydl_opts),
                        daemon=True).start()


def main():
    """Main entry point for video downloader."""
    root = tk.Tk()
    app = YouTubeVideoDownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
