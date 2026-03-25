import pytest
from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch, MagicMock
from io import BytesIO
import json

client = TestClient(app)

@patch("backend.api.router.extract_text_from_pdf")
def test_full_pipeline(mock_extract_pdf):
    # 1. Mock file parsing matching the blocks structure
    mock_extract_pdf.return_value = [
        {"page": 1, "blocks": [{"text": "This is a mock research paper about AI. It uses the Transformer model and achieves SOTA metrics.", "section": "abstract"}]}
    ]
    
    # Upload Paper
    fake_pdf = BytesIO(b"fake pdf content")
    response = client.post(
        "/api/papers", 
        files={"file": ("test_paper.pdf", fake_pdf, "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "paper_id" in data
    paper_id = data["paper_id"]

    # End-to-end flow: Summary
    with patch("backend.services.llm.generate_response", return_value="Mocked LLM Summary"):
        resp_summary = client.get(f"/api/papers/{paper_id}/summary")
        assert resp_summary.status_code == 200
        assert "tldr" in resp_summary.json()

    # End-to-end flow: Ask Question
    with patch("backend.services.llm.generate_response", return_value="It uses the Transformer model."):
        resp_ask = client.post(f"/api/papers/{paper_id}/ask", json={"question": "What model does it use?"})
        assert resp_ask.status_code == 200
        assert "answer" in resp_ask.json()
        assert resp_ask.json()["answer"] == "It uses the Transformer model."

    # End-to-end flow: Insights
    with patch("backend.services.llm.generate_response", return_value=json.dumps({"models": ["Transformer"], "datasets": [], "techniques": [], "metrics": ["SOTA"]})):
        resp_insights = client.get(f"/api/papers/{paper_id}/insights")
        assert resp_insights.status_code == 200
        assert "models" in resp_insights.json()

    # Verify RAG handles 'not found'
    with patch("backend.services.llm.generate_response", return_value="Not found in the paper"):
        resp_ask_empty = client.post(f"/api/papers/{paper_id}/ask", json={"question": "What about quantum computing?"})
        assert resp_ask_empty.json()["answer"] == "Not found in the paper"