import streamlit as st
import yt_dlp

st.title("🎥 YouTube Downloader (yt-dlp)")

url = st.text_input("Enter YouTube video URL:")
download_type = st.radio("Choose download type:", ["Video", "Audio"])

if st.button("Download"):
    if url:
        try:
            ydl_opts = {}
            if download_type == "Audio":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            else:
                ydl_opts = {'format': 'best'}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            st.success("✅ Download completed! File saved in current directory.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a valid YouTube URL.")
