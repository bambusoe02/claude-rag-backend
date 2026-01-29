"""Tests for document management endpoints"""
import pytest

def test_list_documents(client, mock_chroma_collection):
    """Test listing documents"""
    response = client.get("/api/documents/list")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "count" in data
    assert "documents" in data

def test_get_stats(client, mock_chroma_collection):
    """Test getting document statistics"""
    response = client.get("/api/documents/stats")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "total_chunks" in data
    assert "unique_documents" in data

def test_delete_document_empty_id(client):
    """Test delete with empty document ID"""
    response = client.delete("/api/documents/")
    assert response.status_code == 404

def test_delete_document_not_found(client, mock_chroma_collection):
    """Test delete with non-existent document ID"""
    mock_chroma_collection.get.return_value = {"ids": []}
    response = client.delete("/api/documents/nonexistent")
    assert response.status_code == 404




