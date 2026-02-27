"""
Reflection Agent - Provides self-reflection and refinement loop for research hypotheses.

Replaces the traditional reviewer with a reflective approach:
- Identifies logical weaknesses and unrealistic assumptions
- Proposes improved hypothesis versions
- Recomputes RIS after refinement
- Enables iterative improvement

Agent Contract: Takes graph state, updates ONLY state["refined_output"], returns updated state.
"""
from typing import Dict, Any, List
import json
from app.services.llm_service import llm_call
from app.services.scoring_service import compute_complete_ris


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reflection Agent: Provides self-reflection and hypothesis refinement.

    Args:
        state: Current graph state with "experiment", "research_scores", "research_goal", "cluster_analysis" keys

    Returns:
        Updated state with "refined_output" key containing refined hypothesis and updated scores
    """
    experiment = state.get("experiment", {})
    research_scores = state.get("research_scores", {})
    research_goal = state.get("research_goal", "")
    cluster_analysis = state.get("cluster_analysis", {})
    gaps = state.get("gaps", [])
    selected_gap_idx = state.get("selected_gap", 0)

    if not experiment:
        state["error"] = "No experiment available for reflection"
        return state

    # Get selected gap description
    gap_description = ""
    if gaps and selected_gap_idx < len(gaps):
        gap_description = gaps[selected_gap_idx].get("description", "")

    hypothesis = experiment.get("hypothesis", "")
    proposed_method = experiment.get("proposed_method", "")
    centroids = cluster_analysis.get("centroids", [])

    if not hypothesis:
        state["error"] = "No hypothesis available for reflection"
        return state

    try:
        # Construct reflection prompt
        system_prompt = """You are a critical research reviewer. Identify logical weaknesses, unrealistic assumptions, missing baselines, ethical risks. Then propose an improved version of the hypothesis."""

        user_prompt = f"""Research Goal: {research_goal}

Gap Addressed: {gap_description}

Current Hypothesis: {hypothesis}

Proposed Method: {proposed_method}

Current Research Scores:
- Novelty: {research_scores.get('novelty', 'N/A')}/10
- Feasibility: {research_scores.get('feasibility', 'N/A')}/10
- Impact: {research_scores.get('impact', 'N/A')}/10
- Risk: {research_scores.get('risk', 'N/A')}/10
- RIS: {research_scores.get('ris', 'N/A')}/10

Critically evaluate this research plan and provide:

1. criticisms: List of logical weaknesses, unrealistic assumptions, missing components
2. refined_hypothesis: Improved hypothesis addressing the criticisms
3. confidence: Overall confidence in the refined approach (0.0-1.0)

Output strictly as JSON:
{{
  "criticisms": [
    "criticism 1",
    "criticism 2"
  ],
  "refined_hypothesis": "improved hypothesis text",
  "confidence": 0.0-1.0
}}"""

        # Generate reflection
        result = llm_call(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3
        )

        # Parse JSON response
        try:
            reflection_data = json.loads(result)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            reflection_data = {
                "criticisms": ["Unable to parse reflection response"],
                "refined_hypothesis": hypothesis,
                "confidence": 0.5
            }

        refined_hypothesis = reflection_data.get("refined_hypothesis", hypothesis)

        # Recompute RIS for refined hypothesis
        if refined_hypothesis and refined_hypothesis != hypothesis and centroids:
            refined_scores = compute_complete_ris(
                hypothesis=refined_hypothesis,
                gap_description=gap_description,
                research_goal=research_goal,
                centroids=centroids
            )
        else:
            # Use original scores if no refinement or computation fails
            refined_scores = research_scores.copy()

        # Store reflection results
        state["refined_output"] = {
            "criticisms": reflection_data.get("criticisms", []),
            "original_hypothesis": hypothesis,
            "refined_hypothesis": refined_hypothesis,
            "original_scores": research_scores,
            "refined_scores": refined_scores,
            "confidence": reflection_data.get("confidence", 0.5),
            "improvement": {
                "ris_change": refined_scores.get("ris", 0) - research_scores.get("ris", 0),
                "novelty_change": refined_scores.get("novelty", 0) - research_scores.get("novelty", 0),
                "feasibility_change": refined_scores.get("feasibility", 0) - research_scores.get("feasibility", 0),
                "impact_change": refined_scores.get("impact", 0) - research_scores.get("impact", 0)
            }
        }

        # Also keep the refined experiment with updated hypothesis
        refined_experiment = experiment.copy()
        refined_experiment["hypothesis"] = refined_hypothesis
        state["refined_experiment"] = refined_experiment

    except Exception as e:
        state["error"] = f"Reflection failed: {str(e)}"
        # Fallback reflection
        state["refined_output"] = {
            "criticisms": ["Reflection process encountered an error"],
            "original_hypothesis": hypothesis,
            "refined_hypothesis": hypothesis,
            "original_scores": research_scores,
            "refined_scores": research_scores,
            "confidence": 0.3,
            "improvement": {
                "ris_change": 0.0,
                "novelty_change": 0.0,
                "feasibility_change": 0.0,
                "impact_change": 0.0
            }
        }

    return state


def simulate_review_for_paper(
    title: str,
    abstract: str,
    outline: List[str],
    research_goal: str,
    gap_description: str,
    experiment: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Standalone function to simulate a review for a paper.

    Args:
        title: Paper title
        abstract: Paper abstract
        outline: Paper outline sections
        research_goal: Research goal
        gap_description: Gap description
        experiment: Experiment details

    Returns:
        Review feedback dictionary
    """
    state = {
        "research_goal": research_goal,
        "gaps": [{"description": gap_description}],
        "selected_gap": 0,
        "draft": {
            "title": title,
            "abstract": abstract,
            "outline": outline
        },
        "experiment": experiment
    }

    run(state)
    return state.get("review_feedback", {})
