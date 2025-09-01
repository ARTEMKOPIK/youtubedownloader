import os
import shutil
import tempfile
import uuid
from threading import Thread

from flask import (
    Flask,
    flash,
    jsonify,
    render_template,
    request,
    send_file,
    url_for,
    redirect,
)
import yt_dlp

app = Flask(__name__)
app.secret_key = "change-me"

# Stores progress information for active downloads
downloads = {}


def progress_hook(job_id):
    """Create a yt_dlp progress hook for a job id."""

    def hook(d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            if total:
                downloads[job_id]["progress"] = int(
                    d.get("downloaded_bytes", 0) * 100 / total
                )
        elif d.get("status") == "finished":
            downloads[job_id]["status"] = "processing"
            downloads[job_id]["filepath"] = d.get("filename")

    return hook


def run_download(job_id, url, quality):
    """Perform the actual download in a background thread."""

    downloads[job_id] = {"progress": 0, "status": "downloading", "filepath": None}
    tmpdir = tempfile.mkdtemp()
    try:
        # Detect whether the URL is a playlist
        with yt_dlp.YoutubeDL({"quiet": True}) as info_ydl:
            info = info_ydl.extract_info(url, download=False)
        is_playlist = isinstance(info, dict) and info.get("entries")

        ydl_opts = {
            "format": "best",
            "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
            "quiet": True,
            "progress_hooks": [progress_hook(job_id)],
            "noplaylist": not is_playlist,
        }
        if quality == "audio":
            ydl_opts.update(
                {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                }
            )
        elif quality in {"1080p", "720p", "480p"}:
            ydl_opts["format"] = (
                f"bestvideo[height<={quality.rstrip('p')}]" + "+bestaudio/best"
            )
            ydl_opts["merge_output_format"] = "mp4"

        if is_playlist:
            ydl_opts["outtmpl"] = os.path.join(
                tmpdir, "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s"
            )

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if is_playlist:
            archive_base = os.path.join(tmpdir, "playlist")
            zip_path = shutil.make_archive(archive_base, "zip", tmpdir)
            downloads[job_id]["filepath"] = zip_path

        downloads[job_id]["status"] = "finished"
    except Exception as exc:  # pragma: no cover - best effort
        downloads[job_id]["status"] = "error"
        downloads[job_id]["message"] = str(exc)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start_download():
    url = request.form.get("url")
    quality = request.form.get("quality", "best")
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    job_id = uuid.uuid4().hex
    thread = Thread(target=run_download, args=(job_id, url, quality), daemon=True)
    thread.start()
    return jsonify({"job_id": job_id})


@app.route("/progress/<job_id>")
def progress(job_id):
    info = downloads.get(job_id)
    if not info:
        return jsonify({"status": "unknown"}), 404
    return jsonify(info)


@app.route("/file/<job_id>")
def file(job_id):
    info = downloads.get(job_id)
    if not info or info.get("status") != "finished":
        flash("File not ready for download.")
        return redirect(url_for("index"))
    return send_file(info["filepath"], as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
