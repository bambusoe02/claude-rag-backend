"""Tests for startup validation"""
import pytest
import os
from unittest.mock import patch

def test_startup_with_missing_env_vars():
    """Test that startup fails with missing environment variables"""
    # Clear required env vars
    original_anthropic = os.environ.get("ANTHROPIC_API_KEY")
    original_openai = os.environ.get("OPENAI_API_KEY")
    
    try:
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        
        # Import should raise ValueError
        with pytest.raises(ValueError, match="Missing required environment variables"):
            from main import app
            # Trigger startup event
            import asyncio
            asyncio.run(app.router.on_startup[0]())
    finally:
        # Restore original values
        if original_anthropic:
            os.environ["ANTHROPIC_API_KEY"] = original_anthropic
        if original_openai:
            os.environ["OPENAI_API_KEY"] = original_openai

def test_startup_with_all_env_vars():
    """Test that startup succeeds with all required environment variables"""
    os.environ["ANTHROPIC_API_KEY"] = "test_key"
    os.environ["OPENAI_API_KEY"] = "test_key"
    
    try:
        from main import app
        # Should not raise
        assert app is not None
    except ValueError:
        pytest.fail("Startup should not fail when all env vars are set")



