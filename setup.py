"""Setup file for YouTube Downloader package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="youtube-downloader",
    version="1.0.0",
    author="Jarryd Gordon",
    description="A simple GUI application for downloading YouTube videos and audio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JarrydGordon/youtube-downloader",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "yt-dlp>=2023.0.0",
        "validators>=0.20.0",
    ],
    entry_points={
        "console_scripts": [
            "yt-audio=youtube_downloader.audio_downloader:main",
            "yt-video=youtube_downloader.video_downloader:main",
        ],
    },
)
