import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw, ImageFont
import io

st.title("🖌️ WYSIWYG Thumbnail Maker (4K Edition)")

# Fixed resolution: 4K UHD
width, height = 3840, 2160

# Canvas settings
bg_color = st.color_picker("Background color", "#ffffff")

# Brush controls
stroke_color = st.color_picker("Brush/Text color", "#000000")
stroke_width = st.slider("Brush size", 1, 50, 5)
drawing_mode = st.selectbox(
    "Drawing mode",
    ["freedraw", "line", "rect", "circle", "transform"]
)

# Create interactive canvas
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",  # Transparent fill
    stroke_color=stroke_color,
    background_color=bg_color,
    update_streamlit=True,
    height=height,
    width=width,
    drawing_mode=drawing_mode,
    stroke_width=stroke_width,
    key="canvas",
)

# Text inputs
english_text = st.text_input("English text", "Hello World")
tamil_text = st.text_input("Tamil text", "வணக்கம் உலகம்")

# Font sizes
eng_size = st.slider("English font size", 60, 240, 120)
tam_size = st.slider("Tamil font size", 60, 240, 120)

# Render text on canvas preview
if canvas_result.image_data is not None:
    img = Image.fromarray(canvas_result.image_data.astype("uint8"))
    draw = ImageDraw.Draw(img)

    # Safe font loading
    try:
        font_eng = ImageFont.truetype("Arial.ttf", eng_size)
    except OSError:
        font_eng = ImageFont.load_default()

    try:
        font_tam = ImageFont.truetype("NotoSansTamil-Regular.ttf", tam_size)
    except OSError:
        font_tam = ImageFont.load_default()

    # Draw text (positions fixed, but canvas allows free drawing too)
    draw.text((100, height//3), english_text, font=font_eng, fill=stroke_color)
    draw.text((100, 2*height//3), tamil_text, font=font_tam, fill=stroke_color)

    st.image(img, caption="Thumbnail Preview (4K UHD)")

    # Save to memory buffer for download
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="⬇️ Download 4K Thumbnail",
        data=byte_im,
        file_name="thumbnail_4k.png",
        mime="image/png"
    )
