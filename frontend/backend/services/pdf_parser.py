import fitz
import re

def extract_text_from_pdf(file_path: str):
    """
    Extracts text from a PDF, predicting section headers (Abstract, Intro, etc).
    """
    pages_data = []
    SECTION_KEYWORDS = {
        "abstract": re.compile(r"^abstract", re.IGNORECASE),
        "introduction": re.compile(r"^1\.?\s*introduction|^introduction", re.IGNORECASE),
        "related work": re.compile(r"^2\.?\s*related work|^related work|^background", re.IGNORECASE),
        "methodology": re.compile(r"^3\.?\s*method|^methodology|^approach|^model", re.IGNORECASE),
        "experiments": re.compile(r"^4\.?\s*experiment|^evaluation", re.IGNORECASE),
        "results": re.compile(r"^5\.?\s*result|^discussion", re.IGNORECASE),
        "conclusion": re.compile(r"^6\.?\s*conclusion|^future work", re.IGNORECASE),
        "references": re.compile(r"^references|^bibliography", re.IGNORECASE)
    }
    
    current_section = "general"
    
    try:
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("blocks")
            blocks.sort(key=lambda b: b[1])
            
            page_text_blocks = []
            
            for block in blocks:
                block_text = block[4].strip()
                if not block_text:
                    continue
                block_text = re.sub(r'\s+', ' ', block_text)
                
                if len(block_text.split()) < 10:
                    for sec_name, sec_regex in SECTION_KEYWORDS.items():
                        if sec_regex.match(block_text):
                            current_section = sec_name
                            break
                            
                page_text_blocks.append({
                    "text": block_text,
                    "section": current_section
                })
            
            if page_text_blocks:
                pages_data.append({
                    "blocks": page_text_blocks,
                    "page": page_num + 1
                })
        
        doc.close()
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        
    return pages_data
