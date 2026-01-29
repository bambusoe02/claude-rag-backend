"""Tests for chat endpoints"""
import pytest
from unittest.mock import patch

def test_chat_message_success(client, mock_anthropic_client, mock_chroma_collection):
    """Test successful chat message"""
    response = client.post(
        "/api/chat/message",
        json={"message": "What is this document about?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "sources" in data
    assert "conversation_id" in data

def test_chat_message_empty(client):
    """Test chat with empty message"""
    response = client.post(
        "/api/chat/message",
        json={"message": ""}
    )
    assert response.status_code == 400

def test_chat_message_no_documents(client, mock_anthropic_client):
    """Test chat when no documents are available"""
    with patch("rag.chroma_client.get_chroma_collection") as mock_collection:
        mock_collection.return_value.query.return_value = {
            "documents": [[]],
            "metadatas": [[]]
        }
        response = client.post(
            "/api/chat/message",
            json={"message": "Test question"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "I don't have any relevant documents" in data["response"]


