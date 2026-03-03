import streamlit as st
import edge_tts
import asyncio
import os
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# 1. Page Configuration & Mobile-Friendly CSS
st.set_page_config(page_title="Indic Voice AI", page_icon="🎙️", layout="centered")

st.markdown("""
    <style>
    /* Make buttons full width on mobile */
    div.stButton > button:first-child {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
    }
    /* Responsive text area */
    .stTextArea textarea {
        font-size: 16px !important;
    }
    /* Hide Streamlit footer for a cleaner look */
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. Optimized Resource Loading
@st.cache_resource
def get_translator(target_code):
    return GoogleTranslator(source='auto', target=target_code)

# 3. Data Mapping
LANG_MAP = {
    "Hindi": {"code": "hi", "script": sanscript.DEVANAGARI, "Female": "hi-IN-SwaraNeural", "Male": "hi-IN-MadhurNeural"},
    "Tamil": {"code": "ta", "script": sanscript.TAMIL, "Female": "ta-IN-PallaviNeural", "Male": "ta-IN-ValluvarNeural"},
    "Telugu": {"code": "te", "script": sanscript.TELUGU, "Female": "te-IN-ShrutiNeural", "Male": "te-IN-MohanNeural"},
    "Kannada": {"code": "kn", "script": sanscript.KANNADA, "Female": "kn-IN-SapnaNeural", "Male": "kn-IN-GaganNeural"},
    "Malayalam": {"code": "ml", "script": sanscript.MALAYALAM, "Female": "ml-IN-SobhanaNeural", "Male": "ml-IN-MidhunNeural"},
    "English": {"code": "en", "script": None, "Female": "en-IN-NeerjaNeural", "Male": "en-IN-PrabhatNeural"}
}

# 4. App UI
st.title("🎙️ Indic Voice AI")
st.caption("Translate, Transliterate & Speak in Indian Languages")

# Responsive columns
col_a, col_b = st.columns([2, 1])
with col_a:
    target_lang = st.selectbox("Language", list(LANG_MAP.keys()))
with col_b:
    gender = st.selectbox("Voice", ["Female", "Male"])

mode = st.tabs(["🌐 Translation", "⌨️ Transliteration"])

# 5. Logic Engine
async def generate_voice(text, voice_name):
    output_path = "speech.mp3"
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_path)
    return output_path

with mode[0]:
    input_text = st.text_area("Type in English:", placeholder="How are you?", key="trans_in")
    btn_label = "Translate & Speak"

with mode[1]:
    # Instructions for Phonetic typing
    if target_lang != "English":
        st.info("Type phonetically (e.g., 'namaste')")
    input_text_p = st.text_area(f"Type {target_lang} phonetically:", placeholder="namaste", key="phono_in")
    btn_label_p = "Transliterate & Speak"

# Common execution trigger
if st.button("🚀 Generate Audio"):
    active_text = input_text if input_text else input_text_p
    
    if active_text.strip():
        try:
            info = LANG_MAP[target_lang]
            
            # Step A: Text Processing
            if input_text: # Translation Mode
                final_text = get_translator(info["code"]).translate(active_text)
            else: # Transliteration Mode
                final_text = transliterate(active_text, sanscript.ITRANS, info["script"]) if info["script"] else active_text

            # Step B: UI Feedback
            st.subheader("Output Text:")
            st.code(final_text, language=None)
            
            # Step C: Voice Generation
            with st.spinner("Processing Voice..."):
                voice = info[gender]
                audio_path = asyncio.run(generate_voice(final_text, voice))
                st.audio(audio_path)
                
                with open(audio_path, "rb") as f:
                    st.download_button("📥 Download MP3", f, file_name=f"{target_lang}.mp3")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter some text first.")
