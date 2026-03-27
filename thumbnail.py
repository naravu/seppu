import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# Inputs
st.title("Thumbnail Generator")
english_text = st.text_input("Enter English text")
tamil_text = st.text_input("Enter Tamil text")

# Font selection
eng_font = ImageFont.truetype("fonts/Arial.ttf", 60)
tam_font = ImageFont.truetype("fonts/NotoSansTamil-Regular.ttf", 60)

# Base image
img = Image.new("RGB", (800, 400), color=(255, 255, 255))
draw = ImageDraw.Draw(img)

# Draw text
draw.text((50, 100), english_text, font=eng_font, fill=(0, 0, 0))
draw.text((50, 200), tamil_text, font=tam_font, fill=(0, 0, 0))

# Show in Streamlit
st.image(img)

# Export option
if st.button("Save Thumbnail"):
    img.save("thumbnail.png")
    st.success("Thumbnail saved as thumbnail.png")
