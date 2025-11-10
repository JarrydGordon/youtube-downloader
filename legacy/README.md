# Legacy Files

This directory contains deprecated files that are kept for backward compatibility only.

## Deprecated Files

### YT_Audio.py
This file provided an entry point for the audio downloader and is now deprecated.

**Migration Guide:**
- Use the console script: `yt-audio` (recommended)
- Or use the module: `python -m youtube_downloader.audio_downloader`

### YT_Video.py
This file provided an entry point for the video downloader and is now deprecated.

**Migration Guide:**
- Use the console script: `yt-video` (recommended)
- Or use the module: `python -m youtube_downloader.video_downloader`
- Or use the package module: `python -m youtube_downloader` (recommended for all use cases)

## Why These Files Are Deprecated

The original entry point files (YT_Audio.py and YT_Video.py) have been replaced with:

1. **Console Scripts**: Direct command-line executables (`yt-audio`, `yt-video`)
   - Easier to use from the command line
   - Better integration with system PATH
   - More discoverable for end users

2. **Package Modules**: Proper `__main__.py` files and module-based entry points
   - Follow Python packaging best practices
   - Support running with `python -m`
   - Better organized project structure

## Removal Timeline

These files will be removed in a future major version. Users should migrate to the console scripts or module-based approach immediately.

## Support

If you need help migrating from the deprecated entry points, please refer to the main README.md or CONTRIBUTING.md in the project root.
