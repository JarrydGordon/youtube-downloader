import yt_dlp
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import re
from pathlib import Path
import logging
from datetime import datetime
import validators
import os

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader (1080p)")
        self.root.geometry("600x150")
        
        # Configure dark theme
        self.style = ttk.Style()
        self.style.configure(".", background="#2b2b2b", foreground="#ffffff")
        self.style.configure("TFrame", background="#2b2b2b")
        self.style.configure("TLabel", background="#2b2b2b", foreground="#ffffff")
        self.style.configure("TButton", background="#ffffff", foreground="#000000", padding=5, font=("TkDefaultFont", 9, "bold"))
        
        self.root.configure(bg="#2b2b2b")
        
        self.setup_logging()
        self.output_dir = Path("C:/Users/Jarry/Videos")
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
        
        # Progress Bar
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(fill=tk.X, padx=10, pady=(5,0))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, mode='determinate')
        self.progress_bar.pack(fill=tk.X)
        
        self.status_label = ttk.Label(progress_frame, text="")
        self.status_label.pack(fill=tk.X, pady=(2,0))
        
        # Download Button
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        self.download_btn = ttk.Button(button_frame, text="Download Video (1080p)", command=self.download)
        self.download_btn.pack()
        
        # Adjust window size for progress bar
        self.root.geometry("600x200")

    def setup_logging(self):
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=log_dir / f"downloader_{datetime.now():%Y%m%d}.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def validate_url(self, url):
        if not url or not validators.url(url):
            raise ValueError("Please enter a valid YouTube URL")
        if "youtube.com" not in url and "youtu.be" not in url:
            raise ValueError("Not a YouTube URL")

    def download_hook(self, d):
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
        self.progress_var.set(progress)
        self.status_label.config(text=status_text)
        self.root.update_idletasks()
        
    def paste_url(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard_text)
        except tk.TclError:
            messagebox.showwarning("Paste Error", "No text found in clipboard")

    def download_worker(self, url):
        try:
            self.validate_url(url)
            logging.info("Starting download...")
            
            ffmpeg_path = str(Path("./ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe"))
            if not Path(ffmpeg_path).exists():
                raise RuntimeError("FFmpeg not found - please check installation")

            ydl_opts = {
                'format': 'bv*[height<=1080]+ba/b[height<=1080]',  # More flexible format selection
                'ffmpeg_location': ffmpeg_path,
                'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
                'progress_hooks': [self.download_hook],
                'noplaylist': True,
                'merge_output_format': 'mp4',
                'concurrent_fragment_downloads': 3,
                'postprocessor_args': ['-c:v', 'copy', '-c:a', 'copy'],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.root.after(0, lambda: messagebox.showinfo("Success", "Video downloaded successfully!"))
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Download error: {error_msg}", exc_info=True)
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
