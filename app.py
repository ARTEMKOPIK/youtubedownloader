import os
import tempfile
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import yt_dlp

app = Flask(__name__)
app.secret_key = "change-me"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    quality = request.form.get('quality', 'best')
    if not url:
        flash('Please provide a YouTube URL.')
        return redirect(url_for('index'))
    # Create a temporary directory to store the download
    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
            'quiet': True,
        }
        if quality == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            })
        elif quality in {'1080p', '720p', '480p'}:
            ydl_opts['format'] = (
                f"bestvideo[height<={quality.rstrip('p')}]" + "+bestaudio/best"
            )
            ydl_opts['merge_output_format'] = 'mp4'
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
