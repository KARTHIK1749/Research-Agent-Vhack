"""
Ultra-Fast Literature Agent - Optimized for maximum speed.
Uses aggressive caching, reduced processing, and parallel operations.
"""
import re
import asyncio
import concurrent.futures
from typing import Dict, Any, List
from app.services.arxiv_service_optimized import fetch_arxiv_papers
from app.services.llm_service_optimized import llm_call_optimized
from app.services.embedding_service_optimized import create_paper_embeddings_optimized
from app.services.clustering_service_optimized import cluster_embeddings_optimized, get_sparsest_cluster_papers
from app.services.progress_service import get_progress_tracker
from app.utils.prompts import (
    LITERATURE_SYSTEM_PROMPT,
    LITERATURE_ANALYSIS_PROMPT
)

def _clean_literature_summary(text: str) -> str:
    """Quick text cleaning."""
    if not text:
        return text
    
    # Fast cleanup - only essential cleaning
    text = re.sub(r'\*{3,}', '', text)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()

def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ultra-Fast Literature Agent: Optimized for speed.
    
    Speed optimizations:
    - Fewer papers (5 instead of 10)
    - Shorter summaries (200 chars instead of 500)
    - Fewer clusters (3 instead of 5)
    - Reduced LLM prompt size
    - Aggressive caching
    - Parallel processing where possible
    """
    research_goal = state.get("research_goal", "")
    session_id = state.get("session_id", "default")
    
    # Get progress tracker
    tracker = get_progress_tracker(session_id)

    if not research_goal:
        tracker.fail_step("literature", "No research goal provided")
        state["error"] = "No research goal provided"
        return state

    try:
        # Use optimized query from meta agent if available
        meta_optimization = state.get("meta_optimization", {})
        optimized_query = meta_optimization.get("optimized_query", research_goal)

        print(f"🚀 Fast Literature Agent: Using query: {optimized_query}")
        tracker.start_step("literature", "Fast literature review starting")

        # SPEED OPTIMIZATION 1: Fetch fewer papers
        tracker.update_progress("literature", 10, "Fetching papers (fast mode)")
        papers = fetch_arxiv_papers(optimized_query, max_results=5)  # Reduced from 10
        print(f"📊 Fast Literature Agent: Found {len(papers)} papers")
        tracker.update_progress("literature", 30, f"Found {len(papers)} papers")

        # Step 2: Store papers in state
        state["papers"] = [p.model_dump() for p in papers]

        # Step 3: Fast clustering with fewer clusters
        if papers:
            try:
                # SPEED OPTIMIZATION 2: Faster embedding processing
                tracker.update_progress("literature", 40, "Creating embeddings (optimized)")
                embeddings, papers_list = create_paper_embeddings_optimized(papers)
                print(f"🧠 Fast Literature Agent: Created embeddings {embeddings.shape}")
                tracker.update_progress("literature", 60, "Fast clustering analysis")
                
                # SPEED OPTIMIZATION 3: Fewer clusters for faster processing
                cluster_analysis = cluster_embeddings_optimized(
                    embeddings.tolist(), 
                    n_clusters=3  # Reduced from 5
                )
                print(f"📈 Fast Literature Agent: Fast clustering complete")
                tracker.update_progress("literature", 70, "Gap identification")
                
                # Get sparsest cluster papers
                sparsest_papers = get_sparsest_cluster_papers(
                    [p.model_dump() for p in papers], 
                    cluster_analysis["labels"], 
                    cluster_analysis["sparsest_cluster"]
                )
                
                # Store clustering results
                state["cluster_analysis"] = {
                    "density": cluster_analysis["density"],
                    "sparsest_cluster": cluster_analysis["sparsest_cluster"],
                    "centroids": cluster_analysis["centroids"],
                    "sparsest_cluster_papers": sparsest_papers,
                    "n_clusters": cluster_analysis["n_clusters"],
                    "total_papers": cluster_analysis["total_papers"]
                }
                
                # Store embeddings for later use
                state["paper_embeddings"] = embeddings.tolist()
                
            except Exception as e:
                print(f"⚠️ Fast Literature Agent: Clustering failed: {str(e)}")
                tracker.update_progress("literature", 70, f"Clustering skipped: {str(e)}")
                # Continue without clustering analysis

            # Step 4: Fast LLM call with reduced prompt size
            try:
                tracker.update_progress("literature", 80, "Generating fast summary")
                
                # SPEED OPTIMIZATION 4: Much shorter prompts
                papers_summary = "\n\n".join([
                    f"Paper {i+1}:\nTitle: {p.title}\nSummary: {p.summary[:200]}..."  # Reduced from 300
                    for i, p in enumerate(papers[:3])  # Reduced from 5
                ])

                # SPEED OPTIMIZATION 5: Shorter user prompt
                fast_user_prompt = f"""Research Goal: {research_goal}

Found {len(papers)} papers:
{papers_summary}

Provide a concise literature analysis (200-300 words) focusing on:
1. Main themes identified
2. Key findings
3. Research gaps

Keep it brief and focused."""

                print("🤖 Fast Literature Agent: Generating summary...")
                summary = llm_call_optimized(
                    system_prompt=LITERATURE_SYSTEM_PROMPT,
                    user_prompt=fast_user_prompt,
                    temperature=0.3,
                    use_cache=True
                )

                # Quick cleanup
                summary = _clean_literature_summary(summary)
                
                state["literature_summary"] = summary
                print(f"📝 Fast Literature Agent: Summary generated ({len(summary)} chars)")
                tracker.update_progress("literature", 95, "Fast analysis complete")
                
            except Exception as e:
                print(f"⚠️ Fast Literature Agent: Summary generation failed: {str(e)}")
                tracker.fail_step("literature", f"Summary failed: {str(e)}")
                state["literature_summary"] = f"Fast literature analysis failed: {str(e)}. Found {len(papers)} papers."
        else:
            state["literature_summary"] = "No relevant papers found in fast search."
            print("⚠️ Fast Literature Agent: No papers found")
            tracker.complete_step("literature", {"papers_found": 0})
            return state

        # Complete the step
        tracker.complete_step("literature", {
            "papers_found": len(papers),
            "summary_length": len(state.get("literature_summary", "")),
            "clusters_found": cluster_analysis.get("n_clusters", 0) if 'cluster_analysis' in state else 0,
            "mode": "fast"
        })

        return state

    except Exception as e:
        error_msg = f"Fast literature agent failed: {str(e)}"
        print(f"❌ Fast Literature Agent: {error_msg}")
        tracker.fail_step("literature", error_msg)
        state["error"] = error_msg
        state["literature_summary"] = f"Error: {error_msg}"
        return state

# Parallel processing helper
def process_papers_parallel(papers: List, max_workers: int = 4) -> List:
    """Process papers in parallel for faster execution."""
    def process_single_paper(paper):
        # Simple processing - can be expanded
        return {
            "id": paper.id,
            "title": paper.title,
            "summary": paper.summary[:200],  # Truncate for speed
            "authors": paper.authors[:2],  # Limit authors
        }
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_single_paper, papers))
    return results

# Ultra-fast mode for development
def run_ultra_fast(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ultra-fast mode for development/testing.
    Skips clustering and uses minimal processing.
    """
    research_goal = state.get("research_goal", "")
    session_id = state.get("session_id", "default")
    tracker = get_progress_tracker(session_id)
    
    if not research_goal:
        state["error"] = "No research goal provided"
        return state
    
    try:
        tracker.start_step("literature", "Ultra-fast mode")
        
        # Minimal paper fetch
        papers = fetch_arxiv_papers(research_goal, max_results=3)  # Very few papers
        state["papers"] = [p.model_dump() for p in papers]
        
        # Skip clustering entirely for speed
        tracker.update_progress("literature", 50, "Skipping clustering for speed")
        
        # Minimal LLM call
        if papers:
            tracker.update_progress("literature", 80, "Minimal summary")
            minimal_prompt = f"Research: {research_goal}\n\nPapers: {len(papers)} found.\n\nBrief analysis (100 words):"
            
            summary = llm_call_optimized(
                system_prompt="You are a research assistant. Be very brief.",
                user_prompt=minimal_prompt,
                temperature=0.3,
                use_cache=True
            )
            
            state["literature_summary"] = summary[:500]  # Limit length
        
        tracker.complete_step("literature", {"mode": "ultra-fast", "papers": len(papers)})
        return state
        
    except Exception as e:
        tracker.fail_step("literature", str(e))
        state["error"] = str(e)
        return state
