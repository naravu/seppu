import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
import tempfile, os
import imageio_ffmpeg as ffmpeg

# Point pydub to ffmpeg binaries
AudioSegment.converter = ffmpeg.get_ffmpeg_exe()
AudioSegment.ffprobe   = ffmpeg.get_ffprobe_exe()

st.title("🎙️ MP3 Speech-to-Text (Traditional Method)")
st.write("Upload an MP3 file and get the transcription using SpeechRecognition + Google API.")

uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_file.write(uploaded_file.read())
        mp3_path = tmp_file.name

    wav_path = mp3_path.replace(".mp3", ".wav")
    sound = AudioSegment.from_mp3(mp3_path)
    sound.export(wav_path, format="wav")

    st.info("Transcribing... please wait.")

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            text = "Sorry, could not understand the audio."
        except sr.RequestError:
            text = "API unavailable or network error."

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
