import httpx
import json
import re
import sys
from typing import Dict, List, Any
from backend.core.config import settings

_llm_cache = {}

def get_huggingface_url(model: str) -> str:
    # Using the global HF Inference Router v1 endpoint
    return "https://router.huggingface.co/v1/chat/completions"

def generate_response(prompt: str, json_format: bool = False, model: str = "Qwen/Qwen2.5-7B-Instruct") -> str:
    """
    Sends a prompt to the HuggingFace Inference API and returns the generated text.
    Handles fallbacks and caching.
    """
    cache_key = f"{model}_{json_format}_{prompt}"
    if cache_key in _llm_cache:
        return _llm_cache[cache_key]

    url = get_huggingface_url(model)
    headers = {}
    if settings.HUGGINGFACE_API_KEY:
        headers["Authorization"] = f"Bearer {settings.HUGGINGFACE_API_KEY}"
        
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 512,
        "temperature": 0.3
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            result = ""
            if "choices" in data and len(data["choices"]) > 0:
                raw_content = data["choices"][0]["message"]["content"].strip()
                result = raw_content
                # Handle JSON markdown if requested
                if json_format:
                    print(f"DEBUG: Raw response before JSON strip: {raw_content[:200]}...")
                    sys.stdout.flush()
                    # Look for content between ```json and ```
                    json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', result, re.DOTALL)
                    if json_match:
                        result = json_match.group(1).strip()
                    print(f"DEBUG: Response after JSON strip: {result[:200]}...")
                    sys.stdout.flush()
            elif isinstance(data, list) and len(data) > 0:
                # Basic fallback for pipeline format if needed
                if "generated_text" in data[0]:
                    result = data[0]["generated_text"].strip()
                elif "summary_text" in data[0]:
                    result = data[0]["summary_text"].strip()
                else:
                    result = str(data[0])
            elif "error" in data:
                return f"Error: {data['error']}"
            else:
                result = str(data)
                
            _llm_cache[cache_key] = result
            return result
    except httpx.TimeoutException:
        print("Timeout in HuggingFace API")
        raise ValueError("Could not generate response from LLM (Timeout).")
    except httpx.HTTPStatusError as e:
        error_detail = f"HF API Error {e.response.status_code}: {e.response.text}"
        print(f"DEBUG: {error_detail}")
        if e.response.status_code == 401:
            raise ValueError("Invalid Hugging Face API Key. Please check your .env file.")
        raise ValueError(f"Could not generate response from LLM: {error_detail}")
    except Exception as e:
        print(f"Error communicating with HuggingFace API: {e}")
        raise ValueError(f"Could not generate response from LLM: {str(e)}")

def summarize_paper_multi_step(paper_chunks: List[Dict]) -> Dict:
    abstract_chunks = [c["text"] for c in paper_chunks if c.get("section") == "abstract"]
    method_chunks = [c["text"] for c in paper_chunks if c.get("section") == "methodology"]
    results_chunks = [c["text"] for c in paper_chunks if c.get("section") == "results"]
    
    if not abstract_chunks: abstract_chunks = [c["text"] for c in paper_chunks[:3]]
    if not method_chunks: method_chunks = [c["text"] for c in paper_chunks[3:8]]
    if not results_chunks: results_chunks = [c["text"] for c in paper_chunks[-5:]]
    
    text_to_summarize = " ".join(abstract_chunks[:4])
    text_to_summarize = text_to_summarize[:3000]
    prompt_tl = f"Summarize the following research paper abstract in 2-3 concise sentences:\n\n{text_to_summarize}"
    tldr = generate_response(prompt_tl)
    
    if "Error:" in tldr: tldr = "Summary could not be generated at this time."

    prompt_cont = f"Extract exactly 3 key contributions or main take-aways from this research paper abstract. Return a plain string with one contribution per line, no numbering:\n\n{text_to_summarize}"
    cont_text = generate_response(prompt_cont)
    key_contributions = [c.strip("- *•").strip() for c in cont_text.strip().split("\n") if c.strip()][:3]
    if not key_contributions: key_contributions = []

    prompt_meth = f"""Explain the methodology clearly in 2-3 sentences. Return a plain string ONLY. Do not use JSON.\n\nContext:\n{" ".join(method_chunks[:3])[:2000]}"""
    methodology = generate_response(prompt_meth).strip()

    prompt_res = f"""Summarize the key results or findings in 2-3 sentences based PRECISELY on this Context. Return a plain string ONLY. Do not use JSON.\n\nContext:\n{" ".join(results_chunks[:3])[:2000]}"""
    results_text = generate_response(prompt_res).strip()

    summary = {
        "tldr": tldr,
        "key_contributions": key_contributions,
        "methodology": methodology if "Error:" not in methodology else "Methodology details not available.",
        "results": results_text if "Error:" not in results_text else "Results not available."
    }

    return summary

def answer_question(context_chunks: List[str], question: str) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    context = context[:3000]
    prompt = f"""You are a helpful AI research assistant.
Read the context below and answer the user's question based ONLY on the provided context. If the answer is not in context, you must return exactly "Not found in the paper".

Context:
{context}

Question:
{question}

Answer:"""
    
    res = generate_response(prompt).strip()
    if not res or "Error:" in res:
        return "Not found in the paper"
        
    return res

def explain_simple(abstract_chunks: List[str]) -> str:
    context = "\n".join(abstract_chunks)
    prompt = f"Explain this research simple like I am 5 years old. Context: {context[:1000]} Explanation:"
    return generate_response(prompt)
