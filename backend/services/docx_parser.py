import docx
import re

def extract_text_from_docx(file_path: str):
    """
    Extracts text from a DOCX file, mapping heading styles to standard research paper sections.
    """
    pages_data = []
    
    SECTION_KEYWORDS = {
        "abstract": re.compile(r"abstract", re.IGNORECASE),
        "introduction": re.compile(r"introduction", re.IGNORECASE),
        "related work": re.compile(r"related|background", re.IGNORECASE),
        "methodology": re.compile(r"method|approach|model", re.IGNORECASE),
        "experiments": re.compile(r"experiment|evaluation", re.IGNORECASE),
        "results": re.compile(r"result|discussion", re.IGNORECASE),
        "conclusion": re.compile(r"conclusion|future", re.IGNORECASE),
        "references": re.compile(r"reference|bibliography", re.IGNORECASE)
    }
    
    current_section = "general"
    
    try:
        doc = docx.Document(file_path)
        page_text_blocks = []
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
                
            text = re.sub(r'\s+', ' ', text)
            
            is_heading = para.style.name.startswith('Heading') or (len(text.split()) < 10 and text.isupper())
            
            if is_heading:
                for sec_name, sec_regex in SECTION_KEYWORDS.items():
                    if sec_regex.search(text):
                        current_section = sec_name
                        break
            
            page_text_blocks.append({
                "text": text,
                "section": current_section
            })
            
        if page_text_blocks:
            pages_data.append({
                "blocks": page_text_blocks,
                "page": 1
            })
            
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
        
    return pages_data
