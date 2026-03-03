import streamlit as st
import edge_tts
import asyncio
import os
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# 1. Page Config & Responsive CSS
st.set_page_config(page_title="Indic Voice AI", page_icon="🎙️", layout="centered")

st.markdown("""
    <style>
    /* Mobile-friendly button */
    div.stButton > button:first-child {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
    /* Larger text for mobile inputs */
    .stTextArea textarea { font-size: 16px !important; }
    /* Style the radio buttons container */
    div[data-testid="stRadio"] > div { flex-direction: row; gap: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Optimized Data Mapping
LANG_MAP = {
    "Hindi": {"code": "hi", "script": sanscript.DEVANAGARI, "Female": "hi-IN-SwaraNeural", "Male": "hi-IN-MadhurNeural"},
    "Tamil": {"code": "ta", "script": sanscript.TAMIL, "Female": "ta-IN-PallaviNeural", "Male": "ta-IN-ValluvarNeural"},
    "Telugu": {"code": "te", "script": sanscript.TELUGU, "Female": "te-IN-ShrutiNeural", "Male": "te-IN-MohanNeural"},
    "Kannada": {"code": "kn", "script": sanscript.KANNADA, "Female": "kn-IN-SapnaNeural", "Male": "kn-IN-GaganNeural"},
    "Malayalam": {"code": "ml", "script": sanscript.MALAYALAM, "Female": "ml-IN-SobhanaNeural", "Male": "ml-IN-MidhunNeural"},
    "English": {"code": "en", "script": None, "Female": "en-IN-NeerjaNeural", "Male": "en-IN-PrabhatNeural"}
}

# 3. Resource Functions
@st.cache_resource
def get_translator(target_code):
    return GoogleTranslator(source='auto', target=target_code)

async def generate_voice(text, voice_name):
    output_path = "speech.mp3"
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_path)
    return output_path

# 4. App UI
st.title("🎙️ Indic Voice AI")

# Sidebar for Voice Selection
with st.sidebar:
    st.header("Voice Settings")
    target_lang = st.selectbox("Language", list(LANG_MAP.keys()))
    gender = st.radio("Gender", ["Female", "Male"], horizontal=True)
    st.divider()
    st.info("Tip: Use 'Transliterate' to type Hindi/Tamil words using English letters (e.g., 'Vanakkam').")

# Main Selection: Radio Buttons for Mode
mode = st.radio("Select Input Mode:", ["Translate from English", "Transliterate (Phonetic)"], horizontal=True)

# Dynamic Placeholder
placeholder = "Enter English text to translate..." if "Translate" in mode else "Type phonetically (e.g., 'Namaste')..."
user_input = st.text_area("Input Text:", placeholder=placeholder, height=150)

# 5. Execution Logic
if st.button("🔊 Generate Audio"):
    if user_input.strip():
        try:
            info = LANG_MAP[target_lang]
            
            # Step A: Text Processing
            with st.spinner("Processing Text..."):
                if "Translate" in mode:
                    final_text = get_translator(info["code"]).translate(user_input)
                else:
                    # Transliterate ITRANS to Native Script
                    final_text = transliterate(user_input, sanscript.ITRANS, info["script"]) if info["script"] else user_input

            # Step B: Display Result
            st.subheader("Final Text:")
            st.success(final_text)
            
            # Step C: Voice Synthesis
            with st.spinner("Synthesizing Voice..."):
                voice = info[gender]
                audio_path = asyncio.run(generate_voice(final_text, voice))
                st.audio(audio_path)
                
                with open(audio_path, "rb") as f:
                    st.download_button("📥 Download MP3", f, file_name=f"{target_lang}_voice.mp3")
        
        except Exception as e:
            st.error(f"Execution Error: {e}")
    else:
        st.warning("Please enter some text first!")
