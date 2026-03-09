import streamlit as st
from pytube import YouTube

st.title("🎥 Simple YouTube Downloader")

# Input fields
url = st.text_input("Enter YouTube video URL:")
download_type = st.radio("Choose download type:", ["Video", "Audio"])

if st.button("Download"):
    if url:
        try:
            yt = YouTube(url)
            st.write(f"**Title:** {yt.title}")
            st.write("Fetching stream...")

            if download_type == "Video":
                stream = yt.streams.get_highest_resolution()
            else:
                stream = yt.streams.filter(only_audio=True).first()

            st.write("Downloading...")
            stream.download()
            st.success("✅ Download completed! File saved in current directory.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a valid YouTube URL.")
