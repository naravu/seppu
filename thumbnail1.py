import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw, ImageFont
import io

st.title("🖌️ WYSIWYG Thumbnail Maker")

# Canvas settings
bg_color = st.color_picker("Background color", "#ffffff")
stroke_color = st.color_picker("Stroke color", "#000000")
stroke_width = st.slider("Stroke width", 1, 10, 2)

# Create interactive canvas
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",  # Transparent fill
    stroke_color=stroke_color,
    background_color=bg_color,
    update_streamlit=True,
    height=720,
    width=1280,
    drawing_mode="freedraw",  # You can also allow "rect", "circle", "line", "transform"
    key="canvas",
)

# Text input
english_text = st.text_input("English text", "Hello World")
tamil_text = st.text_input("Tamil text", "வணக்கம் உலகம்")

# Font size
eng_size = st.slider("English font size", 30, 120, 60)
tam_size = st.slider("Tamil font size", 30, 120, 60)

# Render text on canvas preview
if canvas_result.image_data is not None:
    img = Image.fromarray(canvas_result.image_data.astype("uint8"))
    draw = ImageDraw.Draw(img)

    try:
        font_eng = ImageFont.truetype("Arial.ttf", eng_size)
    except OSError:
        font_eng = ImageFont.load_default()

    try:
        font_tam = ImageFont.truetype("NotoSansTamil-Regular.ttf", tam_size)
    except OSError:
        font_tam = ImageFont.load_default()

    draw.text((50, 200), english_text, font=font_eng, fill=stroke_color)
    draw.text((50, 400), tamil_text, font=font_tam, fill=stroke_color)

    st.image(img, caption="Thumbnail Preview")

    # Save to memory buffer for download
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="⬇️ Download Thumbnail",
        data=byte_im,
        file_name="thumbnail.png",
        mime="image/png"
    )
