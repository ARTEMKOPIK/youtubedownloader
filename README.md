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

## Testing

Run the test suite with:

```bash
pytest
```
