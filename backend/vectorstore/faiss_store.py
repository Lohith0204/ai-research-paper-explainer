import faiss
import numpy as np
import json
import os
import uuid
import datetime
from typing import List, Dict

class VectorStoreManager:
    """
    Manages isolated FAISS indices per paper and an active registry in data/papers.json.
    """
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.indices_dir = os.path.join(data_dir, "indices")
        self.registry_path = os.path.join(data_dir, "papers.json")
        self.dimension = 384
        
        os.makedirs(self.indices_dir, exist_ok=True)
        self._registry = self._load_registry()
        
    def _load_registry(self) -> Dict:
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
        
    def _save_registry(self):
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self._registry, f, indent=2)
            
    def _get_index_paths(self, paper_id: str):
        return (
            os.path.join(self.indices_dir, f"{paper_id}.index"),
            os.path.join(self.indices_dir, f"{paper_id}.meta.json")
        )

    def add_paper(self, paper_id: str, filename: str, embeddings: np.ndarray, chunks_data: List[Dict]):
        if len(embeddings) == 0:
            return
            
        index_path, meta_path = self._get_index_paths(paper_id)
        
        index = faiss.IndexFlatIP(self.dimension)
        embeddings = np.array(embeddings, dtype=np.float32)
        index.add(embeddings)
        
        faiss.write_index(index, index_path)
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, ensure_ascii=False)
            
        sections = list(set(c.get("section", "general") for c in chunks_data))
            
        self._registry[paper_id] = {
            "filename": filename,
            "chunks": len(chunks_data),
            "created_at": datetime.datetime.utcnow().isoformat(),
            "sections": sections
        }
        self._save_registry()

    def get_paper_chunks(self, paper_id: str) -> List[Dict]:
        """Returns all metadata chunks raw for summaries or graph extractions"""
        _, meta_path = self._get_index_paths(paper_id)
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def search(self, paper_id: str, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
        """Searches specifically inside one paper's isolated vector store."""
        if paper_id not in self._registry:
            return []
            
        index_path, meta_path = self._get_index_paths(paper_id)
        if not os.path.exists(index_path):
            return []
            
        index = faiss.read_index(index_path)
        chunks = self.get_paper_chunks(paper_id)
        
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
        papers = []
        for pid, data in self._registry.items():
            papers.append({
                "paper_id": pid,
                **data
            })
        return papers

vector_store = VectorStoreManager()
