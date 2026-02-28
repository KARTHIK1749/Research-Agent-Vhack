"""
Reviewer Simulator Agent - Simulates peer review feedback on the paper draft.

Catches issues before submission:
- "Gap not clearly motivated"
- "Methodology vague"
- "Missing ablation study suggestions"
- "Weak experimental validation"
- "Poor writing/clarity issues"

Agent Contract: Takes graph state, updates ONLY state["review_feedback"], returns updated state.
"""
from typing import Dict, Any, List
from app.services.llm_service import llm_call_structured
from app.utils.prompts import (
    REVIEWER_SYSTEM_PROMPT,
    REVIEWER_FEEDBACK_PROMPT,
    REVIEWER_OUTPUT_SCHEMA
)


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reviewer Simulator Agent: Provides peer review feedback on the draft.

    Args:
        state: Current graph state with "draft", "experiment", "gaps", "selected_gap" keys

    Returns:
        Updated state with "review_feedback" key containing simulated reviews
    """
    draft = state.get("draft", {})
    experiment = state.get("experiment", {})
    gaps = state.get("gaps", [])
    selected_gap_idx = state.get("selected_gap", 0)
    research_goal = state.get("research_goal", "")

    if not draft:
        state["error"] = "No draft available for review"
        return state

    # Get selected gap description
    gap_description = ""
    if gaps and selected_gap_idx < len(gaps):
        gap_description = gaps[selected_gap_idx].get("description", "")

    try:
        # Generate reviewer feedback
        user_prompt = REVIEWER_FEEDBACK_PROMPT.format(
            research_goal=research_goal,
            title=draft.get("title", ""),
            abstract=draft.get("abstract", ""),
            outline="\n".join([f"- {s}" for s in draft.get("outline", [])]),
            gap_description=gap_description,
            hypothesis=experiment.get("hypothesis", ""),
            proposed_method=experiment.get("proposed_method", ""),
            metrics=", ".join(experiment.get("metrics", [])),
            baselines=", ".join(experiment.get("baseline_methods", []))
        )

        result = llm_call_structured(
            system_prompt=REVIEWER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=REVIEWER_OUTPUT_SCHEMA,
            temperature=0.4  # Slightly higher for varied reviewer perspectives
        )

        # Calculate overall confidence
        strengths_count = len(result.get("strengths", []))
        weaknesses_count = len(result.get("weaknesses", []))
        critical_issues_count = len(result.get("critical_issues", []))

        # Estimate acceptance likelihood
        if critical_issues_count > 2:
            estimated_decision = "Reject"
        elif critical_issues_count > 0 or weaknesses_count > 3:
            estimated_decision = "Major Revision"
        elif weaknesses_count > 1:
            estimated_decision = "Minor Revision"
        else:
            estimated_decision = "Accept"

        state["review_feedback"] = {
            "overall_assessment": result.get("overall_assessment", ""),
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
            "critical_issues": result.get("critical_issues", []),
            "suggestions_for_improvement": result.get("suggestions_for_improvement", []),
            "questions_for_authors": result.get("questions_for_authors", []),
            "experimental_concerns": result.get("experimental_concerns", []),
            "writing_issues": result.get("writing_issues", []),
            "missing_references_suggestions": result.get("missing_references_suggestions", []),
            "score": result.get("score", 5),
            "confidence": result.get("confidence", "Medium"),
            "estimated_decision": estimated_decision,
            "summary": f"{len(result.get('strengths', []))} strengths, "
                      f"{len(result.get('weaknesses', []))} weaknesses, "
                      f"{critical_issues_count} critical issues. "
                      f"Estimated decision: {estimated_decision}"
        }

    except Exception as e:
        state["error"] = f"Review generation failed: {str(e)}"
        # Fallback review
        state["review_feedback"] = {
            "overall_assessment": "Basic review generated (LLM call failed)",
            "strengths": ["Addresses a relevant research gap"],
            "weaknesses": ["Requires manual review due to processing error"],
            "critical_issues": [],
            "suggestions_for_improvement": ["Consider expanding the methodology section"],
            "questions_for_authors": [],
            "experimental_concerns": [],
            "writing_issues": [],
            "missing_references_suggestions": [],
            "score": 5,
            "confidence": "Low",
            "estimated_decision": "Major Revision",
            "summary": "Fallback review generated"
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
