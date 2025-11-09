"""Base GUI class with shared functionality for YouTube downloaders."""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import validators
from pathlib import Path
import yt_dlp

from .config import Config


class BaseYouTubeDownloaderGUI:
    """Base class for YouTube downloader GUI applications."""

    def __init__(self, root, title, output_dir):
        self.root = root
        self.root.title(title)
        self.root.geometry("600x150")

        # Configure dark theme
        self.style = ttk.Style()
        self.style.configure(".", background="#2b2b2b", foreground="#ffffff")
        self.style.configure("TFrame", background="#2b2b2b")
        self.style.configure("TLabel", background="#2b2b2b", foreground="#ffffff")
        self.style.configure("TButton", background="#ffffff", foreground="#000000",
                           padding=5, font=("TkDefaultFont", 9, "bold"))
        self.style.configure("TCheckbutton", background="#2b2b2b", foreground="#ffffff")

        self.root.configure(bg="#2b2b2b")

        self.config = Config()
        self.output_dir = output_dir

    def create_base_widgets(self):
        """Create the base widgets shared by all downloaders."""
        # URL Input
        input_frame = ttk.Frame(self.root)
        input_frame.pack(padx=10, pady=(10,0), fill=tk.X)

        ttk.Label(input_frame, text="YouTube URL:").pack(side=tk.LEFT)

        # Custom Entry widget with dark theme
        self.url_entry = tk.Entry(
            input_frame,
            bg="#1e1e1e",
            fg="#ffffff",
            insertbackground="#ffffff",
            selectbackground="#ff0000",
            selectforeground="#000000",
            relief="flat",
            highlightthickness=1,
            highlightcolor="#404040",
            highlightbackground="#404040",
            font=("Segoe UI", 10)
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,5))

        # Paste URL button
        paste_btn = ttk.Button(input_frame, text="Paste URL", command=self.paste_url)
        paste_btn.pack(side=tk.LEFT)

        # Output Directory Label
        self.dir_label = ttk.Label(self.root, text=f"Output: {self.output_dir}")
        self.dir_label.pack(padx=10, pady=5, anchor='w')

    def validate_url(self, url):
        """Validate that the URL is a valid YouTube URL."""
        if not url or not validators.url(url):
            raise ValueError("Please enter a valid YouTube URL")
        if "youtube.com" not in url and "youtu.be" not in url:
            raise ValueError("Not a YouTube URL")

    def paste_url(self):
        """Paste URL from clipboard into the entry field."""
        try:
            clipboard_text = self.root.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard_text)
        except tk.TclError:
            messagebox.showwarning("Paste Error", "No text found in clipboard")

    def download_worker(self, url, ydl_opts):
        """Worker thread for downloading content."""
        try:
            self.validate_url(url)

            ffmpeg_path = self.config.get_ffmpeg_path()
            if ffmpeg_path.startswith("./") and not Path(ffmpeg_path).exists():
                raise RuntimeError("FFmpeg not found - please check installation")

            ydl_opts['ffmpeg_location'] = ffmpeg_path
            ydl_opts['outtmpl'] = str(self.output_dir / '%(title)s.%(ext)s')

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.root.after(0, lambda: messagebox.showinfo("Success",
                                                           "Download completed successfully!"))

        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            self.root.after(0, lambda: self.download_btn.config(state='normal'))
