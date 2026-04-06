import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os

st.title("🎙️ MP3 Speech-to-Text (Classic Python Method)")
st.write("Upload an MP3 file and get the transcription using SpeechRecognition (Google Web Speech API).")

uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])

if uploaded_file is not None:
    # Save uploaded MP3 temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_file.write(uploaded_file.read())
        mp3_path = tmp_file.name

    # Convert MP3 → WAV using pydub (with ffmpeg-python backend)
    wav_path = mp3_path.replace(".mp3", ".wav")
    sound = AudioSegment.from_file(mp3_path, format="mp3")
    sound.export(wav_path, format="wav")

    st.info("Transcribing... please wait.")

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)  # No API key needed
        except sr.UnknownValueError:
            text = "Sorry, could not understand the audio."
        except sr.RequestError:
            text = "Google Speech API unavailable or network error."

    # Clean up temp files
    os.remove(mp3_path)
    os.remove(wav_path)

    st.subheader("Transcription:")
    st.text_area("Output", text, height=300)

    st.download_button(
        label="Download transcription as TXT",
        data=text,
        file_name="transcription.txt",
        mime="text/plain"
    )
