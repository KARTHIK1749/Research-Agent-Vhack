"""
Service for creating and managing paper embeddings.
Uses sentence-transformers for embeddings and FAISS for similarity search.
"""
import os
from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

from app.models.schemas import Paper

# Global model instance (loaded once)
_model = None

def _get_model() -> SentenceTransformer:
    """Get or initialize the embedding model."""
    global _model
    if _model is None:
        # Using a lightweight but effective model
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def create_paper_embeddings(papers: List[Paper]) -> Tuple[np.ndarray, List[Paper]]:
    """
    Create embeddings for papers based on title and summary.

    Args:
        papers: List of papers to embed

    Returns:
        Tuple of (embeddings array, papers list)
    """
    model = _get_model()

    # Combine title and summary for richer embeddings
    texts = [f"{p.title}. {p.summary}" for p in papers]

    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    return embeddings, papers


def search_similar_papers(
    query: str,
    papers: List[Paper],
    embeddings: np.ndarray,
    top_k: int = 5
) -> List[Tuple[Paper, float]]:
    """
    Search for papers most similar to a query.

    Args:
        query: Search query
        papers: List of papers
        embeddings: Pre-computed embeddings matrix
        top_k: Number of results to return

    Returns:
        List of (paper, score) tuples, sorted by relevance
    """
    model = _get_model()
    query_embedding = model.encode([query], convert_to_numpy=True)

    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)
    faiss.normalize_L2(query_embedding)

    index.add(embeddings)

    # Search
    scores, indices = index.search(query_embedding, k=min(top_k, len(papers)))

    results = []
    for idx, score in zip(indices[0], scores[0]):
        if idx < len(papers):
            results.append((papers[idx], float(score)))

    return results


def get_top_k_papers(papers: List[Paper], top_k: int = 10) -> List[Paper]:
    """
    Simply return top-K papers (already sorted by relevance from arXiv).

    Args:
        papers: List of papers
        top_k: Number to return

    Returns:
        Top K papers
    """
    return papers[:top_k]
