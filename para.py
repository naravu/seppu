import streamlit as st
import nltk
from nltk.corpus import wordnet
import edge_tts
import asyncio
import os

# Ensure WordNet is available
nltk.download("wordnet", quiet=True)

def simple_paraphrase(sentence):
    """
    Lightweight paraphraser using WordNet synonyms.
    """
    words = sentence.split()
    new_words = []
    for w in words:
        syns = wordnet.synsets(w)
        if syns:
            lemmas = syns[0].lemmas()
            if lemmas:
                new_words.append(lemmas[0].name().replace("_", " "))
            else:
                new_words.append(w)
        else:
            new_words.append(w)
    return " ".join(new_words)

async def generate_audio(text, voice="en-US-AriaNeural", filename="output.mp3"):
    """
    Generate audio using edge-tts and save to file.
    """
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)
    return filename

# --- Streamlit UI ---
st.title("📝 Simple Paraphraser WebApp with Audio")
st.write("Enter a paragraph below, get a synonym-based paraphrase, and download the audio.")

# Text input area
text_input = st.text_area("Input Paragraph", height=150)

# Button to trigger paraphrasing
if st.button("Paraphrase"):
    if text_input.strip():
        result = simple_paraphrase(text_input)
        st.subheader("Paraphrased Output")
        st.write(result)

        # Generate audio
        filename = "paraphrase_audio.mp3"
        asyncio.run(generate_audio(result, filename=filename))

        # Provide download option
        with open(filename, "rb") as f:
            st.download_button(
                label="Download Paraphrased Audio",
                data=f,
                file_name="paraphrase_audio.mp3",
                mime="audio/mpeg"
            )
    else:
        st.warning("Please enter some text to paraphrase.")
