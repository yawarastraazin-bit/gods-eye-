"""
Integration tests for the knowledge engine.
Uses temporary directory for Chroma store to avoid side effects.
"""

import os
import tempfile
import pytest
from backend.engine import Engine
from backend.embeddings import LocalEmbeddings


@pytest.fixture
def temp_chroma_dir():
    """Create a temporary directory for Chroma DB."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def engine(temp_chroma_dir):
    """Create an engine instance with temporary storage."""
    embeddings = LocalEmbeddings()
    eng = Engine(chroma_dir=temp_chroma_dir, embedding_provider=embeddings, persistent=True)
    yield eng
    # Cleanup
    eng.clear()


class TestEngineBasics:
    """Test basic engine operations."""

    def test_engine_initialization(self, engine):
        """Test that engine initializes correctly."""
        assert engine is not None
        assert engine.count() == 0

    def test_add_document(self, engine):
        """Test adding a single document."""
        doc_id = engine.add("This is a test document")
        assert doc_id is not None
        assert engine.count() == 1

    def test_add_document_with_metadata(self, engine):
        """Test adding a document with metadata."""
        metadata = {"source": "test", "category": "wisdom"}
        doc_id = engine.add("Test document", metadata=metadata)
        
        docs = engine.list_docs()
        assert len(docs) == 1
        assert docs[0]["metadata"]["source"] == "test"
        assert docs[0]["metadata"]["category"] == "wisdom"

    def test_add_document_with_custom_id(self, engine):
        """Test adding a document with custom ID."""
        custom_id = "my-doc-123"
        doc_id = engine.add("Test document", doc_id=custom_id)
        
        assert doc_id == custom_id
        docs = engine.list_docs()
        assert docs[0]["id"] == custom_id

    def test_add_empty_document_raises_error(self, engine):
        """Test that adding empty text raises ValueError."""
        with pytest.raises(ValueError):
            engine.add("")
        
        with pytest.raises(ValueError):
            engine.add("   ")


class TestEngineQuery:
    """Test semantic search functionality."""

    def test_query_single_document(self, engine):
        """Test querying a single document."""
        engine.add("Meditation is a spiritual practice")
        
        results = engine.query("meditation")
        assert len(results) > 0
        assert results[0]["text"] == "Meditation is a spiritual practice"

    def test_query_multiple_documents(self, engine):
        """Test querying with multiple documents."""
        docs = [
            "Meditation is a spiritual practice",
            "Yoga helps with flexibility and peace",
            "Prayer connects you to the divine",
            "Breathing exercises calm the mind"
        ]
        
        for doc in docs:
            engine.add(doc)
        
        results = engine.query("meditation and spiritual", top_k=3)
        assert len(results) <= 3
        assert len(results) > 0

    def test_query_with_top_k(self, engine):
        """Test that top_k limits results."""
        docs = [
            "First document about peace",
            "Second document about peace",
            "Third document about peace",
            "Fourth document about peace",
            "Fifth document about peace"
        ]
        
        for doc in docs:
            engine.add(doc)
        
        results = engine.query("peace", top_k=2)
        assert len(results) == 2

    def test_query_empty_raises_error(self, engine):
        """Test that empty query raises ValueError."""
        with pytest.raises(ValueError):
            engine.query("")
        
        with pytest.raises(ValueError):
            engine.query("   ")

    def test_query_empty_collection_returns_empty(self, engine):
        """Test that querying empty collection returns empty results."""
        results = engine.query("something")
        assert len(results) == 0


class TestEngineDocumentManagement:
    """Test document listing, deletion, and clearing."""

    def test_list_documents(self, engine):
        """Test listing all documents."""
        engine.add("Doc 1")
        engine.add("Doc 2")
        engine.add("Doc 3")
        
        docs = engine.list_docs()
        assert len(docs) == 3

    def test_list_empty_collection(self, engine):
        """Test listing empty collection."""
        docs = engine.list_docs()
        assert len(docs) == 0

    def test_delete_document(self, engine):
        """Test deleting a specific document."""
        doc_id = engine.add("Document to delete")
        assert engine.count() == 1
        
        deleted = engine.delete(doc_id)
        assert deleted is True
        assert engine.count() == 0

    def test_delete_nonexistent_document(self, engine):
        """Test deleting a non-existent document."""
        deleted = engine.delete("nonexistent-id")
        assert deleted is False

    def test_clear_collection(self, engine):
        """Test clearing all documents."""
        engine.add("Doc 1")
        engine.add("Doc 2")
        engine.add("Doc 3")
        assert engine.count() == 3
        
        count = engine.clear()
        assert count == 3
        assert engine.count() == 0

    def test_clear_empty_collection(self, engine):
        """Test clearing empty collection."""
        count = engine.clear()
        assert count == 0


class TestEngineReindex:
    """Test reindexing functionality."""

    def test_reindex_preserves_documents(self, engine):
        """Test that reindex preserves all documents."""
        docs_to_add = [
            "First spiritual text",
            "Second sacred wisdom",
            "Third divine knowledge"
        ]
        
        for doc in docs_to_add:
            engine.add(doc)
        
        initial_count = engine.count()
        engine.reindex()
        
        assert engine.count() == initial_count
        
        # Verify all docs still exist
        docs = engine.list_docs()
        assert len(docs) == 3

    def test_reindex_empty_collection(self, engine):
        """Test reindex on empty collection."""
        engine.reindex()  # Should not raise
        assert engine.count() == 0


class TestEnginePersistence:
    """Test persistence across instances."""

    def test_persistence_across_instances(self, temp_chroma_dir):
        """Test that data persists across engine instances."""
        embeddings = LocalEmbeddings()
        
        # Create first engine and add docs
        engine1 = Engine(chroma_dir=temp_chroma_dir, embedding_provider=embeddings)
        doc_id = engine1.add("Persistent document")
        assert engine1.count() == 1
        
        # Create second engine with same directory
        engine2 = Engine(chroma_dir=temp_chroma_dir, embedding_provider=embeddings)
        assert engine2.count() == 1
        
        # Verify document exists
        docs = engine2.list_docs()
        assert len(docs) == 1
        assert docs[0]["text"] == "Persistent document"


class TestEngineMetadata:
    """Test metadata handling."""

    def test_metadata_timestamp(self, engine):
        """Test that added_at timestamp is set."""
        engine.add("Document with timestamp")
        
        docs = engine.list_docs()
        assert "added_at" in docs[0]["metadata"]
        assert docs[0]["metadata"]["added_at"] is not None

    def test_metadata_text_length(self, engine):
        """Test that text_length is recorded."""
        text = "This is a test document"
        engine.add(text)
        
        docs = engine.list_docs()
        assert docs[0]["metadata"]["text_length"] == len(text)

    def test_custom_metadata_preserved(self, engine):
        """Test that custom metadata is preserved."""
        custom_meta = {
            "author": "Test Author",
            "source": "test_file.txt",
            "category": "wisdom",
            "nested": {"key": "value"}
        }
        
        engine.add("Document", metadata=custom_meta)
        
        docs = engine.list_docs()
        doc_meta = docs[0]["metadata"]
        
        assert doc_meta["author"] == "Test Author"
        assert doc_meta["source"] == "test_file.txt"
        assert doc_meta["category"] == "wisdom"
        assert doc_meta["nested"]["key"] == "value"


class TestEngineQueryResults:
    """Test query result format and distance metrics."""

    def test_query_result_format(self, engine):
        """Test that query results have correct format."""
        engine.add("Enlightenment through meditation")
        
        results = engine.query("meditation", top_k=1)
        assert len(results) == 1
        
        result = results[0]
        assert "id" in result
        assert "text" in result
        assert "metadata" in result
        assert "distance" in result

    def test_query_result_distance(self, engine):
        """Test that distance is a float between 0 and 2 (cosine)."""
        engine.add("Perfect match document")
        
        results = engine.query("Perfect match document", top_k=1)
        assert len(results) == 1
        
        distance = results[0]["distance"]
        assert isinstance(distance, float)
        assert 0 <= distance <= 2  # Cosine distance range


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
