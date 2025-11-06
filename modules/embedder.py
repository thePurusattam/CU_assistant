from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle

def generate_embeddings(chunks, save_path="data/embeddings/embeddings.index"):
    # Initialize model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Convert text chunks to numeric vectors
    embeddings = model.encode(chunks)

    # Build FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))

    # Save index and text chunks for later retrieval
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    faiss.write_index(index, save_path)
    with open(save_path.replace(".index", ".pkl"), "wb") as f:
        pickle.dump(chunks, f)

    print(f"✅ {len(chunks)} chunks embedded and stored successfully.")
