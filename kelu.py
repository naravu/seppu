import streamlit as st
import whisper
import tempfile
import os

# Load Whisper model once at startup
@st.cache_resource
def load_model():
    return whisper.load_model("base")  # you can use "small", "medium", "large"

model = load_model()

st.title("🎙️ MP3 Speech-to-Text with Whisper")

st.write("Upload an MP3 file and get the transcription using OpenAI's Whisper model.")

# File uploader
uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])

if uploaded_file is not None:
    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    st.info("Transcribing... this may take a moment.")

    # Run Whisper transcription
    result = model.transcribe(tmp_path)

    # Clean up temp file
    os.remove(tmp_path)

    # Display transcription
    st.subheader("Transcription:")
    st.text_area("Output", result["text"], height=300)

    # Option to download transcription
    st.download_button(
        label="Download transcription as TXT",
        data=result["text"],
        file_name="transcription.txt",
        mime="text/plain"
    )
