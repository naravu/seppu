import streamlit as st
import edge_tts
import asyncio
import os
import torch
from diffusers import StableDiffusionPipeline
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from PIL import Image

# 1. Page Config & Responsive CSS
st.set_page_config(page_title="Seppuga AI", page_icon="🎙️", layout="centered")

st.markdown("""
    <style>
    div.stButton > button:first-child {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
    .stTextArea textarea { font-size: 16px !important; }
    div[data-testid="stRadio"] > div { flex-direction: row; gap: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Optimized Data Mapping for Voice
LANG_MAP = {
    "Hindi": {"code": "hi", "script": sanscript.DEVANAGARI, "Female": "hi-IN-SwaraNeural", "Male": "hi-IN-MadhurNeural"},
    "Tamil": {"code": "ta", "script": sanscript.TAMIL, "Female": "ta-IN-PallaviNeural", "Male": "ta-IN-ValluvarNeural"},
    "Telugu": {"code": "te", "script": sanscript.TELUGU, "Female": "te-IN-ShrutiNeural", "Male": "te-IN-MohanNeural"},
    "Kannada": {"code": "kn", "script": sanscript.KANNADA, "Female": "kn-IN-SapnaNeural", "Male": "kn-IN-GaganNeural"},
    "Malayalam": {"code": "ml", "script": sanscript.MALAYALAM, "Female": "ml-IN-SobhanaNeural", "Male": "ml-IN-MidhunNeural"},
    "English": {"code": "en", "script": None, "Female": "en-IN-NeerjaNeural", "Male": "en-IN-PrabhatNeural"}
}

# 3. Resource Functions (Cached for Performance)
@st.cache_resource
def get_translator(target_code):
    return GoogleTranslator(source='auto', target=target_code)

@st.cache_resource
def load_image_pipeline():
    model_id = "runwayml/stable-diffusion-v1-5"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Use float16 for GPU to save memory, float32 for CPU
    dtype = torch.float16 if device == "cuda" else torch.float32
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype)
    return pipe.to(device)

async def generate_voice(text, voice_name):
    output_path = "speech.mp3"
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_path)
    return output_path

# 4. App UI - Navigation
st.title("🎙️ Seppuga AI")
tab1, tab2 = st.tabs(["🔊 Text-to-Speech", "🎨 Text-to-Image"])

# --- TAB 1: TEXT TO SPEECH ---
with tab1:
    with st.sidebar:
        st.header("Voice Settings")
        target_lang = st.selectbox("Language", list(LANG_MAP.keys()))
        gender = st.radio("Gender", ["Female", "Male"], horizontal=True)
        st.divider()
        st.info("Tip: Use 'Transliterate' for phonetic typing.")

    mode = st.radio("Select Input Mode:", ["Translate from English", "Transliterate (Phonetic)"], horizontal=True)
    placeholder = "Enter text..."
    user_input = st.text_area("Input Text:", placeholder=placeholder, height=150, key="tts_input")

    if st.button("🔊 Generate Audio"):
        if user_input.strip():
            try:
                info = LANG_MAP[target_lang]
                with st.spinner("Processing Text..."):
                    if "Translate" in mode:
                        final_text = get_translator(info["code"]).translate(user_input)
                    else:
                        final_text = transliterate(user_input, sanscript.ITRANS, info["script"]) if info["script"] else user_input

                st.subheader("Final Text:")
                st.success(final_text)
                
                with st.spinner("Synthesizing Voice..."):
                    voice = info[gender]
                    audio_path = asyncio.run(generate_voice(final_text, voice))
                    st.audio(audio_path)
                    with open(audio_path, "rb") as f:
                        st.download_button("📥 Download MP3", f, file_name=f"{target_lang}_voice.mp3")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter some text!")

# --- TAB 2: TEXT TO IMAGE ---
with tab2:
    st.header("AI Image Generator")
    img_prompt = st.text_area("Describe the image you want to create:", 
                              placeholder="A majestic elephant in a futuristic Indian city, digital art style",
                              key="img_input")
    
    if st.button("🎨 Generate Visual"):
        if img_prompt.strip():
            try:
                with st.spinner("Loading Model & Generating... (This takes time on CPU)"):
                    pipe = load_image_pipeline()
                    # Generate image
                    image = pipe(img_prompt).images[0]
                    
                    # Display Image
                    st.image(image, caption="Generated Result", use_container_width=True)
                    
                    # Save for download
                    image.save("generated_img.png")
                    with open("generated_img.png", "rb") as file:
                        st.download_button("📥 Download Image", file, "ai_image.png", "image/png")
            except Exception as e:
                st.error(f"Image Error: {e}")
        else:
            st.warning("Please enter a visual description!")
