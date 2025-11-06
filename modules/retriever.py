# modules/retriever.py
import os, pickle, numpy as np, faiss
from sentence_transformers import SentenceTransformer

EMBED_DIR = "data/embeddings"

def retrieve_chunks(query, top_k=10):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    index = faiss.read_index(os.path.join(EMBED_DIR, "embeddings.index"))
    with open(os.path.join(EMBED_DIR, "embeddings.pkl"), "rb") as f:
        data = pickle.load(f)

    chunks = data["chunks"]
    meta = data["meta"]

    # Encode query
    q_emb = model.encode([query], convert_to_numpy=True).astype("float32")

    # Search FAISS
    D, I = index.search(q_emb, top_k)

    # Convert FAISS results to normal Python ints and floats
    results = []
    for dist, idx in zip(D[0], I[0]):
        if 0 <= idx < len(chunks):
            results.append({
                "chunk": chunks[int(idx)],
                "source": meta[int(idx)],
                "score": float(dist)
            })

    return results

