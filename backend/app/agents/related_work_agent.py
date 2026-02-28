"""
Related Work Writer Agent - Generates a proper "Related Work" section from retrieved papers.

Takes the 10 papers and writes a comparative analysis section with:
- Categorization of approaches
- Comparison of methodologies
- Identification of limitations in existing work
- Smooth transitions to the research gap

Agent Contract: Takes graph state, updates ONLY state["related_work"], returns updated state.
"""
from typing import Dict, Any, List
from app.services.llm_service import llm_call
from app.utils.prompts import (
    RELATED_WORK_SYSTEM_PROMPT,
    RELATED_WORK_PROMPT
)


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Related Work Writer Agent: Generates a comparative "Related Work" section.

    Args:
        state: Current graph state with "papers" and "research_goal" keys

    Returns:
        Updated state with "related_work" key containing written section
    """
    papers = state.get("papers", [])
    research_goal = state.get("research_goal", "")
    literature_summary = state.get("literature_summary", "")

    if not papers:
        state["error"] = "No papers available for related work section"
        return state

    # Format papers for the prompt
    papers_formatted = _format_papers_for_prompt(papers)

    try:
        # Generate related work section
        user_prompt = RELATED_WORK_PROMPT.format(
            research_goal=research_goal,
            papers_formatted=papers_formatted,
            literature_summary=literature_summary
        )

        related_work_text = llm_call(
            system_prompt=RELATED_WORK_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.4,
            max_tokens=2500
        )

        state["related_work"] = {
            "section_text": related_work_text,
            "papers_cited": len(papers),
            "word_count": len(related_work_text.split())
        }

    except Exception as e:
        state["error"] = f"Related work generation failed: {str(e)}"
        # Fallback
        state["related_work"] = {
            "section_text": _generate_fallback_related_work(papers),
            "papers_cited": len(papers),
            "word_count": 0
        }

    return state


def _format_papers_for_prompt(papers: List[Dict[str, Any]]) -> str:
    """Format papers into a structured string for the LLM prompt."""
    formatted = []

    for i, paper in enumerate(papers[:10], 1):
        title = paper.get("title", "Unknown Title")
        authors = paper.get("authors", [])
        summary = paper.get("summary", "No summary available")
        category = paper.get("primary_category", "unknown")

        # Truncate summary for context window
        summary_short = summary[:400] + "..." if len(summary) > 400 else summary

        formatted.append(f"""Paper {i}:
Title: {title}
Authors: {', '.join(authors[:3])}{' et al.' if len(authors) > 3 else ''}
Category: {category}
Summary: {summary_short}
---""")

    return "\n\n".join(formatted)


def _generate_fallback_related_work(papers: List[Dict[str, Any]]) -> str:
    """Generate a basic related work section as fallback."""
    sections = ["## Related Work\n"]

    sections.append("Several approaches have been proposed to address similar problems in the literature. "
                     "We review the most relevant works below.\n")

    for i, paper in enumerate(papers[:5], 1):
        title = paper.get("title", "Unknown")
        authors = paper.get("authors", ["Unknown"])
        sections.append(f"{i}. **{title}** by {', '.join(authors[:2])} proposed an approach to address "
                       f"related challenges in this domain.\n")

    sections.append("\nWhile these works provide valuable insights, there remains a gap in addressing "
                   "the specific challenges targeted by our research.")

    return "\n".join(sections)


# Standalone function for generating related work from papers list
def generate_related_work_section(
    papers: List[Dict[str, Any]],
    research_goal: str,
    literature_summary: str = ""
) -> Dict[str, Any]:
    """
    Standalone function to generate related work section.

    Args:
        papers: List of paper dictionaries
        research_goal: Research goal
        literature_summary: Optional literature summary

    Returns:
        Dict with section_text, papers_cited, word_count
    """
    if not papers:
        return {
            "section_text": "No papers available.",
            "papers_cited": 0,
            "word_count": 0
        }

    state = {
        "papers": papers,
        "research_goal": research_goal,
        "literature_summary": literature_summary,
        "related_work": {}
    }

    run(state)
    return state.get("related_work", {})
