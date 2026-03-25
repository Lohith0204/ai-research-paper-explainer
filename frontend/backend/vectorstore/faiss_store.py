import faiss
import numpy as np
import os
import uuid
import datetime
from typing import List, Dict

class VectorStoreManager:
    """
    Manages In-Memory FAISS indices for session-based Vercel hosting.
    No disk persistence to ensure stateless efficiency.
    """
    def __init__(self):
        self.dimension = 384
        self._active_indices = {} # paper_id -> (faiss_index, chunks_data)
        self._registry = {} # paper_id -> metadata
        
    def add_paper(self, paper_id: str, filename: str, embeddings: np.ndarray, chunks_data: List[Dict]):
        if len(embeddings) == 0:
            return
            
        index = faiss.IndexFlatIP(self.dimension)
        embeddings = np.array(embeddings, dtype=np.float32)
        index.add(embeddings)
        
        self._active_indices[paper_id] = (index, chunks_data)
        
        sections = list(set(c.get("section", "general") for c in chunks_data))
        self._registry[paper_id] = {
            "filename": filename,
            "chunks": len(chunks_data),
            "created_at": datetime.datetime.utcnow().isoformat(),
            "sections": sections
        }

    def get_paper_chunks(self, paper_id: str) -> List[Dict]:
        if paper_id in self._active_indices:
            return self._active_indices[paper_id][1]
        return []

    def search(self, paper_id: str, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
        if paper_id not in self._active_indices:
            return []
            
        index, chunks = self._active_indices[paper_id]
        query_embedding = np.array([query_embedding], dtype=np.float32)
        
        search_k = min(top_k, index.ntotal)
        if search_k == 0: return []
        
        distances, indices = index.search(query_embedding, search_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1: continue
            
            chunk_data = chunks[idx]
            results.append({
                "score": float(dist),
                "text": chunk_data["text"],
                "page": chunk_data.get("page", 1),
                "section": chunk_data.get("section", "general")
            })
            
        return results

    def list_papers(self) -> List[Dict]:
        return [{"paper_id": pid, **data} for pid, data in self._registry.items()]

vector_store = VectorStoreManager()
