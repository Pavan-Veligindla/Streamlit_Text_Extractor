import os
import tempfile
import re

import streamlit as st
import pytesseract
from pdf2image import convert_from_path

# Set Tesseract path if required (adjust this path for your OS)
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\1554\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def extract_text_tesseract(pdf_path):
    """Extracts text from a PDF using Tesseract OCR."""
    text = ""
    images = convert_from_path(pdf_path)
    for i, image in enumerate(images):
        text += pytesseract.image_to_string(image) + "\n"
    return text

def extract_relevant_data(text, fields_to_extract):
    """Dynamically extracts specified fields from the text."""
    extracted_data = {}
    fields = [field.strip() for field in fields_to_extract.split(',')]

    for field in fields:
        pattern = re.compile(
            rf"{re.escape(field)}\s*[:\-]?\s*"  # Match label with optional colon or dash
            rf"((?:.|\n)*?)"
            rf"(?=\n\s*\w+\s*[:\-]|\n{{2,}}|\Z)",  # Until another label, 2+ newlines, or end
            re.IGNORECASE | re.DOTALL
        )
        match = pattern.search(text)
        if match:
            raw_value = match.group(1)
            extracted_data[field] = " ".join(raw_value.split()).strip()
        else:
            extracted_data[field] = None

    return extracted_data

# ---------------- Streamlit UI ---------------- #

st.set_page_config(page_title="PDF Field Extractor", layout="centered")

st.title("📄 PDF OCR Field Extractor")

pdf_file = st.file_uploader("Upload a PDF document", type="pdf")

fields = st.text_input("Enter fields to extract (comma-separated)", placeholder="e.g., Name of Work, Estimate Amount")

if st.button("Extract Information") and pdf_file and fields:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_file.read())
        temp_path = tmp_file.name

    try:
        st.info("Extracting text from PDF using Tesseract...")
        extracted_text = extract_text_tesseract(temp_path)
        
        st.success("Text extracted. Extracting fields...")
        extracted_data = extract_relevant_data(extracted_text, fields)

        st.subheader("📋 Extracted Fields")
        for key, value in extracted_data.items():
            st.markdown(f"**{key}**: {value if value else 'Not Found'}")

    except Exception as e:
        st.error(f"An error occurred: {e}")

    finally:
        os.remove(temp_path)
