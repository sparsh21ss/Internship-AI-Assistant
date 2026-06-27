import os
import numpy as np
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"[ERROR] Failed to read PDF file at {pdf_path}: {e}")
        return ""

def read_resume(file_path):
    """
    Reads a resume from a file path. Supports PDF, TXT, and MD files.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found at: {file_path}")
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".txt", ".md"]:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Please use .pdf, .txt, or .md.")

def cosine_similarity(v1, v2):
    """
    Calculates the cosine similarity between two vectors.
    Returns a float between 0.0 and 1.0 (clamped if negative).
    """
    v1 = np.array(v1)
    v2 = np.array(v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0.0 or norm_v2 == 0.0:
        return 0.0
    similarity = np.dot(v1, v2) / (norm_v1 * norm_v2)
    return float(max(0.0, similarity))
