import re
from typing import List, Dict
from backend.services.llm import generate_response

def extract_insights(context_chunks: List[str]) -> Dict:
    """
    Extracts structured technical insights using a robust text-based prompt and manual parsing.
    """
    context = "\n\n".join(context_chunks)
    
    prompt = f"""
You are an expert technical data extractor. Read the following context from a research paper.
Extract the following information:
- MODELS: Specific software tools, formal frameworks, or theoretical models used.
- DATASETS: Databases, public datasets, or specific data sources mentioned.
- TECHNIQUES: Specific algorithms, mathematical methods, or operational procedures described.
- METRICS: Success indicators, measurement criteria, or performance targets mentioned.

Context:
{context}

Format your response EXACTLY like this (one per line):
[MODELS] item1, item2
[DATASETS] item1, item2
[TECHNIQUES] item1, item2
[METRICS] item1, item2

If nothing is found for a category, return 'None' for that category.
Response:"""

    response_text = generate_response(prompt, json_format=False)
    
    insights = {
        "models": [],
        "datasets": [],
        "techniques": [],
        "metrics": []
    }
    
    def parse_line(tag: str, text: str) -> List[str]:
        # Search for tag and capture everything until the next bracketed tag or end of line
        # This handles "**[MODELS]**", "[MODELS]:", "MODELS - ", etc.
        pattern = fr"{tag}.*?[:\]\-\s]\s*([^\[\n]*)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            items_str = match.group(1).strip()
            if items_str.lower() == "none" or not items_str or items_str == "-":
                return []
            # Split by comma or semicolon and clean
            separators = r'[;,]'
            return [i.strip() for i in re.split(separators, items_str) if i.strip()]
        return []

    insights["models"] = parse_line("MODELS", response_text)
    insights["datasets"] = parse_line("DATASETS", response_text)
    insights["techniques"] = parse_line("TECHNIQUES", response_text)
    insights["metrics"] = parse_line("METRICS", response_text)
    
    return insights
