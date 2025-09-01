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

## Updating dependencies

To update Python package versions:

1. Edit `requirements.txt` and set the desired versions, e.g. `Flask==3.0.0`.
2. Install the new versions:

```bash
pip install --upgrade -r requirements.txt
```

This ensures the project uses the specified versions.
