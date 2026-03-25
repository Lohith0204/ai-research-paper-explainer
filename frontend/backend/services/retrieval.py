from typing import List, Dict
import numpy as np
from backend.services.embeddings import generate_embeddings
from backend.vectorstore.faiss_store import vector_store

async def retrieve_and_rerank(paper_id: str, query: str, top_k: int = 5, is_summary: bool = False) -> List[Dict]:
    """
    Retrieves chunks from FAISS and applies lightweight reranking.
    """
    embeddings = await generate_embeddings([query])
    if len(embeddings) == 0:
        return []
    query_embedding = embeddings[0]
    
    fetch_k = top_k * 2
    results = vector_store.search(paper_id, query_embedding, fetch_k)
    
    if not results:
        return []
        
    reranked = []
    for res in results:
        score = res["score"]
        
        if is_summary:
            if res["section"] in ["abstract", "conclusion"]:
                score += 0.15
                
        reranked.append({
            "score": score,
            "text": res["text"],
            "page": res["page"],
            "section": res["section"]
        })
        
    reranked.sort(key=lambda x: x["score"], reverse=True)
    
    return reranked[:top_k]
