#!/usr/bin/env python3
"""
Streamlit app: Download video + subtitles using yt-dlp (only for content you own or have permission to download).

Improvements over basic example:
 - Runs yt-dlp in a background thread (non-blocking UI)
 - Uses yt_dlp progress hooks to update UI via session_state
 - Handles cookies upload safely via tempfile
 - Avoids loading very large files into memory for download_button
 - Provides clear status, logs, and post-download file listing
 - Cleans up temporary cookies file
"""

import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any

import streamlit as st

# Try import yt_dlp; show helpful message if missing
try:
    from yt_dlp import YoutubeDL
except Exception:
    st.error(
        "yt-dlp is not installed in the environment. Install with:\n\n"
        "`pip install git+https://github.com/yt-dlp/yt-dlp.git` or `pip install yt-dlp`"
    )
    st.stop()

import subprocess

# ---------------------------
# Utility helpers
# ---------------------------

def ffmpeg_available() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False

def make_output_dir(base: str) -> Path:
    p = Path(base).expanduser().resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p

def build_ydl_opts(output_template: str,
                   download_subs: bool,
                   sub_lang: Optional[str],
                   allow_auto_subs: bool,
                   convert_subs: bool,
                   cookies_path: Optional[str]) -> Dict[str, Any]:
    opts: Dict[str, Any] = {
        "outtmpl": output_template,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "retries": 3,
        "continuedl": True,
        "ignoreerrors": False,
        # progress_hooks will be attached by caller
    }
    if download_subs:
        opts.update({
            "writesubtitles": True,
            "writeautomaticsub": allow_auto_subs,
            "subtitleslangs": [sub_lang] if sub_lang else ["all"],
            "subtitlesformat": "vtt",
        })
        if convert_subs:
            opts["convert_subtitles"] = "srt"
    if cookies_path:
        opts["cookiefile"] = cookies_path
    return opts

# ---------------------------
# Background download worker
# ---------------------------

def yt_dlp_progress_hook(d: dict):
    """
    Progress hook called by yt_dlp. Updates session_state keys:
      - progress_status (str)
      - progress_pct (int)
      - progress_message (str)
      - last_log (str)
    """
    status = d.get("status")
    if status == "downloading":
        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        downloaded = d.get("downloaded_bytes", 0)
        pct = int(downloaded * 100 / total) if total else 0
        st.session_state.progress_status = "downloading"
        st.session_state.progress_pct = pct
        st.session_state.progress_message = f"{d.get('filename','')} — {pct}% — ETA {d.get('eta','')}"
        st.session_state.last_log = f"downloading: {d.get('filename','')} {downloaded}/{total}"
    elif status == "finished":
        st.session_state.progress_status = "finished_fragment"
        st.session_state.progress_pct = 100
        st.session_state.progress_message = f"Finished fragment: {d.get('filename','')}"
        st.session_state.last_log = f"finished: {d.get('filename','')}"
    elif status == "error":
        st.session_state.progress_status = "error"
        st.session_state.progress_message = f"Error: {d.get('error','')}"
        st.session_state.last_log = f"error: {d.get('error','')}"

def download_worker(url: str,
                    out_dir: str,
                    filename_template: str,
                    download_subs: bool,
                    sub_lang: Optional[str],
                    allow_auto_subs: bool,
                    convert_subs: bool,
                    cookies_path: Optional[str]):
    """
    Runs in a background thread. Updates st.session_state with results.
    """
    st.session_state.progress_status = "starting"
    st.session_state.progress_pct = 0
    st.session_state.progress_message = "Preparing download..."
    st.session_state.last_log = ""

    output_template = os.path.join(out_dir, filename_template)
    opts = build_ydl_opts(output_template, download_subs, sub_lang, allow_auto_subs, convert_subs, cookies_path)

    # attach hook
    opts["progress_hooks"] = [yt_dlp_progress_hook]

    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as e:
        st.session_state.progress_status = "failed"
        st.session_state.progress_message = f"Download failed: {e}"
        st.session_state.last_log = str(e)
        st.session_state.download_info = None
        return

    st.session_state.progress_status = "done"
    st.session_state.progress_pct = 100
    st.session_state.progress_message = "Download completed"
    st.session_state.download_info = info

# ---------------------------
# Streamlit UI
# ---------------------------

st.set_page_config(page_title="Video + Subtitles Downloader", layout="centered")
st.title("Video + Subtitles Downloader (yt-dlp)")

st.markdown(
    "**Legal reminder:** Only download videos you own or have explicit permission to download. "
    "Downloading copyrighted content without permission may violate laws and site terms of service."
)

# Sidebar options
with st.sidebar:
    st.header("Options")
    out_dir_input = st.text_input("Output directory", value="downloads")
    filename_template = st.text_input("Filename template (yt-dlp)", value="%(title)s - %(id)s.%(ext)s")
    download_subs = st.checkbox("Download subtitles", value=True)
    sub_lang = st.text_input("Subtitle language (e.g., en) — leave blank for all", value="")
    allow_auto_subs = st.checkbox("Allow automatic (machine-generated) subtitles", value=True)
    convert_subs = st.checkbox("Convert subtitles to SRT after download", value=True)
    use_cookies = st.checkbox("Use cookies file (for private/authenticated downloads)", value=False)
    cookies_file = None
    if use_cookies:
        cookies_file = st.file_uploader("Upload cookies.txt (Netscape format)", type=["txt"])
    st.markdown("---")
    st.write("System checks")
    if ffmpeg_available():
        st.success("ffmpeg found")
    else:
        st.warning("ffmpeg not found. Merging/conversion may fail. Install ffmpeg and ensure it's in PATH.")

# Main inputs
url = st.text_input("Video URL (YouTube or supported site)", "")
confirm = st.checkbox("I confirm I have permission to download this content", value=False)

col1, col2 = st.columns([1, 1])
start_btn = col1.button("Start Download")
clear_btn = col2.button("Reset")

# Initialize session_state keys
if "progress_status" not in st.session_state:
    st.session_state.progress_status = "idle"
    st.session_state.progress_pct = 0
    st.session_state.progress_message = ""
    st.session_state.last_log = ""
    st.session_state.download_info = None
    st.session_state.worker_thread = None
    st.session_state.cookies_tmp = None

# Reset action
if clear_btn:
    # attempt to cleanup temp cookies
    try:
        if st.session_state.cookies_tmp and os.path.exists(st.session_state.cookies_tmp):
            os.remove(st.session_state.cookies_tmp)
    except Exception:
        pass
    for k in ["progress_status", "progress_pct", "progress_message", "last_log", "download_info", "worker_thread", "cookies_tmp"]:
        st.session_state[k] = None
    st.experimental_rerun()

# Start download
if start_btn:
    if not url:
        st.warning("Please enter a video URL.")
    elif not confirm:
        st.warning("You must confirm you have permission to download this content.")
    else:
        # prepare output dir
        out_dir = make_output_dir(out_dir_input)
        # handle cookies upload
        cookies_path = None
        if cookies_file is not None:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
            tmp.write(cookies_file.getbuffer())
            tmp.flush()
            tmp.close()
            cookies_path = tmp.name
            st.session_state.cookies_tmp = cookies_path

        # spawn background thread
        if st.session_state.worker_thread and st.session_state.worker_thread.is_alive():
            st.info("A download is already running. Please wait or reset.")
        else:
            st.session_state.progress_status = "queued"
            worker = threading.Thread(
                target=download_worker,
                args=(url, str(out_dir), filename_template, download_subs, sub_lang.strip() or None, allow_auto_subs, convert_subs, cookies_path),
                daemon=True
            )
            st.session_state.worker_thread = worker
            worker.start()
            st.success("Download started in background. Monitor progress below.")

# Progress UI
st.subheader("Progress")
st.progress(st.session_state.progress_pct or 0)
st.write(f"**Status:** {st.session_state.progress_status}")
if st.session_state.progress_message:
    st.write(st.session_state.progress_message)
if st.session_state.last_log:
    st.text_area("Log (latest)", value=st.session_state.last_log, height=120)

# If done, show results and files
if st.session_state.progress_status == "done" and st.session_state.download_info:
    info = st.session_state.download_info
    st.success("Download finished successfully.")
    st.write("**Title:**", info.get("title"))
    st.write("**Uploader:**", info.get("uploader"))
    st.write("**ID:**", info.get("id"))
    # try to locate files in out_dir
    out_dir = make_output_dir(out_dir_input)
    # find files matching id or title
    candidates = list(out_dir.glob(f"*{info.get('id','')}*"))
    if not candidates:
        sanitized = "".join(c for c in info.get("title","") if c.isalnum() or c in " -_").strip()
        candidates = list(out_dir.glob(f"*{sanitized}*"))
    if candidates:
        st.write("Files saved to output directory:")
        for p in sorted(candidates, key=lambda x: x.stat().st_mtime, reverse=True):
            size_mb = p.stat().st_size / (1024 * 1024)
            st.write(f"- **{p.name}** — {size_mb:.1f} MB — `{p}`")
            # Provide download button only for reasonably sized files (<200 MB)
            try:
                if p.stat().st_size < 200 * 1024 * 1024:
                    with open(p, "rb") as fh:
                        st.download_button(label=f"Download {p.name}", data=fh, file_name=p.name)
                else:
                    st.info("File is large; download from server filesystem or use SCP/HTTP to transfer.")
            except Exception as e:
                st.warning(f"Could not create download button for {p.name}: {e}")
    else:
        st.warning("Could not locate output files automatically. Check the output directory manually.")
    # list subtitle files
    subs = list(out_dir.glob(f"*{info.get('id','')}*.srt")) + list(out_dir.glob(f"*{info.get('id','')}*.vtt"))
    if subs:
        st.write("Subtitles:")
        for s in subs:
            st.write(f"- {s.name} — `{s}`")
            try:
                with open(s, "rb") as sf:
                    st.download_button(label=f"Download {s.name}", data=sf, file_name=s.name)
            except Exception:
                st.write("Download via server file access if button not available.")
    # cleanup cookies temp if any
    if st.session_state.cookies_tmp:
        try:
            os.remove(st.session_state.cookies_tmp)
            st.session_state.cookies_tmp = None
        except Exception:
            pass

# If failed
if st.session_state.progress_status == "failed":
    st.error(st.session_state.progress_message or "Download failed. See logs above.")

# Footer / notes
st.markdown("---")
st.markdown(
    "**Notes & recommendations**\n\n"
    "- This app is intended for lawful downloads only (your content or permitted content).\n"
    "- For private videos, use a cookies.txt exported from your browser (Netscape format).\n"
    "- For very large files, prefer transferring from the server (SCP/HTTP) rather than streaming through the browser.\n"
    "- If deploying publicly, add authentication and resource limits to prevent abuse."
)
