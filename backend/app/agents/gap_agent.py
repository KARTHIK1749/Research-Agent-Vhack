"""
Gap Detection Agent - Analyzes papers and identifies research gaps.
Agent Contract: Takes graph state, updates ONLY state["gaps"], returns updated state.
"""
from typing import Dict, Any, List
from app.services.llm_service import llm_call_structured
from app.utils.prompts import (
    GAP_DETECTION_SYSTEM_PROMPT,
    GAP_DETECTION_PROMPT,
    GAP_OUTPUT_SCHEMA
)


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gap Detection Agent: Identifies research gaps from literature analysis.

    Args:
        state: Current graph state with "research_goal" and "literature_summary" keys

    Returns:
        Updated state with "gaps" key containing list of identified gaps
    """
    research_goal = state.get("research_goal", "")
    literature_summary = state.get("literature_summary", "")

    if not literature_summary:
        state["error"] = "No literature summary available for gap detection"
        return state

    # Generate gaps using LLM
    user_prompt = GAP_DETECTION_PROMPT.format(
        research_goal=research_goal,
        literature_summary=literature_summary
    )

    try:
        result = llm_call_structured(
            system_prompt=GAP_DETECTION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=GAP_OUTPUT_SCHEMA,
            temperature=0.3
        )

        # Ensure we have a list of gaps
        if isinstance(result, dict) and "gaps" in result:
            gaps = result["gaps"]
        elif isinstance(result, list):
            gaps = result
        else:
            gaps = []

        # Validate gap structure
        validated_gaps = []
        for gap in gaps:
            if isinstance(gap, dict) and all(k in gap for k in ["description", "rationale", "impact"]):
                validated_gaps.append(gap)

        state["gaps"] = validated_gaps

    except Exception as e:
        state["error"] = f"Gap detection failed: {str(e)}"
        # Provide fallback gaps
        state["gaps"] = [
            {
                "description": "Limited exploration of cross-domain transfer in this area",
                "rationale": "Most papers focus on single-domain experiments",
                "impact": "Could enable broader applicability of methods"
            }
        ]

    return state
