#!/usr/bin/env python3
"""
Streamlit app: Download video only using yt-dlp.
Use this only for videos you own or have permission to download.
"""

import os
import threading
from pathlib import Path
import subprocess
import streamlit as st

try:
    from yt_dlp import YoutubeDL
except Exception:
    st.error("yt-dlp not installed. Install with: pip install yt-dlp")
    st.stop()

# --- Helpers ---
def ffmpeg_available() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False

def build_opts(output_template: str, cookies_path: str | None) -> dict:
    opts = {
        "outtmpl": output_template,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "retries": 3,
        "continuedl": True,
        "ignoreerrors": False,
    }
    if cookies_path:
        opts["cookiefile"] = cookies_path
    return opts

def progress_hook(d: dict):
    status = d.get("status")
    if status == "downloading":
        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        downloaded = d.get("downloaded_bytes", 0)
        pct = int(downloaded * 100 / total) if total else 0
        st.session_state.progress_pct = pct
        st.session_state.progress_msg = f"{pct}% downloaded"
    elif status == "finished":
        st.session_state.progress_pct = 100
        st.session_state.progress_msg = "Download finished"
    elif status == "error":
        st.session_state.progress_msg = "Error during download"

def download_worker(url: str, out_dir: str, filename_template: str, cookies_path: str | None):
    output_template = os.path.join(out_dir, filename_template)
    opts = build_opts(output_template, cookies_path)
    opts["progress_hooks"] = [progress_hook]
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
        st.session_state.download_info = info
        st.session_state.progress_msg = "Download complete"
    except Exception as e:
        st.session_state.progress_msg = f"Download failed: {e}"

# --- UI ---
st.set_page_config(page_title="Video Downloader", layout="centered")
st.title("Video Downloader (yt-dlp)")

st.markdown("**Reminder:** Only download videos you own or have explicit permission to download.")

with st.sidebar:
    out_dir = st.text_input("Output directory", value="downloads")
    filename_template = st.text_input("Filename template", value="%(title)s - %(id)s.%(ext)s")
    use_cookies = st.checkbox("Use cookies file (for private videos)", value=False)
    cookies_file = None
    if use_cookies:
        cookies_file = st.file_uploader("Upload cookies.txt", type=["txt"])
    st.markdown("---")
    if ffmpeg_available():
        st.success("ffmpeg found")
    else:
        st.warning("ffmpeg not found. Install it for merging audio/video.")

url = st.text_input("Video URL")
confirm = st.checkbox("I confirm I have permission to download this content", value=False)
start_btn = st.button("Start Download")

# Session state init
if "progress_pct" not in st.session_state:
    st.session_state.progress_pct = 0
    st.session_state.progress_msg = ""
    st.session_state.download_info = None

if start_btn:
    if not url:
        st.warning("Please enter a video URL.")
    elif not confirm:
        st.warning("You must confirm you have permission.")
    else:
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        cookies_path = None
        if cookies_file is not None:
            tmp_path = Path(out_dir) / "cookies.txt"
            with open(tmp_path, "wb") as f:
                f.write(cookies_file.getbuffer())
            cookies_path = str(tmp_path)
        worker = threading.Thread(target=download_worker, args=(url, out_dir, filename_template, cookies_path), daemon=True)
        worker.start()
        st.info("Download started...")

st.progress(st.session_state.progress_pct)
st.write(st.session_state.progress_msg)

if st.session_state.download_info:
    info = st.session_state.download_info
    st.success(f"Downloaded: {info.get('title')} by {info.get('uploader')}")
    out_dir_path = Path(out_dir)
    candidates = list(out_dir_path.glob(f"*{info.get('id','')}*"))
    if candidates:
        final_path = max(candidates, key=lambda p: p.stat().st_mtime)
        st.write("Saved to:", final_path)
        if final_path.stat().st_size < 200*1024*1024:  # only stream small files
            with open(final_path, "rb") as fh:
                st.download_button("Download file", data=fh, file_name=final_path.name)
        else:
            st.info("File is large; download directly from server filesystem.")
