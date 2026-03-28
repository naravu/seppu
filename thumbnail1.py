import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw, ImageFont
import io, random

st.title("🎨 Paint‑Style WYSIWYG Thumbnail Maker (4K Edition)")

# Fixed resolution: 4K UHD
width, height = 3840, 2160

# Canvas background
bg_color = st.color_picker("Background color", "#ffffff")

# Brush controls
stroke_color = st.color_picker("Brush/Text color", "#000000")
stroke_width = st.slider("Brush size", 1, 50, 5)
stroke_opacity = st.slider("Brush opacity", 0, 255, 255)

tool = st.selectbox(
    "Tool",
    ["freedraw", "line", "rect", "circle", "eraser", "spray", "highlighter"]
)

# Zoom & pan controls
zoom_factor = st.slider("Zoom (%)", 25, 200, 100)
pan_x = st.slider("Pan X offset", -500, 500, 0)
pan_y = st.slider("Pan Y offset", -500, 500, 0)

# Effective color with opacity
rgba_color = stroke_color + f"{stroke_opacity:02x}"

# Map eraser to freedraw with background color
effective_color = bg_color if tool == "eraser" else rgba_color
drawing_mode = "freedraw" if tool in ["eraser", "spray", "highlighter"] else tool

# Create interactive canvas
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_color=effective_color,
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

# Render text + special tools
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

    # Draw text
    draw.text((100, height//3), english_text, font=font_eng, fill=stroke_color)
    draw.text((100, 2*height//3), tamil_text, font=font_tam, fill=stroke_color)

    # Special tools simulation
    if tool == "spray":
        for _ in range(200):
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.ellipse((x, y, x+2, y+2), fill=stroke_color)
    elif tool == "highlighter":
        draw.rectangle([100, 500, 1000, 600], fill=stroke_color + "80")  # semi-transparent

    # Apply zoom & pan for preview
    preview = img.copy()
    zoomed_w = int(width * zoom_factor / 100)
    zoomed_h = int(height * zoom_factor / 100)
    preview = preview.crop((
        max(0, pan_x),
        max(0, pan_y),
        min(width, pan_x + zoomed_w),
        min(height, pan_y + zoomed_h)
    ))
    preview = preview.resize((1280, 720))  # preview window

    st.image(preview, caption=f"Thumbnail Preview (Zoom {zoom_factor}%)")

    # Save full 4K image for download
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="⬇️ Download Full 4K Thumbnail",
        data=byte_im,
        file_name="thumbnail_4k.png",
        mime="image/png"
    )
