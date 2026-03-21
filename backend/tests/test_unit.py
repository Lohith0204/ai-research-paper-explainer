import pytest
from unittest.mock import patch, MagicMock
from backend.services.chunking import chunk_text
from backend.services.embeddings import generate_embeddings
from backend.services.llm import generate_response

def test_chunking():
    # Adjusted format for the chunk logic, multiple blocks to exceed chunk_size
    sample_text = [{"page": 1, "blocks": [{"text": "A " * 20, "section": "abstract"}, {"text": "B " * 20, "section": "abstract"}]}]
    chunks = chunk_text(sample_text, chunk_size=2, chunk_overlap=0)
    assert len(chunks) > 1
    assert "page" in chunks[0]
    assert "text" in chunks[0]

@patch("backend.services.embeddings.get_model")
def test_embedding_generation(mock_get_model):
    mock_model = MagicMock()
    # Mocking numpy array return format
    import numpy as np
    mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
    mock_get_model.return_value = mock_model
    
    embeddings = generate_embeddings(["Test sentence"])
    assert embeddings.shape == (1, 3)
    mock_model.encode.assert_called_once()

@patch("backend.services.llm.httpx.Client.post")
def test_huggingface_api_call(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = [{"generated_text": "Mocked summary"}]
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    
    with patch("backend.services.llm.settings.HUGGINGFACE_API_KEY", "test_key"):
        result = generate_response("Explain this", model="google/flan-t5-base")
        assert result == "Mocked summary"
        mock_post.assert_called_once()
