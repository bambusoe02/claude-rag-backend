from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import chromadb

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="documents")

@router.get("/list")
async def list_documents() -> Dict[str, Any]:
    """List all uploaded documents"""
    
    try:
        # Get all documents from collection
        results = collection.get()
        
        # Extract unique documents by filename
        documents = {}
        if results['metadatas']:
            for i, metadata in enumerate(results['metadatas']):
                filename = metadata.get('filename', 'unknown')
                if filename not in documents:
                    documents[filename] = {
                        "filename": filename,
                        "file_type": metadata.get('file_type', 'unknown'),
                        "chunks": 0
                    }
                documents[filename]["chunks"] += 1
        
        return {
            "success": True,
            "count": len(documents),
            "documents": list(documents.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@router.delete("/{doc_id}")
async def delete_document(doc_id: str) -> Dict[str, Any]:
    """Delete a document by ID"""
    
    try:
        # Get all IDs that match the doc_id prefix
        results = collection.get()
        ids_to_delete = []
        
        if results['ids']:
            for doc_id_in_db in results['ids']:
                if doc_id_in_db.startswith(doc_id):
                    ids_to_delete.append(doc_id_in_db)
        
        if not ids_to_delete:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from collection
        collection.delete(ids=ids_to_delete)
        
        return {
            "success": True,
            "message": f"Deleted document with {len(ids_to_delete)} chunks",
            "doc_id": doc_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Get statistics about the document collection"""
    
    try:
        results = collection.get()
        total_chunks = len(results['ids']) if results['ids'] else 0
        
        # Count unique documents
        unique_docs = set()
        if results['metadatas']:
            for metadata in results['metadatas']:
                filename = metadata.get('filename', 'unknown')
                unique_docs.add(filename)
        
        return {
            "success": True,
            "total_chunks": total_chunks,
            "unique_documents": len(unique_docs),
            "collection_name": "documents"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

