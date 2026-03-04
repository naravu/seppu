import streamlit as st
from diffusers import StableDiffusionPipeline
import torch

# Page setup
st.set_page_config(page_title="AI Image Generator", page_icon="🎨", layout="centered")
st.title("🎨 Free AI Image Generator")

# Prompt input
prompt = st.text_area("Enter your image description:", 
                      placeholder="A futuristic city with flying cars")

if st.button("Generate Image"):
    if prompt.strip():
        with st.spinner("Generating image..."):
            # Load model (cached for performance)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if device == "cuda" else torch.float32
            pipe = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=dtype
            ).to(device)

            # Generate image
            image = pipe(prompt).images[0]

            # Show result
            st.image(image, caption="Generated Image", use_container_width=True)

            # Download option
            image.save("generated.png")
            with open("generated.png", "rb") as f:
                st.download_button("📥 Download Image", f, "generated.png", "image/png")
    else:
        st.warning("Please enter a description!")
