"""
FastAPI routes for knowledge engine endpoints.
Exposes semantic search, document management, and configuration.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from backend.engine import Engine

# Initialize router and engine
router = APIRouter(prefix="/knowledge", tags=["knowledge"])
engine = Engine()


# Request/Response models
class AddDocumentRequest(BaseModel):
    """Request model for adding a document."""
    text: str
    metadata: Optional[Dict[str, Any]] = None
    doc_id: Optional[str] = None


class AddDocumentResponse(BaseModel):
    """Response model for add document endpoint."""
    doc_id: str
    message: str


class QueryResponse(BaseModel):
    """Response model for query results."""
    query: str
    results: List[Dict[str, Any]]
    count: int


class DocumentListResponse(BaseModel):
    """Response model for document list."""
    documents: List[Dict[str, Any]]
    total: int


class DeleteResponse(BaseModel):
    """Response model for delete operations."""
    message: str
    deleted_count: int


# Endpoints

@router.post("/add", response_model=AddDocumentResponse)
def add_document(request: AddDocumentRequest):
    """
    Add a document to the knowledge base.
    
    **Parameters:**
    - `text`: Document content (required)
    - `metadata`: Optional metadata dict (e.g., {"source": "file.txt", "category": "spiritual"})
    - `doc_id`: Optional custom document ID
    
    **Returns:**
    - `doc_id`: Generated or provided document ID
    
    **Example:**
    ```
    curl -X POST "http://localhost:8000/knowledge/add" \\
      -H "Content-Type: application/json" \\
      -d '{"text": "Enlightenment is the path to inner peace", "metadata": {"source": "wisdom"}}'
    ```
    """
    try:
        doc_id = engine.add(
            text=request.text,
            metadata=request.metadata,
            doc_id=request.doc_id
        )
        return AddDocumentResponse(
            doc_id=doc_id,
            message=f"Document '{doc_id}' added successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding document: {str(e)}")


@router.get("/query", response_model=QueryResponse)
def query_documents(
    q: str = Query(..., description="Query text"),
    top_k: Optional[int] = Query(None, description="Number of results (default: 5)")
):
    """
    Perform semantic search in the knowledge base.
    
    **Parameters:**
    - `q`: Search query (required)
    - `top_k`: Max results to return (default: 5, or DEFAULT_TOP_K env var)
    
    **Returns:**
    - `query`: The query that was executed
    - `results`: List of matching documents with scores
    - `count`: Number of results
    
    **Example:**
    ```
    curl "http://localhost:8000/knowledge/query?q=meditation&top_k=3"
    ```
    """
    try:
        results = engine.query(query_text=q, top_k=top_k)
        return QueryResponse(
            query=q,
            results=results,
            count=len(results)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying documents: {str(e)}")


@router.get("/docs", response_model=DocumentListResponse)
def list_documents():
    """
    List all documents in the knowledge base.
    
    **Returns:**
    - `documents`: List of all documents with metadata
    - `total`: Total document count
    
    **Example:**
    ```
    curl "http://localhost:8000/knowledge/docs"
    ```
    """
    try:
        docs = engine.list_docs()
        return DocumentListResponse(
            documents=docs,
            total=len(docs)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@router.delete("/docs/{doc_id}")
def delete_document(doc_id: str):
    """
    Delete a specific document by ID.
    
    **Parameters:**
    - `doc_id`: Document ID to delete
    
    **Returns:**
    - `message`: Status message
    
    **Example:**
    ```
    curl -X DELETE "http://localhost:8000/knowledge/docs/123e4567-e89b-12d3-a456-426614174000"
    ```
    """
    try:
        deleted = engine.delete(doc_id=doc_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found")
        return {"message": f"Document '{doc_id}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@router.delete("/clear", response_model=DeleteResponse)
def clear_all():
    """
    Clear all documents from the knowledge base.
    
    **Returns:**
    - `message`: Status message
    - `deleted_count`: Number of documents deleted
    
    **Example:**
    ```
    curl -X DELETE "http://localhost:8000/knowledge/clear"
    ```
    """
    try:
        count = engine.clear()
        return DeleteResponse(
            message="Knowledge base cleared successfully",
            deleted_count=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing knowledge base: {str(e)}")


@router.post("/reindex")
def reindex():
    """
    Reindex all documents (useful after embedding provider changes).
    
    **Returns:**
    - `message`: Status message
    - `reindexed_count`: Number of documents reindexed
    
    **Example:**
    ```
    curl -X POST "http://localhost:8000/knowledge/reindex"
    ```
    """
    try:
        count = engine.count()
        engine.reindex()
        return {
            "message": "Knowledge base reindexed successfully",
            "reindexed_count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reindexing: {str(e)}")


@router.get("/health")
def health_check():
    """
    Health check for the knowledge engine.
    
    **Returns:**
    - `status`: Service status
    - `doc_count`: Number of documents in store
    
    **Example:**
    ```
    curl "http://localhost:8000/knowledge/health"
    ```
    """
    try:
        count = engine.count()
        return {
            "status": "healthy",
            "doc_count": count
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Engine unhealthy: {str(e)}")
