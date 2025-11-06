import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """Extract clean text from a PDF file using PyMuPDF."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            page_text = page.get_text("text")
            page_text = " ".join(page_text.split())  # remove weird line breaks
            text += page_text + "\n"
    return text.strip()
