"""
Literature Agent - Fetches relevant papers from arXiv and analyzes them.
Agent Contract: Takes graph state, updates ONLY state["papers"], returns updated state.
"""
from typing import Dict, Any, List
from app.services.arxiv_service import fetch_arxiv_papers
from app.services.llm_service import llm_call
from app.services.embedding_service import create_paper_embeddings
from app.services.clustering_service import cluster_embeddings, get_sparsest_cluster_papers
from app.utils.prompts import (
    LITERATURE_SYSTEM_PROMPT,
    LITERATURE_ANALYSIS_PROMPT
)


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Literature Agent: Fetches and analyzes papers from arXiv.

    Args:
        state: Current graph state with "research_goal" key

    Returns:
        Updated state with "papers" and "literature_summary" keys
    """
    research_goal = state.get("research_goal", "")

    if not research_goal:
        state["error"] = "No research goal provided"
        return state

    # Use optimized query from meta agent if available
    meta_optimization = state.get("meta_optimization", {})
    optimized_query = meta_optimization.get("optimized_query", research_goal)

    # Step 1: Fetch papers from arXiv using optimized query
    papers = fetch_arxiv_papers(optimized_query, max_results=10)

    # Step 2: Store papers in state
    state["papers"] = [p.model_dump() for p in papers]

    # Step 3: Create embeddings and perform clustering analysis
    if papers:
        # Create embeddings
        embeddings, papers_list = create_paper_embeddings(papers)
        
        # Perform clustering analysis
        cluster_analysis = cluster_embeddings(embeddings.tolist(), n_clusters=5)
        
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

    # Step 4: Generate literature summary via LLM
    if papers:
        papers_summary = "\n\n".join([
            f"Paper {i+1}:\nTitle: {p.title}\nSummary: {p.summary[:500]}..."
            for i, p in enumerate(papers[:5])  # Summarize top 5 for context window
        ])

        user_prompt = LITERATURE_ANALYSIS_PROMPT.format(
            research_goal=research_goal,
            count=len(papers),
            papers_summary=papers_summary
        )

        summary = llm_call(
            system_prompt=LITERATURE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3
        )

        # Clean up special characters and formatting
        summary = summary.replace("*", "").replace("•", "").replace("-", "")
        # Remove excessive whitespace
        summary = " ".join(summary.split())
        
        state["literature_summary"] = summary
    else:
        state["literature_summary"] = "No relevant papers found."

    return state
