"""Singleton ChromaDB client to avoid multiple connections"""
import chromadb
import os
from typing import Optional

_chroma_client: Optional[chromadb.PersistentClient] = None
_collection: Optional[chromadb.Collection] = None


def get_chroma_client() -> chromadb.PersistentClient:
    """Get or create ChromaDB client (singleton pattern)"""
    global _chroma_client
    if _chroma_client is None:
        chroma_db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        _chroma_client = chromadb.PersistentClient(path=chroma_db_path)
    return _chroma_client


def get_chroma_collection() -> chromadb.Collection:
    """Get or create ChromaDB collection (singleton pattern)"""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    return _collection

