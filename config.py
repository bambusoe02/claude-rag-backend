"""Application configuration constants"""
import os

# File upload settings
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB default
ALLOWED_EXTENSIONS = ['.pdf', '.txt', '.md', '.docx']
ALLOWED_MIME_TYPES = [
    'application/pdf',
    'text/plain',
    'text/markdown',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]

# API settings
ANTHROPIC_TIMEOUT = int(os.getenv("ANTHROPIC_TIMEOUT", 30))  # 30 seconds
OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", 30))  # 30 seconds
API_MAX_RETRIES = int(os.getenv("API_MAX_RETRIES", 3))  # 3 retries

# Chunking settings
DEFAULT_CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

