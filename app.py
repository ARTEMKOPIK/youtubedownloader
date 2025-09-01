import os
import tempfile
from flask import (
    Flask,
    render_template,
    request,
    send_file,
    redirect,
    url_for,
    flash,
    after_this_request,
)
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
    # Create a named temporary file to store the download
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_name = tmp_file.name
    tmp_file.close()
    try:
        os.remove(tmp_name)
    except OSError:
        pass

    ydl_opts = {
        'format': 'best',
        'outtmpl': tmp_name + '.%(ext)s',
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
        try:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        except yt_dlp.utils.DownloadError:
            flash('Failed to download video. Ensure ffmpeg is installed.')
            try:
                os.remove(tmp_name)
            except OSError:
                pass
            return redirect(url_for('index'))

    download_name = (
        f"{info.get('title', 'download')}.{info.get('ext', '')}".rstrip('.')
    )

    @after_this_request
    def remove_file(response):
        for path in (filename, tmp_name):
            try:
                os.remove(path)
            except OSError:
                pass
        return response

    return send_file(filename, as_attachment=True, download_name=download_name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
