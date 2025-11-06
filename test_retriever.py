# test_retriever.py
from modules.retriever import retrieve_chunks

query = "What is the time table for Monday for 25MAM-3"
results = retrieve_chunks(query, top_k=5)

print("\n🔍 Retrieved chunks:")
for r in results:
    print("-", r.get("chunk", "")[:300], "\n---")
