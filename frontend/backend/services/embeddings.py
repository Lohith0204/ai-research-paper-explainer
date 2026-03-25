import httpx
from backend.core.config import settings
from typing import List
import numpy as np

async def generate_embeddings(texts: List[str]) -> np.ndarray:
    """
    Generates embeddings using the Hugging Face Inference API for Vercel efficiency.
    Model: sentence-transformers/all-MiniLM-L6-v2
    """
    if not texts:
        return np.array([], dtype=np.float32)
        
    api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            api_url,
            headers=headers,
            json={"inputs": texts, "options": {"wait_for_model": True}}
        )
        
        if response.status_code != 200:
            print(f"Embedding API error: {response.text}")
            # Fallback to zeros instead of crashing the app
            return np.zeros((len(texts), 384), dtype=np.float32)
            
        embeddings = response.json()
        return np.array(embeddings, dtype=np.float32)
