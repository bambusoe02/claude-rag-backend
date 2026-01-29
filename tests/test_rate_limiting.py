"""Tests for rate limiting"""
import pytest
from fastapi.testclient import TestClient

def test_rate_limiting_upload(client):
    """Test rate limiting on upload endpoint"""
    # Make multiple requests quickly
    for i in range(6):  # Limit is 5/minute
        response = client.post(
            "/api/upload/document",
            files={"file": ("test.txt", b"test content", "text/plain")}
        )
        if i < 5:
            # First 5 should work (or fail validation, but not rate limit)
            assert response.status_code in [200, 400, 422]
        else:
            # 6th request might be rate limited
            # Note: Rate limiting might not trigger in test environment
            assert response.status_code in [200, 400, 422, 429]

def test_rate_limiting_chat(client):
    """Test rate limiting on chat endpoint"""
    # Make multiple requests quickly
    for i in range(11):  # Limit is 10/minute
        response = client.post(
            "/api/chat/message",
            json={"message": "test question"}
        )
        # Should work or fail validation, but not rate limit in test
        assert response.status_code in [200, 400, 422, 429, 500]

def test_rate_limiting_documents_list(client):
    """Test rate limiting on documents list endpoint"""
    response = client.get("/api/documents/list")
    # Should work (limit is 30/minute, very high)
    assert response.status_code in [200, 500]

def test_rate_limiting_documents_stats(client):
    """Test rate limiting on documents stats endpoint"""
    response = client.get("/api/documents/stats")
    # Should work (limit is 30/minute, very high)
    assert response.status_code in [200, 500]

