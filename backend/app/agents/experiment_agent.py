"""
Experiment Design Agent - Converts a gap into a concrete experiment plan with RIS scoring.
Agent Contract: Takes graph state, updates ONLY state["experiment"], returns updated state.
"""
from typing import Dict, Any
from app.services.llm_service import llm_call
from app.services.scoring_service import compute_complete_ris
from app.utils.prompts import (
    EXPERIMENT_SYSTEM_PROMPT,
    EXPERIMENT_DESIGN_PROMPT,
    EXPERIMENT_OUTPUT_SCHEMA
)


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Experiment Design Agent: Creates a concrete experiment plan and computes RIS scores.

    Args:
        state: Current graph state with "research_goal", "gaps", "selected_gap", and "cluster_analysis" keys

    Returns:
        Updated state with "experiment" and "research_scores" keys
    """
    research_goal = state.get("research_goal", "")
    gaps = state.get("gaps", [])
    selected_gap_idx = state.get("selected_gap")
    cluster_analysis = state.get("cluster_analysis", {})

    if selected_gap_idx is None or not gaps or selected_gap_idx >= len(gaps):
        state["error"] = "No gap selected for experiment design"
        return state

    selected_gap = gaps[selected_gap_idx]
    gap_description = selected_gap.get("description", "")
    centroids = cluster_analysis.get("centroids", [])

    # Generate experiment design using LLM
    user_prompt = EXPERIMENT_DESIGN_PROMPT.format(
        research_goal=research_goal,
        gap_description=gap_description
    )

    try:
        experiment_result = llm_call(
            system_prompt=EXPERIMENT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3
        )

        # Parse JSON response
        import json
        try:
            experiment = json.loads(experiment_result)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            experiment = {}

        # Validate experiment structure
        required_keys = ["hypothesis", "dataset_suggestion", "metrics", "baseline_methods", "proposed_method"]
        if not all(k in experiment for k in required_keys):
            # Add missing fields with defaults
            for key in required_keys:
                if key not in experiment:
                    experiment[key] = f"Default {key} for addressing: {gap_description}"

        hypothesis = experiment.get("hypothesis", "")

        # Compute RIS scores if we have a hypothesis and centroids
        if hypothesis and centroids:
            research_scores = compute_complete_ris(
                hypothesis=hypothesis,
                gap_description=gap_description,
                research_goal=research_goal,
                centroids=centroids
            )
            state["research_scores"] = research_scores
        else:
            # Default scores if computation fails
            state["research_scores"] = {
                "novelty": 5.0,
                "feasibility": 5.0,
                "impact": 5.0,
                "risk": 5.0,
                "ris": 5.0
            }

        state["experiment"] = experiment

    except Exception as e:
        state["error"] = f"Experiment design failed: {str(e)}"
        # Provide fallback experiment
        fallback_experiment = {
            "hypothesis": f"Addressing the gap in '{gap_description}' will improve performance",
            "dataset_suggestion": "Standard benchmark dataset for this domain",
            "metrics": ["Accuracy", "F1-Score", "Runtime"],
            "baseline_methods": ["Existing Method A", "Existing Method B"],
            "proposed_method": "Novel approach targeting the identified gap"
        }
        state["experiment"] = fallback_experiment
        
        # Default scores for fallback
        state["research_scores"] = {
            "novelty": 5.0,
            "feasibility": 5.0,
            "impact": 5.0,
            "risk": 5.0,
            "ris": 5.0
        }

    return state
