import os
import io
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.title("🎨 Thumbnail Generator (English + Tamil)")

# Inputs
english_text = st.text_input("Enter English text", "Hello World")
tamil_text = st.text_input("Enter Tamil text", "வணக்கம் உலகம்")

# Font paths
eng_font_path = os.path.join(os.path.dirname(__file__), "fonts", "Arial.ttf")
tam_font_path = os.path.join(os.path.dirname(__file__), "fonts", "NotoSansTamil-Regular.ttf")

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

# Save to memory buffer for download
buf = io.BytesIO()
img.save(buf, format="PNG")
byte_im = buf.getvalue()

# Download button
st.download_button(
    label="⬇️ Download Thumbnail",
    data=byte_im,
    file_name="thumbnail.png",
    mime="image/png"
)
