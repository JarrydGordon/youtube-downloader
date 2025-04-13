import yt_dlp
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import re
from pathlib import Path
import validators
import os

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Audio Downloader")
        self.root.geometry("600x180")  # Increased height for playlist checkbox
        
        # Configure dark theme
        self.style = ttk.Style()
        self.style.configure("TCheckbutton",
                           background="#2b2b2b",
                           foreground="#ffffff")
        self.style.configure(".", background="#2b2b2b", foreground="#ffffff")
        self.style.configure("TFrame", background="#2b2b2b")
        self.style.configure("TLabel", background="#2b2b2b", foreground="#ffffff")
        self.style.configure("TButton", background="#ffffff", foreground="#000000", padding=5, font=("TkDefaultFont", 9, "bold"))
        
        self.root.configure(bg="#2b2b2b")
        
        self.output_dir = Path("C:/Users/Jarry/Music")
        self.create_widgets()
        
    def create_widgets(self):
        # URL Input
        input_frame = ttk.Frame(self.root)
        input_frame.pack(padx=10, pady=(10,0), fill=tk.X)
        
        ttk.Label(input_frame, text="YouTube URL:").pack(side=tk.LEFT)
        
        # Custom Entry widget with dark theme
        self.url_entry = tk.Entry(input_frame,
                                bg="#1e1e1e",
                                fg="#ffffff",
                                insertbackground="#ffffff",
                                selectbackground="#ff0000",
                                selectforeground="#000000",
                                relief="flat",
                                highlightthickness=1,
                                highlightcolor="#404040",
                                highlightbackground="#404040",
                                font=("Segoe UI", 10))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,5))
        
        # Paste URL button
        paste_btn = ttk.Button(input_frame, text="Paste URL", command=self.paste_url)
        paste_btn.pack(side=tk.LEFT)
        
        # Output Directory Label
        self.dir_label = ttk.Label(self.root, text=f"Output: {self.output_dir}")
        self.dir_label.pack(padx=10, pady=5, anchor='w')
        
        # Download Button with black background and white text
        # Playlist checkbox
        self.playlist_var = tk.BooleanVar()
        self.playlist_check = ttk.Checkbutton(
            self.root,
            text="Download Playlist",
            variable=self.playlist_var,
            style="TCheckbutton"
        )
        self.playlist_check.pack(pady=(0,5))

        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=5)
        self.download_btn = ttk.Button(button_frame, text="Download Audio", command=self.download)
        self.download_btn.pack()

    def validate_url(self, url):
        if not url or not validators.url(url):
            raise ValueError("Please enter a valid YouTube URL")
        if "youtube.com" not in url and "youtu.be" not in url:
            raise ValueError("Not a YouTube URL")
        
        # Verify playlist URL if playlist mode is selected
        if self.playlist_var.get() and "list=" not in url:
            raise ValueError("Not a valid YouTube playlist URL")

    def paste_url(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard_text)
        except tk.TclError:
            messagebox.showwarning("Paste Error", "No text found in clipboard")

    def download_hook(self, d):
        if d['status'] == 'finished':
            pass

    def download_worker(self, url):
        try:
            self.validate_url(url)
            
            ffmpeg_path = str(Path("./ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe"))
            if not Path(ffmpeg_path).exists():
                raise RuntimeError("FFmpeg not found - please check installation")

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                'ffmpeg_location': ffmpeg_path,
                'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
                'progress_hooks': [self.download_hook],
                'noplaylist': not self.playlist_var.get()
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.root.after(0, lambda: messagebox.showinfo("Success", "Audio downloaded successfully!"))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            self.root.after(0, lambda: self.download_btn.config(state='normal'))

    def download(self):
        url = self.url_entry.get().strip()
        self.download_btn.config(state='disabled')
        threading.Thread(target=self.download_worker, args=(url,), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()
