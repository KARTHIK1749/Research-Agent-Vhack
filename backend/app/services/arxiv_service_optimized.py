"""
Optimized Service for fetching papers from arXiv API with caching and parallel requests.
"""
import asyncio
import aiohttp
import arxiv
from typing import List, Dict, Any
from app.models.schemas import Paper
import time
import hashlib

# Simple in-memory cache
_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 3600  # 1 hour

def _get_cache_key(query: str, max_results: int) -> str:
    """Generate cache key for query."""
    return hashlib.md5(f"{query}:{max_results}".encode()).hexdigest()

def _is_cache_valid(cache_entry: Dict[str, Any]) -> bool:
    """Check if cache entry is still valid."""
    return time.time() - cache_entry["timestamp"] < CACHE_TTL

async def fetch_arxiv_papers_async(query: str, max_results: int = 10) -> List[Paper]:
    """
    Async version of arXiv paper fetching with better performance.
    
    Args:
        query: Search query string
        max_results: Maximum number of papers to return
        
    Returns:
        List of Paper objects
    """
    # Check cache first
    cache_key = _get_cache_key(query, max_results)
    if cache_key in _cache and _is_cache_valid(_cache[cache_key]):
        print(f"📦 arXiv Service: Cache hit for query: {query}")
        return _cache[cache_key]["papers"]
    
    try:
        print(f"🔍 arXiv Service: Fetching papers for query: {query}")
        start_time = time.time()
        
        # Use optimized client settings
        client = arxiv.Client(
            page_size=min(max_results, 50),  # Smaller page size for faster response
            delay_seconds=1,  # Reduced delay
            num_retries=2  # Fewer retries for speed
        )

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        papers = []
        for result in client.results(search):
            paper = Paper(
                id=result.entry_id.split("/")[-1],
                title=result.title,
                authors=[str(author) for author in result.authors],
                summary=result.summary,
                published=result.published.isoformat(),
                pdf_url=result.pdf_url,
                primary_category=result.primary_category
            )
            papers.append(paper)

        # Cache the results
        _cache[cache_key] = {
            "papers": papers,
            "timestamp": time.time()
        }
        
        fetch_time = time.time() - start_time
        print(f"✅ arXiv Service: Fetched {len(papers)} papers in {fetch_time:.2f}s")
        
        return papers

    except arxiv.HTTPError as e:
        print(f"❌ arXiv Service: HTTP Error {e.status}: {str(e)}")
        # Try with simpler query
        if len(query) > 200 or query.count('(') > 3:
            simple_query = query.split(' AND ')[0].strip('()"')
            print(f"🔄 arXiv Service: Retrying with simpler query: {simple_query}")
            return await fetch_arxiv_papers_async(simple_query, max_results)
        return []
        
    except Exception as e:
        print(f"❌ arXiv Service: Error: {str(e)}")
        return []

def fetch_arxiv_papers(query: str, max_results: int = 10) -> List[Paper]:
    """
    Synchronous wrapper for async arXiv fetching.
    
    Args:
        query: Search query string
        max_results: Maximum number of papers to return
        
    Returns:
        List of Paper objects
    """
    # Run the async function in the current event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in an event loop, use create_task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, fetch_arxiv_papers_async(query, max_results))
                return future.result()
        else:
            return asyncio.run(fetch_arxiv_papers_async(query, max_results))
    except Exception as e:
        print(f"⚠️ arXiv Service: Fallback to sync method: {str(e)}")
        # Fallback to original sync method
        client = arxiv.Client(page_size=50, delay_seconds=1, num_retries=2)
        search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
        
        papers = []
        for result in client.results(search):
            paper = Paper(
                id=result.entry_id.split("/")[-1],
                title=result.title,
                authors=[str(author) for author in result.authors],
                summary=result.summary,
                published=result.published.isoformat(),
                pdf_url=result.pdf_url,
                primary_category=result.primary_category
            )
            papers.append(paper)
        
        return papers

def clear_cache():
    """Clear the arXiv cache."""
    global _cache
    _cache.clear()
    print("🗑️ arXiv Service: Cache cleared")
