import streamlit as st
import nltk
from nltk.corpus import wordnet

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
                # Replace underscores with spaces for readability
                new_words.append(lemmas[0].name().replace("_", " "))
            else:
                new_words.append(w)
        else:
            new_words.append(w)
    return " ".join(new_words)

# --- Streamlit UI ---
st.title("📝 Simple Paraphraser WebApp")
st.write("Enter a paragraph below and get a synonym-based paraphrase.")

# Text input area
text_input = st.text_area("Input Paragraph", height=150)

# Button to trigger paraphrasing
if st.button("Paraphrase"):
    if text_input.strip():
        result = simple_paraphrase(text_input)
        st.subheader("Paraphrased Output")
        st.write(result)
    else:
        st.warning("Please enter some text to paraphrase.")
