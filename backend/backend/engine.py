"""
Core knowledge engine with vector-store-backed pipeline.
Manages documents, semantic search, and indexing using Chroma DB.
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

import chromadb
from chromadb.config import Settings

from backend.embeddings import get_embeddings_provider


class Engine:
    """Knowledge engine with Chroma DB backend."""

    def __init__(
        self,
        chroma_dir: str = None,
        embedding_provider=None,
        persistent: bool = True
    ):
        """
        Initialize the knowledge engine.
        
        Args:
            chroma_dir: Directory for Chroma DB persistence. Defaults to CHROMA_DIR env var or ./data/chroma
            embedding_provider: Custom embeddings provider. Defaults to get_embeddings_provider()
            persistent: Whether to use persistent storage. Defaults to True.
        """
        self.chroma_dir = chroma_dir or os.getenv("CHROMA_DIR", "./data/chroma")
        self.embedding_provider = embedding_provider or get_embeddings_provider()
        self.persistent = persistent

        # Ensure chroma dir exists
        if self.persistent:
            os.makedirs(self.chroma_dir, exist_ok=True)

        # Initialize Chroma client
        if self.persistent:
            settings = Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.chroma_dir,
                anonymized_telemetry=False,
            )
            self.client = chromadb.Client(settings)
        else:
            self.client = chromadb.Client()

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="knowledge",
            metadata={"hnsw:space": "cosine"}
        )

    def add(
        self,
        text: str,
        metadata: Dict[str, Any] = None,
        doc_id: str = None
    ) -> str:
        """
        Add a document to the knowledge base.
        
        Args:
            text: Document text content
            metadata: Optional metadata dict (e.g., {"source": "file.txt", "category": "spiritual"})
            doc_id: Optional custom document ID. If not provided, UUID is generated.
        
        Returns:
            Document ID
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        doc_id = doc_id or str(uuid.uuid4())
        
        # Embed the text
        embedding = self.embedding_provider.embed_single(text)
        
        # Prepare metadata
        doc_metadata = metadata or {}
        doc_metadata["added_at"] = datetime.utcnow().isoformat()
        doc_metadata["text_length"] = len(text)

        # Add to collection
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[doc_metadata]
        )

        # Persist if enabled
        if self.persistent:
            self.client.persist()

        return doc_id

    def query(
        self,
        query_text: str,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search in the knowledge base.
        
        Args:
            query_text: Query text
            top_k: Number of results. Defaults to DEFAULT_TOP_K env var or 5
        
        Returns:
            List of results with format: [{"id": str, "text": str, "metadata": dict, "distance": float}, ...]
        """
        if not query_text or not query_text.strip():
            raise ValueError("Query text cannot be empty")

        top_k = top_k or int(os.getenv("DEFAULT_TOP_K", "5"))

        # Embed query
        query_embedding = self.embedding_provider.embed_single(query_text)

        # Search in collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        # Format results
        formatted = []
        if results and results["ids"] and len(results["ids"]) > 0:
            for i, doc_id in enumerate(results["ids"][0]):
                formatted.append({
                    "id": doc_id,
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": float(results["distances"][0][i])
                })

        return formatted

    def list_docs(self) -> List[Dict[str, Any]]:
        """
        List all documents in the knowledge base.
        
        Returns:
            List of documents with format: [{"id": str, "text": str, "metadata": dict}, ...]
        """
        results = self.collection.get(include=["documents", "metadatas"])

        if not results or not results["ids"]:
            return []

        formatted = []
        for i, doc_id in enumerate(results["ids"]):
            formatted.append({
                "id": doc_id,
                "text": results["documents"][i],
                "metadata": results["metadatas"][i]
            })

        return formatted

    def delete(self, doc_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            doc_id: Document ID
        
        Returns:
            True if deleted, False if not found
        """
        try:
            self.collection.delete(ids=[doc_id])
            if self.persistent:
                self.client.persist()
            return True
        except Exception:
            return False

    def clear(self) -> int:
        """
        Clear all documents from the knowledge base.
        
        Returns:
            Number of documents deleted
        """
        count = self.collection.count()
        if count > 0:
            # Chroma doesn't have a direct clear, so delete all docs
            all_docs = self.collection.get()
            if all_docs["ids"]:
                self.collection.delete(ids=all_docs["ids"])
                if self.persistent:
                    self.client.persist()
        return count

    def reindex(self) -> None:
        """Reindex all documents (useful after configuration changes)."""
        # Get all docs
        all_docs = self.collection.get(include=["documents", "metadatas"])
        
        if not all_docs["ids"]:
            return

        # Delete all
        self.collection.delete(ids=all_docs["ids"])

        # Re-add with re-computed embeddings
        for i, doc_id in enumerate(all_docs["ids"]):
            text = all_docs["documents"][i]
            metadata = all_docs["metadatas"][i]
            embedding = self.embedding_provider.embed_single(text)

            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata]
            )

        if self.persistent:
            self.client.persist()

    def count(self) -> int:
        """Get total count of documents in the knowledge base."""
        return self.collection.count()
