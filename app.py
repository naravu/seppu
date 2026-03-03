import streamlit as st
from gtts import gTTS
import os

st.set_page_config(page_title="Indic TTS Web App", page_icon="🎙️")

st.title("🎙️ Multi-Language Text-to-Speech")
st.write("Enter text and select a language to generate speech.")

# Updated language mapping including Telugu
languages = {
    "English": "en",
    "Hindi (हिन्दी)": "hi",
    "Tamil (தமிழ்)": "ta",
    "Telugu (తెలుగు)": "te",      # Telugu added here
    "Kannada (ಕನ್ನಡ)": "kn",
    "Malayalam (മലയാളం)": "ml"
}

# Sidebar for options
selected_lang_name = st.selectbox("Choose Language:", list(languages.keys()))
lang_code = languages[selected_lang_name]

# Text Input
text_input = st.text_area(
    "Enter your text:", 
    placeholder=f"Type something in {selected_lang_name} here...",
    height=150
)

if st.button("Convert to Speech"):
    if text_input.strip():
        with st.spinner(f"Generating {selected_lang_name} audio..."):
            try:
                # Initialize gTTS
                tts = gTTS(text=text_input, lang=lang_code, slow=False)
                
                # Save as temporary file
                audio_file = "output_speech.mp3"
                tts.save(audio_file)
                
                # Display result
                st.success("Done!")
                st.audio(audio_file, format="audio/mp3")
                
                # Download button
                with open(audio_file, "rb") as file:
                    st.download_button(
                        label="Download MP3",
                        data=file,
                        file_name=f"{selected_lang_name}_speech.mp3",
                        mime="audio/mp3"
                    )
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter some text first.")
