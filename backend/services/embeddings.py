import numpy as np
from sentence_transformers import SentenceTransformer
import warnings
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore")

_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading SentenceTransformer model all-MiniLM-L6-v2...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def generate_embeddings(texts: list) -> np.ndarray:
    """
    Generates L2-normalized embeddings for a list of texts using sentence-transformers.
    """
    if not texts:
        return np.array([])
        
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True)
    
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normalized_embeddings = embeddings / norms
    
    return normalized_embeddings
