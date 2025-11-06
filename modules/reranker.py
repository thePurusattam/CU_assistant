from sentence_transformers import CrossEncoder

_reranker = None
def get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker

def rerank(query, passages, top_k=3):
    model = get_reranker()
    pairs = [(query, p) for p in passages]
    scores = model.predict(pairs)
    ranked = sorted(zip(passages, scores), key=lambda x: x[1], reverse=True)
    return [p for p, _ in ranked[:top_k]]
