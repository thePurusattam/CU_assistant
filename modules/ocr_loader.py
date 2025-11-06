import os
import pytesseract
from PIL import Image
import re
import os
from dotenv import load_dotenv

load_dotenv()
TESS_PATH = os.getenv("TESSERACT_PATH", "")

if TESS_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESS_PATH

def load_jpegs(folder_path="data/pdfs"):
    texts = {}
    for f in os.listdir(folder_path):
        if f.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(folder_path, f)
            try:
                text = pytesseract.image_to_string(Image.open(img_path))
                # Clean up whitespace
                text = re.sub(r"\s+", " ", text).strip()
                if text:
                    texts[f] = text
            except Exception as e:
                print(f"[OCR] Failed {f}: {e}")
    return texts
