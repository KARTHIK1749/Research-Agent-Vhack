"""
Optimized LLM Service with caching, batching, and performance improvements.
"""
import hashlib
import time
import pickle
from typing import Dict, Any
from pathlib import Path
from app.services.gemini_service import call_gemini, call_gemini_with_json_enforcement

# Simple in-memory cache for LLM responses
_llm_cache: Dict[str, Dict[str, Any]] = {}
_cache_dir = Path(__file__).parent.parent.parent / "cache"
_cache_dir.mkdir(exist_ok=True)
CACHE_TTL = 1800  # 30 minutes for LLM cache

def _get_cache_key(system_prompt: str, user_prompt: str, temperature: float) -> str:
    """Generate cache key for LLM request."""
    content = f"{system_prompt}|{user_prompt}|{temperature}"
    return hashlib.md5(content.encode()).hexdigest()

def _is_cache_valid(cache_entry: Dict[str, Any]) -> bool:
    """Check if cache entry is still valid."""
    return time.time() - cache_entry["timestamp"] < CACHE_TTL

def _load_llm_cache():
    """Load LLM cache from disk."""
    cache_file = _cache_dir / "llm_cache.pkl"
    if cache_file.exists():
        try:
            with open(cache_file, 'rb') as f:
                global _llm_cache
                _llm_cache = pickle.load(f)
            print(f"📦 LLM Service: Loaded {len(_llm_cache)} cached responses")
        except Exception as e:
            print(f"⚠️ LLM Service: Failed to load cache: {str(e)}")

def _save_llm_cache():
    """Save LLM cache to disk."""
    cache_file = _cache_dir / "llm_cache.pkl"
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(_llm_cache, f)
        print(f"💾 LLM Service: Saved {len(_llm_cache)} responses to cache")
    except Exception as e:
        print(f"⚠️ LLM Service: Failed to save cache: {str(e)}")

def llm_call_optimized(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 2048,
    use_cache: bool = True
) -> str:
    """
    Optimized LLM call with caching and performance monitoring.
    
    Args:
        system_prompt: System instructions
        user_prompt: User input/question
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        use_cache: Whether to use caching
        
    Returns:
        Generated text response
    """
    # Load cache on first use
    if not _llm_cache and use_cache:
        _load_llm_cache()
    
    # Check cache first
    if use_cache:
        cache_key = _get_cache_key(system_prompt, user_prompt, temperature)
        if cache_key in _llm_cache and _is_cache_valid(_llm_cache[cache_key]):
            print(f"📦 LLM Service: Cache hit for response ({len(_llm_cache[cache_key]['response'])} chars)")
            return _llm_cache[cache_key]["response"]
    
    # Make actual LLM call
    print(f"🤖 LLM Service: Generating response ({len(user_prompt)} chars prompt)...")
    start_time = time.time()
    
    try:
        response = call_gemini(system_prompt, user_prompt, temperature)
        
        generation_time = time.time() - start_time
        print(f"✅ LLM Service: Response generated in {generation_time:.2f}s ({len(response)} chars)")
        
        # Cache the response
        if use_cache and response:
            cache_key = _get_cache_key(system_prompt, user_prompt, temperature)
            _llm_cache[cache_key] = {
                "response": response,
                "timestamp": time.time(),
                "generation_time": generation_time
            }
            # Save cache periodically
            if len(_llm_cache) % 10 == 0:
                _save_llm_cache()
        
        return response
        
    except Exception as e:
        print(f"❌ LLM Service: Error generating response: {str(e)}")
        raise

def llm_call_structured_optimized(
    system_prompt: str,
    user_prompt: str,
    output_schema: Dict[str, Any],
    temperature: float = 0.2,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Optimized structured LLM call with caching.
    
    Args:
        system_prompt: System instructions
        user_prompt: User input
        output_schema: Description of expected output structure
        temperature: Sampling temperature
        use_cache: Whether to use caching
        
    Returns:
        Parsed JSON as dictionary
    """
    # Load cache on first use
    if not _llm_cache and use_cache:
        _load_llm_cache()
    
    # Check cache first
    if use_cache:
        cache_key = _get_cache_key(system_prompt, user_prompt, temperature)
        if cache_key in _llm_cache and _is_cache_valid(_llm_cache[cache_key]):
            print(f"📦 LLM Service: Cache hit for structured response")
            return _llm_cache[cache_key]["response"]
    
    # Make actual LLM call
    print(f"🤖 LLM Service: Generating structured response...")
    start_time = time.time()
    
    try:
        response = call_gemini_with_json_enforcement(system_prompt, user_prompt, temperature)
        
        generation_time = time.time() - start_time
        print(f"✅ LLM Service: Structured response generated in {generation_time:.2f}s")
        
        # Cache the response
        if use_cache and response:
            cache_key = _get_cache_key(system_prompt, user_prompt, temperature)
            _llm_cache[cache_key] = {
                "response": response,
                "timestamp": time.time(),
                "generation_time": generation_time
            }
            # Save cache periodically
            if len(_llm_cache) % 5 == 0:
                _save_llm_cache()
        
        return response
        
    except Exception as e:
        print(f"❌ LLM Service: Error generating structured response: {str(e)}")
        raise

# Backward compatibility wrappers
def llm_call(system_prompt: str, user_prompt: str, temperature: float = 0.3, max_tokens: int = 2048) -> str:
    """Backward compatibility wrapper."""
    return llm_call_optimized(system_prompt, user_prompt, temperature, max_tokens)

def llm_call_structured(system_prompt: str, user_prompt: str, output_schema: Dict[str, Any], temperature: float = 0.2) -> Dict[str, Any]:
    """Backward compatibility wrapper."""
    return llm_call_structured_optimized(system_prompt, user_prompt, output_schema, temperature)

def clear_llm_cache():
    """Clear the LLM cache."""
    global _llm_cache
    _llm_cache.clear()
    cache_file = _cache_dir / "llm_cache.pkl"
    if cache_file.exists():
        cache_file.unlink()
    print("🗑️ LLM Service: Cache cleared")

def get_cache_stats() -> Dict[str, Any]:
    """Get LLM cache statistics."""
    valid_entries = sum(1 for entry in _llm_cache.values() if _is_cache_valid(entry))
    return {
        "total_cached_responses": len(_llm_cache),
        "valid_cached_responses": valid_entries,
        "cache_file_exists": (_cache_dir / "llm_cache.pkl").exists(),
        "cache_file_size_mb": (_cache_dir / "llm_cache.pkl").stat().st_size / (1024*1024) if (_cache_dir / "llm_cache.pkl").exists() else 0
    }

def cleanup_expired_cache():
    """Remove expired entries from cache."""
    global _llm_cache
    original_size = len(_llm_cache)
    _llm_cache = {k: v for k, v in _llm_cache.items() if _is_cache_valid(v)}
    removed = original_size - len(_llm_cache)
    if removed > 0:
        print(f"🧹 LLM Service: Removed {removed} expired cache entries")
        _save_llm_cache()
