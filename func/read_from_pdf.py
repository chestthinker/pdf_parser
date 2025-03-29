import os
import json
from PyPDF2 import PdfReader


def read_from_pdf(pdf_path, output_json):

    with open(pdf_path, 'rb') as pdf_file:

        pdf_reader = PdfReader(pdf_file)
        if pdf_reader.is_encrypted: # Check for encrypted PDF
            print(f"Encrypted PDF detected: {pdf_path}")
            return None

        # Extract text from all pages
        text_pages = [ page.extract_text() for page in pdf_reader.pages ]

        # Persist extracted text with Unicode preservation
        with open(output_json, "w", encoding='utf-8') as f:
            json.dump(text_pages, f, ensure_ascii=False, indent=4)

        print(f" Complete: {os.path.basename(pdf_path)} -> {os.path.basename(output_json)} - Pages: {len(pdf_reader.pages)}") 

    return text_pages

