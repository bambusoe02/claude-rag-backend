"""Pytest configuration and fixtures"""
import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Set test environment variables
os.environ["ANTHROPIC_API_KEY"] = "test_anthropic_key"
os.environ["OPENAI_API_KEY"] = "test_openai_key"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000"

@pytest.fixture
def client():
    """Create test client"""
    from main import app
    return TestClient(app)

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client"""
    with patch("rag.claude_chain.get_client") as mock:
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Test response")]
        mock_client.messages.create.return_value = mock_message
        mock.return_value = mock_client
        yield mock_client

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client"""
    with patch("rag.embeddings._get_client") as mock:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock.return_value = mock_client
        yield mock_client

@pytest.fixture
def mock_chroma_collection():
    """Mock ChromaDB collection"""
    with patch("rag.chroma_client.get_chroma_collection") as mock:
        mock_collection = MagicMock()
        mock_collection.get.return_value = {
            "ids": ["doc1_0", "doc1_1"],
            "documents": ["Test chunk 1", "Test chunk 2"],
            "metadatas": [
                {"filename": "test.pdf", "file_type": "application/pdf", "chunk_id": 0},
                {"filename": "test.pdf", "file_type": "application/pdf", "chunk_id": 1}
            ]
        }
        mock_collection.query.return_value = {
            "documents": [["Test chunk 1", "Test chunk 2"]],
            "metadatas": [[
                {"filename": "test.pdf", "chunk_id": 0},
                {"filename": "test.pdf", "chunk_id": 1}
            ]]
        }
        mock.return_value = mock_collection
        yield mock_collection


