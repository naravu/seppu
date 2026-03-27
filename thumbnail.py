import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# Title
st.title("🎨 Thumbnail Generator (English + Tamil)")

# Inputs
english_text = st.text_input("Enter English text", "Hello World")
tamil_text = st.text_input("Enter Tamil text", "வணக்கம் உலகம்")

# Font paths (safe absolute paths)
eng_font_path = os.path.join(os.path.dirname(__file__), "fonts", "Arial.ttf")
tam_font_path = os.path.join(os.path.dirname(__file__), "fonts", "NotoSansTamil-Regular.ttf")

# Check font existence
if not os.path.exists(eng_font_path):
    st.error("English font not found at: " + eng_font_path)
if not os.path.exists(tam_font_path):
    st.error("Tamil font not found at: " + tam_font_path)

# Load fonts safely
try:
    eng_font = ImageFont.truetype(eng_font_path, 60)
except OSError:
    st.warning("Could not load English font, using default.")
    eng_font = ImageFont.load_default()

try:
    tam_font = ImageFont.truetype(tam_font_path, 60)
except OSError:
    st.warning("Could not load Tamil font, using default.")
    tam_font = ImageFont.load_default()

# Base image
img = Image.new("RGB", (800, 400), color=(255, 255, 255))
draw = ImageDraw.Draw(img)

# Draw text
draw.text((50, 100), english_text, font=eng_font, fill=(0, 0, 0))
draw.text((50, 200), tamil_text, font=tam_font, fill=(0, 0, 0))

# Show preview
st.image(img, caption="Generated Thumbnail", use_column_width=True)

# Save option
if st.button("💾 Save Thumbnail"):
    output_path = os.path.join(os.path.dirname(__file__), "thumbnail.png")
    img.save(output_path)
    st.success(f"Thumbnail saved as {output_path}")
