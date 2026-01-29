"""Tests for service functions"""
import pytest
from services.chunker import chunk_text
from services.parser import parse_text, parse_markdown

def test_chunk_text_basic():
    """Test basic text chunking"""
    text = "This is a test document. " * 50
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 0
    assert all(len(chunk) > 0 for chunk in chunks)

def test_chunk_text_empty():
    """Test chunking empty text"""
    chunks = chunk_text("", chunk_size=100, overlap=20)
    assert chunks == []

def test_chunk_text_invalid_size():
    """Test chunking with invalid chunk size"""
    with pytest.raises(ValueError):
        chunk_text("Test text", chunk_size=0, overlap=20)

def test_chunk_text_invalid_overlap():
    """Test chunking with invalid overlap"""
    with pytest.raises(ValueError):
        chunk_text("Test text", chunk_size=100, overlap=100)

def test_parse_text():
    """Test parsing plain text"""
    content = b"Test content"
    result = parse_text(content)
    assert result == "Test content"

def test_parse_markdown():
    """Test parsing markdown"""
    content = b"# Test\n\nContent here"
    result = parse_markdown(content)
    assert "# Test" in result




