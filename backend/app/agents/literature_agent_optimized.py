"""
Optimized Literature Agent - Fetches relevant papers from arXiv and analyzes them.
Uses optimized services for better performance.
"""
import re
from typing import Dict, Any, List
from app.services.arxiv_service_optimized import fetch_arxiv_papers
from app.services.llm_service_optimized import llm_call_optimized
from app.services.embedding_service_optimized import create_paper_embeddings_optimized
from app.services.clustering_service_optimized import cluster_embeddings_optimized, get_sparsest_cluster_papers
from app.services.performance_service import monitor_performance, performance_monitor
from app.utils.prompts import (
    LITERATURE_SYSTEM_PROMPT,
    LITERATURE_ANALYSIS_PROMPT
)


def _clean_literature_summary(text: str) -> str:
    """
    Clean literature summary while preserving structure and readability.
    
    Args:
        text: Raw literature summary text
        
    Returns:
        Cleaned, well-formatted text
    """
    if not text:
        return text
    
    # Remove excessive stars but keep some formatting
    text = re.sub(r'\*{3,}', '', text)  # Remove 3+ consecutive stars
    text = re.sub(r'\*{2}', '', text)   # Remove double stars
    
    # Clean up excessive whitespace while preserving paragraph breaks
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Multiple blank lines to double
    text = re.sub(r'[ \t]+', ' ', text)           # Multiple spaces/tabs to single
    
    # Ensure proper spacing around headings
    text = re.sub(r'([A-Z][A-Z\s]+:)', r'\n\1', text)  # Add newline before all-caps headings
    
    # Clean bullet points but keep structure
    text = re.sub(r'•\s*', '• ', text)      # Normalize bullet points
    text = re.sub(r'-\s*', '- ', text)      # Normalize dashes
    
    # Remove excessive punctuation
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    
    # Clean up line endings
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line:  # Only keep non-empty lines
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


@monitor_performance("literature_agent_run")
def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimized Literature Agent: Fetches and analyzes papers from arXiv.

    Args:
        state: Current graph state with "research_goal" key

    Returns:
        Updated state with "papers" and "literature_summary" keys
    """
    research_goal = state.get("research_goal", "")

    if not research_goal:
        state["error"] = "No research goal provided"
        return state

    try:
        # Use optimized query from meta agent if available
        meta_optimization = state.get("meta_optimization", {})
        optimized_query = meta_optimization.get("optimized_query", research_goal)

        print(f"🔍 Literature Agent: Using query: {optimized_query}")

        # Step 1: Fetch papers from arXiv using optimized service
        papers_op_id = performance_monitor.start_operation("fetch_papers")
        try:
            papers = fetch_arxiv_papers(optimized_query, max_results=10)
            performance_monitor.end_operation(papers_op_id, "fetch_papers", success=True)
        except Exception as e:
            performance_monitor.end_operation(papers_op_id, "fetch_papers", success=False, error_message=str(e))
            raise

        print(f"📊 Literature Agent: Found {len(papers)} papers")

        # Step 2: Store papers in state
        state["papers"] = [p.model_dump() for p in papers]

        # Step 3: Create embeddings and perform clustering analysis (if papers exist)
        if papers:
            try:
                # Create embeddings using optimized service
                embeddings_op_id = performance_monitor.start_operation("create_embeddings")
                try:
                    embeddings, papers_list = create_paper_embeddings_optimized(papers)
                    performance_monitor.end_operation(embeddings_op_id, "create_embeddings", success=True)
                except Exception as e:
                    performance_monitor.end_operation(embeddings_op_id, "create_embeddings", success=False, error_message=str(e))
                    raise
                
                print(f"🧠 Literature Agent: Created embeddings with shape {embeddings.shape}")
                
                # Perform clustering analysis using optimized service
                clustering_op_id = performance_monitor.start_operation("clustering_analysis")
                try:
                    cluster_analysis = cluster_embeddings_optimized(embeddings.tolist(), n_clusters=5)
                    performance_monitor.end_operation(clustering_op_id, "clustering_analysis", success=True)
                except Exception as e:
                    performance_monitor.end_operation(clustering_op_id, "clustering_analysis", success=False, error_message=str(e))
                    raise
                
                print(f"📈 Literature Agent: Cluster analysis complete")
                
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
                print(f"⚠️ Literature Agent: Clustering failed: {str(e)}")
                # Continue without clustering analysis

            # Step 4: Generate literature summary via optimized LLM service
            try:
                # Use only top 5 papers for LLM to reduce token usage and improve speed
                papers_summary = "\n\n".join([
                    f"Paper {i+1}:\nTitle: {p.title}\nSummary: {p.summary[:300]}..."  # Reduced summary length
                    for i, p in enumerate(papers[:5])
                ])

                user_prompt = LITERATURE_ANALYSIS_PROMPT.format(
                    research_goal=research_goal,
                    count=len(papers),
                    papers_summary=papers_summary
                )

                summary_op_id = performance_monitor.start_operation("generate_summary")
                try:
                    summary = llm_call_optimized(
                        system_prompt=LITERATURE_SYSTEM_PROMPT,
                        user_prompt=user_prompt,
                        temperature=0.3,
                        use_cache=True
                    )
                    performance_monitor.end_operation(summary_op_id, "generate_summary", success=True)
                except Exception as e:
                    performance_monitor.end_operation(summary_op_id, "generate_summary", success=False, error_message=str(e))
                    raise

                # Clean up excessive formatting but preserve structure
                summary = _clean_literature_summary(summary)
                
                state["literature_summary"] = summary
                print(f"📝 Literature Agent: Summary generated ({len(summary)} chars)")
                
            except Exception as e:
                print(f"⚠️ Literature Agent: Summary generation failed: {str(e)}")
                state["literature_summary"] = f"Literature analysis failed: {str(e)}. Found {len(papers)} papers."
        else:
            state["literature_summary"] = "No relevant papers found."
            print("⚠️ Literature Agent: No papers found")

        return state

    except Exception as e:
        error_msg = f"Literature agent failed: {str(e)}"
        print(f"❌ Literature Agent: {error_msg}")
        state["error"] = error_msg
        state["literature_summary"] = f"Error: {error_msg}"
        return state

def get_performance_stats() -> Dict[str, Any]:
    """Get performance statistics for the literature agent."""
    return performance_monitor.get_metrics_summary()
