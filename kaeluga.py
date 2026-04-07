import streamlit as st
import pyttsx3
import PyPDF2
import tempfile
import os

st.title("📖 PDF to Speech WebApp")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# Page range selection
start_page = st.number_input("Start page", min_value=0, value=0)
end_page = st.number_input("End page (leave 0 for all)", min_value=0, value=0)

if uploaded_file is not None:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # Read PDF
    book = open(tmp_path, "rb")
    pdfReader = PyPDF2.PdfFileReader(book)
    pages = pdfReader.numPages

    if end_page == 0 or end_page > pages:
        end_page = pages

    st.write(f"Total pages: {pages}")
    st.write(f"Reading from page {start_page} to {end_page}")

    # Initialize TTS engine
    speaker = pyttsx3.init()

    # Extract and speak text
    for num in range(start_page, end_page):
        page = pdfReader.getPage(num)
        text = page.extractText()
        if text.strip():
            st.text_area(f"Page {num}", text, height=200)
            speaker.say(text)
    speaker.runAndWait()

    book.close()
    os.remove(tmp_path)
