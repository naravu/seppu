import os
import io
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

st.title("🎨 Thumbnail Generator (English + Tamil, 4K + Effects)")

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

# Background type
bg_option = st.selectbox("Background type", ["Solid Color", "Upload Image", "Template Gallery"])
bg_color, bg_image = None, None

if bg_option == "Solid Color":
    bg_color = st.color_picker("Pick background color", "#ffffff")
elif bg_option == "Upload Image":
    uploaded_file = st.file_uploader("Upload background image", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        bg_image = Image.open(uploaded_file).convert("RGB").resize((3840, 2160))
elif bg_option == "Template Gallery":
    template_choice = st.selectbox("Choose a template", ["Gradient Blue", "Dark Theme", "Sunset", "Cinematic", "Minimal White"])
    if template_choice == "Gradient Blue":
        bg_image = Image.linear_gradient("L").resize((3840, 2160)).convert("RGB")
    elif template_choice == "Dark Theme":
        bg_image = Image.new("RGB", (3840, 2160), color="#111111")
    elif template_choice == "Sunset":
        bg_image = Image.radial_gradient("L").resize((3840, 2160)).convert("RGB")
    elif template_choice == "Cinematic":
        bg_image = Image.new("RGB", (3840, 2160), color="#222222").filter(ImageFilter.GaussianBlur(20))
    elif template_choice == "Minimal White":
        bg_image = Image.new("RGB", (3840, 2160), color="#fdfdfd")

# Foreground text color
fg_color = st.color_picker("Pick text color", "#000000")

# Overlay controls
use_overlay = st.checkbox("Add text overlay boxes", value=True)
overlay_color = st.color_picker("Overlay color", "#000000")
overlay_opacity = st.slider("Overlay opacity (0-255)", 50, 255, 120)

# Font size sliders
eng_size = st.slider("English font size", 60, 240, 120)
tam_size = st.slider("Tamil font size", 60, 240, 120)

# Alignment dropdown
alignment = st.selectbox("Text alignment", ["Left", "Center", "Right"])

# Text effects
effect_choice = st.selectbox("Text effect", ["None", "Shadow", "Outline", "Glow"])
effect_color = st.color_picker("Effect color", "#ffffff")

# Font paths
eng_font_path = os.path.join(os.path.dirname(__file__), "fonts", "Arial.ttf")
tam_font_path = os.path.join(os.path.dirname(__file__), "fonts", "NotoSansTamil-Regular.ttf")

# Load fonts safely
def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        st.warning(f"Could not load font {path}, using default.")
        return ImageFont.load_default()

eng_font = load_font(eng_font_path, eng_size)
tam_font = load_font(tam_font_path, tam_size)

# Base image
img = bg_image.copy() if bg_image else Image.new("RGB", (3840, 2160), color=bg_color or "#ffffff")
draw = ImageDraw.Draw(img)

# Helper: get text width/height
def get_text_size(text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

# Positioning
def get_positions():
    w, h = img.size
    eng_w, eng_h = get_text_size(english_text, eng_font)
    tam_w, tam_h = get_text_size(tamil_text, tam_font)
    if alignment == "Center":
        return ((w - eng_w) // 2, 600), ((w - tam_w) // 2, 1200)
    elif alignment == "Right":
        return (w - eng_w - 100, 600), (w - tam_w - 100, 1200)
    else:
        return (100, 600), (100, 1200)

eng_pos, tam_pos = get_positions()

# Overlay boxes
def draw_overlay(pos, text, font):
    if use_overlay:
        w, h = get_text_size(text, font)
        x, y = pos
        box = Image.new("RGBA", (w + 40, h + 40), overlay_color + f"{overlay_opacity:02x}")
        img.paste(box, (x - 20, y - 20), box)

draw_overlay(eng_pos, english_text, eng_font)
draw_overlay(tam_pos, tamil_text, tam_font)

# Text effects
def draw_text_with_effect(pos, text, font, fill):
    x, y = pos
    if effect_choice == "Shadow":
        draw.text((x+4, y+4), text, font=font, fill=effect_color)
    elif effect_choice == "Outline":
        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                if dx != 0 or dy != 0:
                    draw.text((x+dx, y+dy), text, font=font, fill=effect_color)
    elif effect_choice == "Glow":
        for radius in range(8, 20, 4):
            draw.text((x, y), text, font=font, fill=effect_color)
    draw.text(pos, text, font=font, fill=fill)

# Draw text with effects
draw_text_with_effect(eng_pos, english_text, eng_font, fg_color)
draw_text_with_effect(tam_pos, tamil_text, tam_font, fg_color)

# Show preview
st.image(img, caption="Generated 4K Thumbnail with Text Effects")

# Save to memory buffer for download
buf = io.BytesIO()
img.save(buf, format="PNG")
byte_im = buf.getvalue()

# Download button
st.download_button(
    label="⬇️ Download 4K Thumbnail",
    data=byte_im,
    file_name="thumbnail_4k.png",
    mime="image/png"
)
