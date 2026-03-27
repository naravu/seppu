import os
import io
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.title("🎨 Thumbnail Generator (English + Tamil)")

# Inputs
english_text = st.text_input("Enter English text", "Hello World")
tamil_text = st.text_input("Enter Tamil text", "வணக்கம் உலகம்")

# Modern color controls
bg_color = st.color_picker("Pick background color", "#ffffff")
fg_color = st.color_picker("Pick text color", "#000000")

# Font size sliders
eng_size = st.slider("English font size", 30, 120, 60)
tam_size = st.slider("Tamil font size", 30, 120, 60)

# Alignment options
alignment = st.radio("Text alignment", ["Left", "Center", "Right"])

# Font paths
eng_font_path = os.path.join(os.path.dirname(__file__), "fonts", "Arial.ttf")
tam_font_path = os.path.join(os.path.dirname(__file__), "fonts", "NotoSansTamil-Regular.ttf")

# Load fonts safely
try:
    eng_font = ImageFont.truetype(eng_font_path, eng_size)
except OSError:
    st.warning("Could not load English font, using default.")
    eng_font = ImageFont.load_default()

try:
    tam_font = ImageFont.truetype(tam_font_path, tam_size)
except OSError:
    st.warning("Could not load Tamil font, using default.")
    tam_font = ImageFont.load_default()

# Base image with chosen background color (YouTube recommended size)
img = Image.new("RGB", (1280, 720), color=bg_color)
draw = ImageDraw.Draw(img)

# Calculate positions based on alignment
if alignment == "Center":
    w, h = img.size
    eng_w, _ = draw.textsize(english_text, font=eng_font)
    tam_w, _ = draw.textsize(tamil_text, font=tam_font)
    eng_pos = ((w - eng_w) // 2, 200)
    tam_pos = ((w - tam_w) // 2, 400)
elif alignment == "Right":
    w, _ = img.size
    eng_w, _ = draw.textsize(english_text, font=eng_font)
    tam_w, _ = draw.textsize(tamil_text, font=tam_font)
    eng_pos = (w - eng_w - 50, 200)
    tam_pos = (w - tam_w - 50, 400)
else:  # Left
    eng_pos = (50, 200)
    tam_pos = (50, 400)

# Draw text
draw.text(eng_pos, english_text, font=eng_font, fill=fg_color)
draw.text(tam_pos, tamil_text, font=tam_font, fill=fg_color)

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
