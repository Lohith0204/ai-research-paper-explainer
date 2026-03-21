from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Path
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import uuid
import shutil

from backend.services.pdf_parser import extract_text_from_pdf
from backend.services.docx_parser import extract_text_from_docx
from backend.services.chunking import chunk_text
from backend.services.embeddings import generate_embeddings
from backend.services.llm import summarize_paper_multi_step, answer_question, explain_simple
from backend.services.insights import extract_insights
from backend.services.graph import extract_knowledge_graph
from backend.services.retrieval import retrieve_and_rerank
from backend.vectorstore.faiss_store import vector_store
from backend.core.config import settings

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class AskRequest(BaseModel):
    question: str

@router.post("/papers")
async def upload_paper(file: UploadFile = File(...)):
    if not (file.filename.endswith(".pdf") or file.filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are supported")
        
    paper_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{paper_id}_{file.filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        if file.filename.endswith(".pdf"):
            pages_data = extract_text_from_pdf(file_path)
        else:
            pages_data = extract_text_from_docx(file_path)
            
        if not pages_data:
            raise HTTPException(status_code=400, detail="Could not extract text or document is empty")
            
        chunks = chunk_text(pages_data, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        texts_to_embed = [c["text"] for c in chunks]
        embeddings = generate_embeddings(texts_to_embed)
        
        vector_store.add_paper(paper_id, file.filename, embeddings, chunks)
        
        return {
            "paper_id": paper_id,
            "filename": file.filename,
            "message": "Paper processed structured successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@router.get("/papers")
async def list_papers():
    return {"papers": vector_store.list_papers()}

@router.get("/papers/{paper_id}")
async def get_paper_metadata(paper_id: str = Path(...)):
    papers = vector_store.list_papers()
    for p in papers:
        if p["paper_id"] == paper_id:
            return p
    raise HTTPException(status_code=404, detail="Paper not found")

@router.get("/papers/{paper_id}/summary")
async def get_paper_summary(paper_id: str = Path(...)):
    try:
        paper_chunks = vector_store.get_paper_chunks(paper_id)
        if not paper_chunks:
            raise HTTPException(status_code=404, detail="Paper not found")
            
        summary = summarize_paper_multi_step(paper_chunks)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/papers/{paper_id}/explain-simple")
async def get_paper_eli5(paper_id: str = Path(...)):
    """ELI5 simple explanation focusing on the abstract."""
    try:
        paper_chunks = vector_store.get_paper_chunks(paper_id)
        if not paper_chunks:
            raise HTTPException(status_code=404, detail="Paper not found")
            
        abstract_chunks = [c["text"] for c in paper_chunks if c.get("section") == "abstract"]
        if not abstract_chunks:
            abstract_chunks = [c["text"] for c in paper_chunks[:3]]
            
        simple_explanation = explain_simple(abstract_chunks[:4])
        return {"simple_explanation": simple_explanation.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/papers/{paper_id}/ask")
async def ask_question(request: AskRequest, paper_id: str = Path(...)):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
        
    try:
        results = retrieve_and_rerank(paper_id, request.question, top_k=5)
        if not results:
            return {"answer": "Not found in the paper", "context_used": []}
            
        context_chunks = [r["text"] for r in results]
        answer = answer_question(context_chunks, request.question)
        
        return {
            "answer": answer,
            "context_used": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/papers/{paper_id}/search")
async def search_paper(
    query: str, 
    paper_id: str = Path(...), 
    top_k: int = Query(default=settings.TOP_K_RETRIEVAL)
):
    try:
        results = retrieve_and_rerank(paper_id, query, top_k=top_k)
        if not results:
            return {"message": "No results found matching your query.", "results": []}
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/papers/{paper_id}/insights")
async def get_paper_insights(paper_id: str = Path(...)):
    """Extract models, datasets, techniques, metrics."""
    try:
        paper_chunks = vector_store.get_paper_chunks(paper_id)
        if not paper_chunks:
            raise HTTPException(status_code=404, detail="Paper not found")
            
        # Take 3 head and 3 middle chunks for balanced, concise context
        total = len(paper_chunks)
        indices = list(range(min(3, total))) # Head 3
        if total > 6:
            indices.extend(range(total // 2 - 1, total // 2 + 2)) # Middle 3
            
        unique_indices = sorted(list(set(indices)))
        texts_to_extract = [paper_chunks[i]["text"] for i in unique_indices]
        
        insights_data = extract_insights(texts_to_extract)
        return insights_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/papers/{paper_id}/graph")
async def get_paper_graph(paper_id: str = Path(...)):
    try:
        paper_chunks = vector_store.get_paper_chunks(paper_id)
        if not paper_chunks:
            raise HTTPException(status_code=404, detail="Paper not found")
            
        texts_to_extract = [m["text"] for m in paper_chunks[:4]]
        graph_data = extract_knowledge_graph(texts_to_extract)
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
