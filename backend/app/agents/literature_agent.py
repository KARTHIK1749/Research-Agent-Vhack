"""
Literature Agent - Fetches relevant papers from arXiv and analyzes them.
Agent Contract: Takes graph state, updates ONLY state["papers"], returns updated state.
"""
from typing import Dict, Any, List
from app.services.arxiv_service import fetch_arxiv_papers
from app.services.llm_service import llm_call
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

    # Step 3: Generate literature summary via LLM
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

        state["literature_summary"] = summary
    else:
        state["literature_summary"] = "No relevant papers found."

    return state
