# scripts/index_all.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import os, pickle
import faiss
from sentence_transformers import SentenceTransformer
from modules.pdf_loader import extract_text_from_pdf

# Paths
PDF_DIR = "data/pdfs"
EMBED_DIR = "data/embeddings"
os.makedirs(EMBED_DIR, exist_ok=True)

print("\n🚀 Rebuilding CU Assistant Knowledge Index...\n")

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

texts, sources = [], []

# Step 1 – Extract text from all PDFs
for file in sorted(os.listdir(PDF_DIR)):
    if not file.lower().endswith(".pdf"):
        continue
    pdf_path = os.path.join(PDF_DIR, file)
    print(f"📄 Reading: {file}")

    try:
        text = extract_text_from_pdf(pdf_path)
        if not text.strip():
            print(f"⚠️ Skipping empty or unreadable file: {file}")
            continue
        # Clean text
        clean_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
        texts.append(clean_text)
        sources.append(file)
    except Exception as e:
        print(f"❌ Error reading {file}: {e}")

print(f"\n✅ Loaded {len(texts)} valid PDFs.\n")

# Step 2 – Chunk text for embeddings
def chunk_text(text, chunk_size=700):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

chunks, metadata = [], []
for i, doc in enumerate(texts):
    for chunk in chunk_text(doc):
        chunks.append(chunk)
        metadata.append(sources[i])

print(f"🔹 Total chunks to embed: {len(chunks)}")

# Step 3 – Create embeddings
embeddings = model.encode(chunks, convert_to_numpy=True)
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Step 4 – Save index
faiss.write_index(index, os.path.join(EMBED_DIR, "embeddings.index"))
with open(os.path.join(EMBED_DIR, "embeddings.pkl"), "wb") as f:
    pickle.dump({"chunks": chunks, "meta": metadata}, f)

print("\n✅ Embeddings index successfully rebuilt and saved!")
print("📦 Total documents indexed:", len(sources))

