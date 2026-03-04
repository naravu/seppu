# 🎙️ Seppuga AI

Seppuga AI is a **Streamlit application** that brings together multilingual **Text‑to‑Speech** and **Text‑to‑Image** generation in one simple interface.  
It leverages **Microsoft Edge TTS**, **Stable Diffusion**, and **Google Translator** to create audio and visuals from user input.

---

## ✨ Features

- 🔊 **Text‑to‑Speech**
  - Supports multiple Indian languages (Hindi, Tamil, Telugu, Kannada, Malayalam) and English.
  - Choice of **male/female neural voices**.
  - Input modes:
    - Translate from English
    - Transliterate (phonetic typing)
  - Instant playback and MP3 download.

- 🎨 **Text‑to‑Image**
  - Generate AI images using **Stable Diffusion v1.5**.
  - Works on both CPU and GPU (optimized for CUDA if available).
  - Download generated images as PNG.

- 🛠️ **Optimizations**
  - Cached translators and pipelines for faster performance.
  - Responsive UI with custom CSS styling.
  - Error handling and user‑friendly messages.

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/your-username/seppuga-ai.git
cd seppuga-ai

## Install dependencies
pip install -r requirements.txt

## Run the app
streamlit run app.py

## Project Structure
.
├── app.py                # Main Streamlit app
├── requirements.txt      # Python dependencies
├── pri/bm/bm.md          # Example bookmarks file (optional)
└── README.md             # Project documentation

⚙️ Requirements

    Python 3.9+

    Streamlit

    edge-tts

    torch

    diffusers

    deep-translator

    indic-transliteration

    Pillow

🚀 Deployment

    You can deploy this app easily on Streamlit Cloud:

    Push this repo to GitHub.

    Go to Streamlit Cloud.

    Connect your repo and deploy.

    Enjoy your AI app in the browser!


---

This README is **GitHub‑ready**: it explains what the project does, how to install and run it, and how to deploy.  

Would you like me to also prepare a **requirements.txt** file alongside this README so you can commit both together for a streamlined setup?
