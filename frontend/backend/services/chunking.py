from typing import List, Dict
import re
from backend.core.config import settings

def chunk_text(pages_data: List[Dict], chunk_size: int = None, chunk_overlap: int = None) -> List[Dict]:
    """
    Splits page text into smart chunks, preserving section boundaries.
    """
    if chunk_size is None:
        chunk_size = settings.CHUNK_SIZE
    if chunk_overlap is None:
        chunk_overlap = settings.CHUNK_OVERLAP
        
    chunks = []
    current_chunk = ""
    current_length = 0
    current_section = "general"
    current_page = 1
    
    for page in pages_data:
        page_num = page["page"]
        blocks = page.get("blocks", [])
        
        for block in blocks:
            text = block["text"].strip()
            section = block["section"]
            
            if not text:
                continue
                
            if section != current_section and current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "page": current_page,
                    "section": current_section
                })
                current_chunk = ""
                current_length = 0
            
            current_section = section
            current_page = page_num
            
            para_len = len(text.split())
            
            if current_length + para_len > chunk_size and current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "page": current_page,
                    "section": current_section
                })
                overlap_words = current_chunk.split()[-chunk_overlap:] if chunk_overlap > 0 else []
                current_chunk = " ".join(overlap_words) + "\n\n" + text
                current_length = len(current_chunk.split())
            else:
                current_chunk += ("\n\n" if current_chunk else "") + text
                current_length += para_len
                
    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "page": current_page,
            "section": current_section
        })
            
    return chunks
