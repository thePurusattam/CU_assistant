# modules/generator_gemini.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_KEY")
if not api_key:
    raise RuntimeError("⚠️ GEMINI_KEY not found in your .env file!")

# Configure Gemini
genai.configure(api_key=api_key)

# ✅ Choose the correct working model
MODEL_NAME = "models/gemini-2.5-flash"

def generate_answer(retrieved_chunks, query: str) -> str:
    """
    Generates an academic-style answer using Gemini 2.5 Flash.
    Integrates RAG context from retrieved chunks.
    """
    # Combine retrieved text into context
    context = "\n\n".join(
        [
            r.get("chunk") if isinstance(r, dict) else str(r)
            for r in retrieved_chunks
        ]
    )

    prompt = (
        "You are CU_Assistant, an academic AI tutor designed for students of Chandigarh University.\n"
        "Use ONLY the context provided below to answer the question.\n"
        "If the information is missing, clearly say 'The answer is not available in the given material.'\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n\n"
        "Answer:"
    )

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error generating answer: {e}"
