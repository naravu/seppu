import os
import io
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

st.title("🎨 Thumbnail Generator (English + Tamil with Transliteration)")

# Inputs
english_text = st.text_input("Enter English text", "Hello World")

# Tamil input with transliteration option
use_transliteration = st.checkbox("Enable Tamil transliteration")
raw_tamil_input = st.text_input("Enter Tamil text (or transliteration)", "vanakkam ulagam")

if use_transliteration:
    try:
        tamil_text = transliterate(raw_tamil_input, sanscript.ITRANS, sanscript.TAMIL)
    except Exception:
        st.warning("Could not transliterate, using raw input.")
        tamil_text = raw_tamil_input
else:
    tamil_text = raw_tamil_input

# Background type as combo box
bg_option = st.selectbox("Background type", ["Solid Color", "Upload Image", "Template"])
bg_color = None
bg_image = None

if bg_option == "Solid Color":
    bg_color = st.color_picker("Pick background color", "#ffffff")
elif bg_option == "Upload Image":
    uploaded_file = st.file_uploader("Upload background image", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        bg_image = Image.open(uploaded_file).convert("RGB").resize((1280, 720))
elif bg_option == "Template":
    template_choice = st.selectbox("Choose a template", ["Gradient Blue", "Dark Theme", "Sunset"])
    if template_choice == "Gradient Blue":
        bg_image = Image.linear_gradient("L").resize((1280, 720)).convert("RGB")
    elif template_choice == "Dark Theme":
        bg_image = Image.new("RGB", (1280, 720), color="#111111")
    elif template_choice == "Sunset":
        bg_image = Image.radial_gradient("L").resize((1280, 720)).convert("RGB")

# Foreground text color
fg_color = st.color_picker("Pick text color", "#000000")

# Overlay controls
use_overlay = st.checkbox("Add text overlay boxes", value=True)
overlay_color = st.color_picker("Overlay color", "#000000")
overlay_opacity = st.slider("Overlay opacity (0-255)", 50, 255, 120)

# Font size sliders
eng_size = st.slider("English font size", 30, 120, 60)
tam_size = st.slider("Tamil font size", 30, 120, 60)

# Alignment dropdown
alignment = st.selectbox("Text alignment", ["Left", "Center", "Right"])

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

# Base image
if bg_image:
    img = bg_image.copy()
else:
    img = Image.new("RGB", (1280, 720), color=bg_color or "#ffffff")

draw = ImageDraw.Draw(img)

# Helper: get text width/height
def get_text_size(text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height

# Calculate positions
if alignment == "Center":
    w, h = img.size
    eng_w, eng_h = get_text_size(english_text, eng_font)
    tam_w, tam_h = get_text_size(tamil_text, tam_font)
    eng_pos = ((w - eng_w) // 2, 200)
    tam_pos = ((w - tam_w) // 2, 400)
elif alignment == "Right":
    w, h = img.size
    eng_w, eng_h = get_text_size(english_text, eng_font)
    tam_w, tam_h = get_text_size(tamil_text, tam_font)
    eng_pos = (w - eng_w - 50, 200)
    tam_pos = (w - tam_w - 50, 400)
else:  # Left
    eng_pos = (50, 200)
    tam_pos = (50, 400)

# Draw overlay boxes if enabled
def draw_overlay(pos, text, font):
    if use_overlay:
        w, h = get_text_size(text, font)
        x, y = pos
        box = Image.new("RGBA", (w + 20, h + 20), overlay_color + f"{overlay_opacity:02x}")
        img.paste(box, (x - 10, y - 10), box)

draw_overlay(eng_pos, english_text, eng_font)
draw_overlay(tam_pos, tamil_text, tam_font)

# Draw text
draw.text(eng_pos, english_text, font=eng_font, fill=fg_color)
draw.text(tam_pos, tamil_text, font=tam_font, fill=fg_color)

# Show preview
st.image(img, caption="Generated Thumbnail")

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
