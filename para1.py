import streamlit as st
import nltk
from nltk.corpus import wordnet
import edge_tts
import asyncio
from pydub import AudioSegment

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

async def generate_audio(text, voice="en-US-AriaNeural", filename="speech.mp3"):
    """
    Generate audio using edge-tts and save to file.
    """
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)
    return filename

def add_background_music(speech_file, music_file="background.mp3", output_file="final_output.mp3"):
    """
    Overlay background music with speech using pydub.
    """
    speech = AudioSegment.from_file(speech_file, format="mp3")
    music = AudioSegment.from_file(music_file, format="mp3")

    # Lower music volume so it doesn't overpower speech
    music = music - 15  

    # Loop music if shorter than speech
    if len(music) < len(speech):
        times = int(len(speech) / len(music)) + 1
        music = music * times

    # Trim to match speech length
    music = music[:len(speech)]

    # Overlay speech on music
    combined = music.overlay(speech)

    combined.export(output_file, format="mp3")
    return output_file

# --- Streamlit UI ---
st.title("📝 Paraphraser WebApp with Audio + Background Music")
st.write("Enter a paragraph, get a synonym-based paraphrase, listen with background music, and download it.")

text_input = st.text_area("Input Paragraph", height=150)

if st.button("Paraphrase"):
    if text_input.strip():
        result = simple_paraphrase(text_input)
        st.subheader("Paraphrased Output")
        st.write(result)

        # Generate speech audio
        speech_file = "speech.mp3"
        asyncio.run(generate_audio(result, filename=speech_file))

        # Add background music (ensure you have a background.mp3 file in the project folder)
        final_file = add_background_music(speech_file, music_file="background.mp3")

        # Play audio in browser
        with open(final_file, "rb") as f:
            audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")

            # Download option
            st.download_button(
                label="Download Paraphrased Audio with Music",
                data=audio_bytes,
                file_name="paraphrase_with_music.mp3",
                mime="audio/mpeg"
            )
    else:
        st.warning("Please enter some text to paraphrase.")
