"""
Paper Drafting Agent - Generates title, abstract, and outline.
Agent Contract: Takes graph state, updates ONLY state["draft"], returns updated state.
"""
from typing import Dict, Any
from app.services.llm_service import llm_call_structured
from app.utils.prompts import (
    DRAFTING_SYSTEM_PROMPT,
    DRAFTING_PROMPT,
    DRAFT_OUTPUT_SCHEMA
)


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Paper Drafting Agent: Generates a paper draft based on experiment design.

    Args:
        state: Current graph state with "research_goal", "gaps", "selected_gap", and "experiment" keys

    Returns:
        Updated state with "draft" key containing paper draft
    """
    research_goal = state.get("research_goal", "")
    gaps = state.get("gaps", [])
    selected_gap_idx = state.get("selected_gap", 0)
    experiment = state.get("experiment", {})

    if not experiment:
        state["error"] = "No experiment design available for paper drafting"
        return state

    # Get selected gap description
    gap_description = ""
    if gaps and selected_gap_idx < len(gaps):
        gap_description = gaps[selected_gap_idx].get("description", "")

    # Generate draft using LLM
    user_prompt = DRAFTING_PROMPT.format(
        research_goal=research_goal,
        gap_description=gap_description,
        hypothesis=experiment.get("hypothesis", ""),
        dataset=experiment.get("dataset_suggestion", ""),
        metrics=", ".join(experiment.get("metrics", [])),
        proposed_method=experiment.get("proposed_method", "")
    )

    try:
        draft = llm_call_structured(
            system_prompt=DRAFTING_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=DRAFT_OUTPUT_SCHEMA,
            temperature=0.4
        )

        # Validate draft structure
        required_keys = ["title", "abstract", "outline"]
        if all(k in draft for k in required_keys):
            state["draft"] = draft
        else:
            raise ValueError("LLM response missing required draft fields")

    except Exception as e:
        state["error"] = f"Paper drafting failed: {str(e)}"
        # Provide fallback draft
        state["draft"] = {
            "title": f"Addressing Research Gaps in {research_goal[:50]}...",
            "abstract": f"This paper addresses the gap in {gap_description}. We propose a novel approach and evaluate it on standard benchmarks. Our method shows promising results compared to existing baselines.",
            "outline": [
                "Introduction: Motivation and problem statement",
                "Related Work: Survey of existing approaches",
                "Method: Detailed description of our proposed approach",
                "Experiments: Evaluation setup and results",
                "Conclusion: Summary and future work"
            ]
        }

    return state
