from typing import List, Dict
import json
from backend.services.llm import generate_response

def extract_knowledge_graph(context_chunks: List[str]) -> Dict:
    """
    Extracts nodes and edges for building a Knowledge Graph representation.
    """
    context = "\n\n".join(context_chunks)
    
    prompt = f"""
You are an expert AI data extractor. Read the following context and extract a knowledge graph.

Context:
{context}

Generate a structured JSON response with exactly these keys:
- "nodes": A list of objects with "id" (the entity name) and "label" (Entity Type).
- "edges": A list of objects with "source" (node id), "target" (node id), and "relation" (how they are connected, e.g., "uses", "improves").

Response MUST be valid JSON.
"""
    response_text = generate_response(prompt, json_format=True)
    
    try:
        data = json.loads(response_text)
        if "nodes" not in data or "edges" not in data:
            raise ValueError("Missing keys")
        return data
    except Exception as e:
        print(f"Graph JSON parsing failed: {e}. Raw: {response_text}")
        return {
            "nodes": [],
            "edges": []
        }
