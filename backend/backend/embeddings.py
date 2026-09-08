"""
Embeddings abstraction layer.
Supports OpenAI embeddings with local sentence-transformers fallback.
"""

import os
from typing import List


class EmbeddingsProvider:
    """Base class for embeddings providers."""

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts and return vectors."""
        raise NotImplementedError

    def embed_single(self, text: str) -> List[float]:
        """Embed a single text and return a vector."""
        vectors = self.embed([text])
        return vectors[0] if vectors else []


class OpenAIEmbeddings(EmbeddingsProvider):
    """OpenAI embeddings provider."""

    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        """Initialize OpenAI embeddings."""
        try:
            import openai
        except ImportError:
            raise ImportError("openai package required for OpenAI embeddings. Install with: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Embed texts using OpenAI API."""
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [item.embedding for item in response.data]


class LocalEmbeddings(EmbeddingsProvider):
    """Local embeddings using sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize local embeddings with sentence-transformers."""
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers package required for local embeddings. "
                "Install with: pip install sentence-transformers"
            )

        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Embed texts using local model."""
        embeddings = self.model.encode(texts, convert_to_numpy=False)
        return [emb.tolist() if hasattr(emb, 'tolist') else emb for emb in embeddings]


def get_embeddings_provider() -> EmbeddingsProvider:
    """
    Get the appropriate embeddings provider based on environment configuration.
    
    Tries OpenAI first if OPENAI_API_KEY is set, falls back to local embeddings.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "").lower()

    # If provider explicitly set to 'local', use local
    if embedding_provider == "local":
        return LocalEmbeddings()

    # If OpenAI key is present, try OpenAI (even if provider is not set)
    if openai_key:
        try:
            return OpenAIEmbeddings(api_key=openai_key)
        except ImportError:
            print("OpenAI package not available, falling back to local embeddings")
            return LocalEmbeddings()

    # Default to local if no key and provider not specified
    return LocalEmbeddings()
