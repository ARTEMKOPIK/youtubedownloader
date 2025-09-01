# YouTube Downloader

Simple web application built with Flask and yt-dlp to download videos or audio from YouTube with selectable quality.

## Setup

This application requires [ffmpeg](https://ffmpeg.org) to merge video and audio streams.
Ensure it is installed and available in your PATH before running the app.

```bash
pip install -r requirements.txt
python app.py
```

Open your browser at `http://localhost:5000` and enter a YouTube URL. Choose the desired quality (video resolution or audio) and download the file.

### Playlists

Playlist URLs are detected automatically and downloaded in their entirety. The resulting files are packaged into a ZIP archive for download.

### Progress feedback

Downloads run in the background and the web interface polls the server for updates. A progress bar reflects the download status.

### Limitations

- Progress information is kept in memory and is lost if the server restarts.
- Large playlists may take significant time and disk space while preparing the ZIP archive.

