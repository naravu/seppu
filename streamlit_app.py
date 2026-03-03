import streamlit as st
import edge_tts
import asyncio
import os

st.set_page_config(page_title="Multi-Voice Indic TTS", page_icon="🎙️")
st.title("🎙️ Male & Female Indic TTS")

# Mapping languages to specific Microsoft Edge Male/Female voices
VOICE_MAPPING = {
    "English": {"Female": "en-IN-NeerjaNeural", "Male": "en-IN-PrabhatNeural"},
    "Hindi": {"Female": "hi-IN-SwaraNeural", "Male": "hi-IN-MadhurNeural"},
    "Tamil": {"Female": "ta-IN-PallaviNeural", "Male": "ta-IN-ValluvarNeural"},
    "Telugu": {"Female": "te-IN-ShrutiNeural", "Male": "te-IN-MohanNeural"},
    "Kannada": {"Female": "kn-IN-SapnaNeural", "Male": "kn-IN-GaganNeural"},
    "Malayalam": {"Female": "ml-IN-SobhanaNeural", "Male": "ml-IN-MidhunNeural"}
}

# UI components
selected_lang = st.selectbox("Select Language", list(VOICE_MAPPING.keys()))
gender = st.radio("Select Gender", ["Female", "Male"], horizontal=True)
voice = VOICE_MAPPING[selected_lang][gender]

text_input = st.text_area("Enter text:", height=150)

async def generate_speech(text, voice_name):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save("output.mp3")

if st.button("Generate Audio"):
    if text_input.strip():
        with st.spinner(f"Generating {gender} voice..."):
            asyncio.run(generate_speech(text_input, voice))
            st.audio("output.mp3", format="audio/mp3")
            with open("output.mp3", "rb") as f:
                st.download_button("Download MP3", f, file_name="speech.mp3")
    else:
        st.warning("Please enter text first.")
