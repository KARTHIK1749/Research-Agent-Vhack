"""
Experiment Design Agent - Converts a gap into a concrete experiment plan.
Agent Contract: Takes graph state, updates ONLY state["experiment"], returns updated state.
"""
from typing import Dict, Any
from app.services.llm_service import llm_call_structured
from app.utils.prompts import (
    EXPERIMENT_SYSTEM_PROMPT,
    EXPERIMENT_DESIGN_PROMPT,
    EXPERIMENT_OUTPUT_SCHEMA
)


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Experiment Design Agent: Creates a concrete experiment plan for a selected gap.

    Args:
        state: Current graph state with "research_goal", "gaps", and "selected_gap" keys

    Returns:
        Updated state with "experiment" key containing experiment design
    """
    research_goal = state.get("research_goal", "")
    gaps = state.get("gaps", [])
    selected_gap_idx = state.get("selected_gap")

    if selected_gap_idx is None or not gaps or selected_gap_idx >= len(gaps):
        state["error"] = "No gap selected for experiment design"
        return state

    selected_gap = gaps[selected_gap_idx]
    gap_description = selected_gap.get("description", "")

    # Generate experiment design using LLM
    user_prompt = EXPERIMENT_DESIGN_PROMPT.format(
        research_goal=research_goal,
        gap_description=gap_description
    )

    try:
        experiment = llm_call_structured(
            system_prompt=EXPERIMENT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=EXPERIMENT_OUTPUT_SCHEMA,
            temperature=0.3
        )

        # Validate experiment structure
        required_keys = ["hypothesis", "dataset_suggestion", "metrics", "baseline_methods", "proposed_method"]
        if all(k in experiment for k in required_keys):
            state["experiment"] = experiment
        else:
            raise ValueError("LLM response missing required experiment fields")

    except Exception as e:
        state["error"] = f"Experiment design failed: {str(e)}"
        # Provide fallback experiment
        state["experiment"] = {
            "hypothesis": f"Addressing the gap in '{gap_description}' will improve performance",
            "dataset_suggestion": "Standard benchmark dataset for this domain",
            "metrics": ["Accuracy", "F1-Score", "Runtime"],
            "baseline_methods": ["Existing Method A", "Existing Method B"],
            "proposed_method": "Novel approach targeting the identified gap"
        }

    return state
