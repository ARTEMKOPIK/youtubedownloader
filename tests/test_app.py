import os
import sys

import pytest
from flask import Response, get_flashed_messages

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import app as youtube_app


def test_successful_download(monkeypatch):
    class DummyYDL:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def extract_info(self, url, download):
            return {'id': '123', 'title': 'video', 'ext': 'mp4'}
        def prepare_filename(self, info):
            return 'dummy.mp4'

    def fake_send_file(filename, as_attachment=True):
        return Response('filedata', mimetype='text/plain')

    monkeypatch.setattr(youtube_app.yt_dlp, 'YoutubeDL', lambda opts: DummyYDL())
    monkeypatch.setattr(youtube_app, 'send_file', fake_send_file)

    client = youtube_app.app.test_client()
    response = client.post('/download', data={'url': 'https://youtu.be/test'})

    assert response.status_code == 200
    assert response.data == b'filedata'


def test_ffmpeg_missing_flash(monkeypatch):
    class DummyYDL:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def extract_info(self, url, download):
            raise youtube_app.yt_dlp.utils.DownloadError('ffmpeg not found')
        def prepare_filename(self, info):
            return 'dummy.mp4'

    monkeypatch.setattr(youtube_app.yt_dlp, 'YoutubeDL', lambda opts: DummyYDL())

    client = youtube_app.app.test_client()
    with client:
        response = client.post('/download', data={'url': 'https://youtu.be/test'}, follow_redirects=True)
        messages = get_flashed_messages()

    assert response.status_code == 200
    assert 'Failed to download video. Ensure ffmpeg is installed.' in messages
