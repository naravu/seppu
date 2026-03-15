import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import os

def generate_thumbnail(text, font_path, bg_type="solid", output_file="thumbnail.png"):
    width, height = 1280, 720  # YouTube thumbnail size

    # Step 1: Background
    if bg_type == "solid":
        background = Image.new("RGB", (width, height),
                               (random.randint(0,255), random.randint(0,255), random.randint(0,255)))
    elif bg_type == "gradient":
        background = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(background)
        for y in range(height):
            r = int(255 * (y / height))
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    else:
        background = Image.new("RGB", (width, height), (0, 0, 0))

    # Step 2: Add text
    draw = ImageDraw.Draw(background)
    try:
        font = ImageFont.truetype(font_path, 80)
    except:
        font = ImageFont.load_default()

    text_width, text_height = draw.textsize(text, font=font)
    position = ((width - text_width) // 2, (height - text_height) // 2)

    draw.text(position, text, font=font, fill=(255, 255, 255))

    # Step 3: Save
    background.save(output_file)
    return output_file

# --- Streamlit UI ---
st.title("🎨 YouTube Thumbnail Generator")
st.write("Generate thumbnails with dynamic backgrounds and regional fonts.")

# Input lyrics/text
text_input = st.text_area("Enter lyrics or text", "ನನ್ನ ಹಾಡಿನ ಸಾಹಿತ್ಯ")

# Upload font file
font_file = st.file_uploader("Upload a regional font (.ttf)", type=["ttf"])

# Background type
bg_type = st.selectbox("Background type", ["solid", "gradient", "black"])

# Generate button
if st.button("Generate Thumbnail"):
    if text_input.strip():
        if font_file is not None:
            font_path = os.path.join("uploaded_font.ttf")
            with open(font_path, "wb") as f:
                f.write(font_file.read())
        else:
            font_path = "NotoSansKannada-Regular.ttf"  # fallback font

        output_file = generate_thumbnail(text_input, font_path, bg_type)
        st.image(output_file, caption="Generated Thumbnail", use_column_width=True)

        # Download option
        with open(output_file, "rb") as f:
            st.download_button(
                label="Download Thumbnail",
                data=f,
                file_name="thumbnail.png",
                mime="image/png"
            )
    else:
        st.warning("Please enter some text.")
