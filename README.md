# AI Research Paper Explainer

**Deep Insights & Semantic Understanding for Academic Research**

---

### 🌐 Live Preview
- **Research Dashboard**: [Example Live Link](https://ai-research-paper-explainer.example.com/)

---

## Overview

**AI Research Paper Explainer** is a production-oriented platform that helps researchers and developers understand complex academic papers using a specialized **Retrieval-Augmented Generation (RAG)** pipeline.

Instead of generic summarization, the system:
- **Partitions** research documents into semantic chunks.
- **Generates** high-fidelity embeddings using `all-MiniLM-L6-v2`.
- **Retrieves** relevant context for multi-step reasoning.
- **Extracts** structured technical insights (Models, Datasets, Techniques, Metrics).

This approach ensures that even long, data-heavy research papers are explained with high precision and technical accuracy.

---

## Core Capabilities

- **Automated Research Summarization**: Multi-step LLM chain for TL;DR, Methodology, and Results.
- **Key Contributions Extraction**: Focused retrieval to identify exactly what a paper adds to the field.
- **Technical Entity Discovery**: Automatic identification of Models, Datasets, Algorithms, and Performance Metrics.
- **Semantic Search**: Ask questions directly to the document using vector similarity search.
- **Multi-Format Support**: Native processing for both `.pdf` and `.docx` research documents.
- **Isolated Vector Storage**: Paper-centric FAISS indices for efficient data management and privacy.
- **Modern Responsive UI**: Premium Next.js dashboard with dark mode and interactive sections.

---

## Architecture

### System Flow
```mermaid
graph TD
    A[Research Paper PDF/DOCX] -->|Upload| B[FastAPI Backend]
    B -->|Text Extraction| C[PyMuPDF / python-docx]
    C --> D[Semantic Chunking]
    D --> E[Sentence Transformers]
    E --> F[Isolated FAISS Index]
    F --> G[RAG Orchestrator]
    G --> H[Contextual Retrieval]
    H --> I[Hugging Face Qwen-2.5-7B]
    I --> J[Structured Analysis]
    J --> K[Next.js Dashboard]
```

The architecture separates the **Ingestion Pipeline** (chunking/embedding), the **Vector Store** (FAISS), and the **Reasoning Layer** (Hugging Face Inference Router). This ensures low latency and high scalability.

---

## Demo

### Working Model Preview
![Project Demo Recording](<assets/Research Paper Explainer.gif>)
*A preview of the AI Research Paper Explainer processing a document and generating technical insights.*

---

## Engineering Decisions & Design Rationale

### Why Paper-Centric FAISS?
Instead of a single massive index, the system uses isolated FAISS indices per paper. This prevents context bleed between different research topics and allows for rapid, focused retrieval within a single document's context.

### Why Qwen-2.5-7B via Unified Router?
Academic text is dense and requires a model with strong logical reasoning and technical vocabulary. Qwen-2.5 offers superior performance on instruction following and JSON-like structuring compared to other serverless models on the Hugging Face tier.

### Robust Insight Extraction Strategy
To handle the inherent variability in LLM responses (markdown artifacts, varying JSON keys), the system uses a hardened text-based tagging and regex parsing strategy. This ensures that "Models", "Datasets", and other entities are extracted even if the model's formatting fluctuates.

---

## Tech Stack

- **Frontend**: Next.js, React, Lucide Icons, Vanilla CSS
- **Backend API**: FastAPI, Uvicorn, Pydantic
- **AI/ML Layer**: Hugging Face Inference API (Qwen-2.5-7B), Sentence-Transformers, FAISS
- **Processing**: PyMuPDF, python-docx, NumPy

---

## Project Structure

```text
ai-research-paper-explainer/
├── backend/              # Research Logic & API
│   ├── api/              # FastAPI Routes (Papers, Q&A)
│   ├── core/             # Configuration & Security
│   ├── services/         # RAG, LLM Integration, Insights
│   └── vectorstore/      # FAISS Index Management
├── frontend/             # Next.js Web Application
│   ├── src/app/          # Layout & Routing
│   ├── src/components/   # Modular UI Sections
│   └── public/           # Static Assets (Logo, Icons)
├── data/                 # Isolated FAISS Indices & Registry
├── assets/               # Demo GIFs & Media
├── uploads/              # Temporary Upload Processing
├── requirements.txt      # Python Dependencies
└── README.md             # Project Master Info
```

---

## Local Development

1. **Backend Setup**:
```bash
# From root directory
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

2. **Frontend Setup**:
```bash
cd frontend
npm install
npm run dev
```

3. **Configuration**:
Ensure you have a `.env` file in the root with your `HUGGINGFACE_API_KEY`.

---

## What This Project Demonstrates
- High-fidelity RAG architecture for technical document analysis.
- Designing resilient LLM integrations on serverless inference tiers.
- Building beautiful, developer-focused React interfaces for AI tools.
- Clean Code in Python, adhering to modern FastAPI best practices.