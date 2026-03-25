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
        embeddings = await generate_embeddings(texts_to_embed)
        
        vector_store.add_paper(paper_id, file.filename, embeddings, chunks)
        
        return {
            "paper_id": paper_id,
            "filename": file.filename,
            "message": "Paper optimized for session-based analysis."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# Internal helper functions that return data or raise standard exceptions
async def _extract_summary(paper_id: str):
    paper_chunks = vector_store.get_paper_chunks(paper_id)
    if not paper_chunks:
        raise ValueError("Paper not found")
    return summarize_paper_multi_step(paper_chunks)

async def _extract_insights(paper_id: str):
    paper_chunks = vector_store.get_paper_chunks(paper_id)
    if not paper_chunks:
        raise ValueError("Paper not found")
    # Balanced context extraction
    total = len(paper_chunks)
    indices = list(range(min(3, total)))
    if total > 6:
        indices.extend(range(total // 2 - 1, total // 2 + 2))
    context = [paper_chunks[i]["text"] for i in indices]
    return extract_insights(context)

async def _extract_graph(paper_id: str):
    paper_chunks = vector_store.get_paper_chunks(paper_id)
    if not paper_chunks:
        raise ValueError("Paper not found")
    context = [c["text"] for c in paper_chunks[:5]]
    return extract_knowledge_graph(context)

@router.post("/papers/process")
async def process_full_paper(file: UploadFile = File(...)):
    """Fast, single-call analysis for Vercel efficiency."""
    try:
        res = await upload_paper(file)
        paper_id = res["paper_id"]
        
        import asyncio
        async def safe_task(coro):
            try:
                return await coro
            except Exception as e:
                print(f"Sub-task error in process_full_paper: {str(e)}")
                return None

        # Run analysis steps in parallel using internal helpers
        summary, insights, graph = await asyncio.gather(
            safe_task(_extract_summary(paper_id)),
            safe_task(_extract_insights(paper_id)),
            safe_task(_extract_graph(paper_id))
        )
        
        return {
            **res,
            "summary": summary or {"tldr": "Analysis failed for this section."},
            "insights": insights,
            "graph": graph
        }
    except Exception as e:
        import traceback
        print(f"CRITICAL: process_full_paper failed: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/papers/{paper_id}/summary")
async def get_paper_summary(paper_id: str = Path(...)):
    try:
        return await _extract_summary(paper_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/papers/{paper_id}/insights")
async def get_paper_insights(paper_id: str = Path(...)):
    try:
        return await _extract_insights(paper_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/papers/{paper_id}/graph")
async def get_paper_graph(paper_id: str = Path(...)):
    try:
        return await _extract_graph(paper_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
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
        results = await retrieve_and_rerank(paper_id, request.question, top_k=5)
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
        results = await retrieve_and_rerank(paper_id, query, top_k=top_k)
        if not results:
            return {"message": "No results found matching your query.", "results": []}
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# End of router
