"""Tests for health check endpoints"""
import pytest

def test_root_endpoint(client):
    """Test root endpoint returns status"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "Claude RAG API running"

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "claude-rag-api"


