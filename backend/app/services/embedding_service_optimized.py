"""
Optimized Service for creating and managing paper embeddings.
Uses caching, batch processing, and faster models.
"""
import os
import pickle
import hashlib
from typing import List, Tuple, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import time
import threading
from pathlib import Path

from app.models.schemas import Paper

# Global model instance and cache (loaded once)
_model = None
_model_lock = threading.Lock()
_embedding_cache: Dict[str, np.ndarray] = {}
_cache_dir = Path(__file__).parent.parent.parent / "cache"
_cache_dir.mkdir(exist_ok=True)

def _get_cache_key(text: str) -> str:
    """Generate cache key for text."""
    return hashlib.md5(text.encode()).hexdigest()

def _get_model() -> SentenceTransformer:
    """Get or initialize the embedding model with thread safety."""
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                print("🧠 Embedding Service: Loading model...")
                start_time = time.time()
                # Using a faster model for better performance
                _model = SentenceTransformer('all-MiniLM-L6-v2')
                load_time = time.time() - start_time
                print(f"✅ Embedding Service: Model loaded in {load_time:.2f}s")
    return _model

def _load_cache_from_disk():
    """Load embedding cache from disk."""
    cache_file = _cache_dir / "embeddings.pkl"
    if cache_file.exists():
        try:
            with open(cache_file, 'rb') as f:
                global _embedding_cache
                _embedding_cache = pickle.load(f)
            print(f"📦 Embedding Service: Loaded {len(_embedding_cache)} cached embeddings")
        except Exception as e:
            print(f"⚠️ Embedding Service: Failed to load cache: {str(e)}")

def _save_cache_to_disk():
    """Save embedding cache to disk."""
    cache_file = _cache_dir / "embeddings.pkl"
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(_embedding_cache, f)
        print(f"💾 Embedding Service: Saved {len(_embedding_cache)} embeddings to cache")
    except Exception as e:
        print(f"⚠️ Embedding Service: Failed to save cache: {str(e)}")

def create_paper_embeddings_optimized(papers: List[Paper]) -> Tuple[np.ndarray, List[Paper]]:
    """
    Create embeddings for papers with caching and batch processing.
    
    Args:
        papers: List of papers to embed
        
    Returns:
        Tuple of (embeddings array, papers list)
    """
    if not papers:
        return np.array([]), papers
    
    # Load cache on first use
    if not _embedding_cache:
        _load_cache_from_disk()
    
    print(f"🧠 Embedding Service: Processing {len(papers)} papers...")
    start_time = time.time()
    
    model = _get_model()
    
    # Combine title and summary for richer embeddings
    texts = [f"{p.title}. {p.summary}" for p in papers]
    
    # Check cache for existing embeddings
    cached_embeddings = []
    uncached_texts = []
    uncached_indices = []
    
    for i, text in enumerate(texts):
        cache_key = _get_cache_key(text)
        if cache_key in _embedding_cache:
            cached_embeddings.append((i, _embedding_cache[cache_key]))
        else:
            uncached_texts.append(text)
            uncached_indices.append(i)
    
    print(f"📦 Embedding Service: Found {len(cached_embeddings)} cached embeddings")
    print(f"🔄 Embedding Service: Computing {len(uncached_texts)} new embeddings")
    
    # Compute new embeddings in batch
    new_embeddings = []
    if uncached_texts:
        # Use batch processing for better performance
        new_embeddings = model.encode(
            uncached_texts, 
            convert_to_numpy=True, 
            show_progress_bar=False,
            batch_size=8,  # Optimal batch size for most GPUs
            normalize_embeddings=True  # Normalized for better clustering
        )
        
        # Cache new embeddings
        for text, embedding in zip(uncached_texts, new_embeddings):
            cache_key = _get_cache_key(text)
            _embedding_cache[cache_key] = embedding
    
    # Combine cached and new embeddings
    embeddings = np.zeros((len(papers), new_embeddings.shape[1] if new_embeddings else 384))
    
    # Fill in cached embeddings
    for idx, embedding in cached_embeddings:
        embeddings[idx] = embedding
    
    # Fill in new embeddings
    for idx, embedding in zip(uncached_indices, new_embeddings):
        embeddings[idx] = embedding
    
    # Save cache periodically
    if len(uncached_texts) > 0:
        _save_cache_to_disk()
    
    processing_time = time.time() - start_time
    print(f"✅ Embedding Service: Completed in {processing_time:.2f}s")
    
    return embeddings, papers

def create_paper_embeddings(papers: List[Paper]) -> Tuple[np.ndarray, List[Paper]]:
    """
    Backward compatibility wrapper.
    """
    return create_paper_embeddings_optimized(papers)

def search_similar_papers_optimized(
    query: str,
    papers: List[Paper],
    embeddings: np.ndarray,
    top_k: int = 5
) -> List[Tuple[Paper, float]]:
    """
    Optimized similarity search using cached query embeddings.
    
    Args:
        query: Search query
        papers: List of papers to search through
        embeddings: Pre-computed paper embeddings
        top_k: Number of top results to return
        
    Returns:
        List of (paper, similarity_score) tuples
    """
    if not papers or embeddings.size == 0:
        return []
    
    # Load cache if needed
    if not _embedding_cache:
        _load_cache_from_disk()
    
    model = _get_model()
    
    # Check cache for query embedding
    query_cache_key = _get_cache_key(f"query:{query}")
    if query_cache_key in _embedding_cache:
        query_embedding = _embedding_cache[query_cache_key]
    else:
        query_embedding = model.encode([query], convert_to_numpy=True)[0]
        _embedding_cache[query_cache_key] = query_embedding
        _save_cache_to_disk()
    
    # Compute similarities using dot product (faster than cosine for normalized embeddings)
    similarities = np.dot(embeddings, query_embedding)
    
    # Get top-k indices
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        if idx < len(papers):
            results.append((papers[idx], float(similarities[idx])))
    
    return results

def clear_embedding_cache():
    """Clear the embedding cache."""
    global _embedding_cache
    _embedding_cache.clear()
    cache_file = _cache_dir / "embeddings.pkl"
    if cache_file.exists():
        cache_file.unlink()
    print("🗑️ Embedding Service: Cache cleared")

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return {
        "cached_embeddings": len(_embedding_cache),
        "cache_file_exists": (_cache_dir / "embeddings.pkl").exists(),
        "cache_file_size_mb": (_cache_dir / "embeddings.pkl").stat().st_size / (1024*1024) if (_cache_dir / "embeddings.pkl").exists() else 0
    }
