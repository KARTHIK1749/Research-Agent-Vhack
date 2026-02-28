"""
API routes for the research workflow.
"""
import uuid
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import (
    StartResearchRequest,
    StartResearchResponse,
    StepRequest,
    StepResponse,
    GetStateResponse,
    ResearchStep
)
from app.graph.research_graph import run_step, get_next_step, STEP_ORDER

router = APIRouter()

# In-memory session storage (for hackathon/demo purposes)
# In production, use Redis or database
_sessions: Dict[str, Dict[str, Any]] = {}


def _state_to_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """Convert internal state to API response format."""
    return {
        "research_goal": state.get("research_goal", ""),
        "current_step": _get_current_step_from_state(state),
        "papers": state.get("papers", []),
        "gaps": state.get("gaps", []),
        "selected_gap": state.get("selected_gap"),
        "experiment": state.get("experiment"),
        "draft": state.get("draft"),
        "error": state.get("error"),
        # Meta Agent outputs
        "meta_optimization": state.get("meta_optimization"),
        "gap_scores": state.get("gap_scores"),
        "validations": state.get("validations"),
        # New agent outputs
        "related_work": state.get("related_work"),
        "dataset_recommendation": state.get("dataset_recommendation"),
        "review_feedback": state.get("review_feedback")
    }


# def _get_current_step_from_state(state: Dict[str, Any]) -> str:
#     """Determine current step based on state content."""
#     if state.get("review_feedback") and state["review_feedback"].get("score"):
#         return ResearchStep.COMPLETE
#     elif state.get("draft") and state["draft"].get("title"):
#         return "review"
#     elif state.get("dataset_recommendation") and state["dataset_recommendation"].get("primary_dataset"):
#         return ResearchStep.DRAFT
#     elif state.get("experiment") and state["experiment"].get("hypothesis"):
#         return "dataset"
#     elif state.get("gaps") and len(state["gaps"]) > 0:
#         return ResearchStep.EXPERIMENT
#     elif state.get("related_work") and state["related_work"].get("section_text"):
#         return ResearchStep.GAP
#     elif state.get("papers") and len(state["papers"]) > 0:
#         return "related_work"
#     elif state.get("meta_optimization") and state["meta_optimization"].get("optimized_query"):
#         return ResearchStep.LITERATURE
#     return "meta"  # Start with meta agent
def _get_current_step_from_state(state: Dict[str, Any]) -> ResearchStep:
    if state.get("review_feedback"):
        return ResearchStep.COMPLETE

    if state.get("draft"):
        return ResearchStep.DRAFT

    if state.get("experiment"):
        return ResearchStep.EXPERIMENT

    if state.get("gaps"):
        return ResearchStep.GAP

    return ResearchStep.LITERATURE

## sanitize state :
def _sanitize_state(state: Dict[str, Any]) -> Dict[str, Any]:
    for key in [
        "experiment",
        "draft",
        "meta_optimization",
        "gap_scores",
        "validations",
        "related_work",
        "dataset_recommendation",
        "review_feedback"
    ]:
        if state.get(key) == {}:
            state[key] = None
    return state


@router.post("/research/start", response_model=StartResearchResponse)
async def start_research(request: StartResearchRequest):
    """
    Start a new research session.

    Creates a session and runs the literature agent.
    """
    session_id = str(uuid.uuid4())

    # Initialize state with all agent fields
    initial_state = {
        "research_goal": request.research_goal,
        "papers": [],
        "literature_summary": "",
        "gaps": [],
        "selected_gap": None,
        "experiment": None,
        "draft": None,
        "error": None,
        "meta_optimization": None,
        "gap_scores": None,
        "validations": None,
        "related_work": None,
        "dataset_recommendation": None,
        "review_feedback": None
    }

    # Run meta agent first for query optimization
    from app.agents.meta_agent import run as meta_run
    state_after_meta = meta_run(initial_state)

    # Then run literature agent with optimized query
    from app.agents.literature_agent import run as literature_run
    updated_state = literature_run(state_after_meta)

    # Sanitize state before storing
    updated_state = _sanitize_state(updated_state)

    # Store session
    _sessions[session_id] = updated_state

    return StartResearchResponse(
        session_id=session_id,
        state=_state_to_response(updated_state)
    )


@router.post("/research/step", response_model=StepResponse)
async def research_step(request: StepRequest):
    """
    Execute the next step in the research workflow.

    For gap->experiment transition, user should provide selected_gap.
    """
    if request.session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = _sessions[request.session_id]

    # Determine current step
    current_step = _get_current_step_from_state(state)

    if current_step == ResearchStep.COMPLETE:
        return StepResponse(
            state=_state_to_response(state),
            step_completed=ResearchStep.COMPLETE,
            next_step=None,
            output={"message": "Research workflow complete"}
        )

    # Map step names
    step_mapping = {
        "meta": "meta",
        ResearchStep.LITERATURE: "literature",
        "related_work": "related_work",
        ResearchStep.GAP: "gap",
        ResearchStep.EXPERIMENT: "experiment",
        "dataset": "dataset",
        ResearchStep.DRAFT: "draft",
        "review": "review"
    }

    agent_step = step_mapping.get(current_step, current_step)

    # Run the step
    updated_state = run_step(
        state,
        step=agent_step,
        selected_gap=request.selected_gap
    )

    # Store updated state
    _sessions[request.session_id] = updated_state

    # Determine next step
    next_step = get_next_step(agent_step)
    if next_step == "draft":
        next_step = ResearchStep.DRAFT
    elif next_step == "experiment":
        next_step = ResearchStep.EXPERIMENT
    elif next_step == "gap":
        next_step = ResearchStep.GAP
    else:
        next_step = ResearchStep.COMPLETE if updated_state.get("draft") else None

    # Prepare output based on step
    output = {}
    if agent_step == "meta":
        output = {
            "optimized_query": updated_state.get("meta_optimization", {}).get("optimized_query"),
            "query_rationale": updated_state.get("meta_optimization", {}).get("query_rationale")
        }
    elif agent_step == "literature":
        output = {
            "papers_count": len(updated_state.get("papers", [])),
            "literature_summary": updated_state.get("literature_summary", ""),
            "optimized_query": updated_state.get("meta_optimization", {}).get("optimized_query")
        }
    elif agent_step == "related_work":
        output = {
            "related_work": updated_state.get("related_work", {})
        }
    elif agent_step == "gap":
        output = {
            "gaps": updated_state.get("gaps", []),
            "gap_scores": updated_state.get("gap_scores", [])
        }
    elif agent_step == "experiment":
        output = {
            "experiment": updated_state.get("experiment", {}),
            "experiment_validation": updated_state.get("validations", {}).get("experiment")
        }
    elif agent_step == "dataset":
        output = {
            "dataset_recommendation": updated_state.get("dataset_recommendation", {})
        }
    elif agent_step == "draft":
        output = {
            "draft": updated_state.get("draft", {}),
            "draft_validation": updated_state.get("validations", {}).get("draft")
        }
    elif agent_step == "review":
        output = {
            "review_feedback": updated_state.get("review_feedback", {})
        }

    # Map completed step to enum
    completed_enum = {
        "meta": ResearchStep.LITERATURE,
        "literature": ResearchStep.LITERATURE,
        "related_work": ResearchStep.LITERATURE,
        "gap": ResearchStep.GAP,
        "experiment": ResearchStep.EXPERIMENT,
        "dataset": ResearchStep.EXPERIMENT,
        "draft": ResearchStep.DRAFT,
        "review": ResearchStep.COMPLETE
    }.get(agent_step, ResearchStep.LITERATURE)

    return StepResponse(
        state=_state_to_response(updated_state),
        step_completed=completed_enum,
        next_step=next_step,
        output=output
    )


@router.get("/research/state", response_model=GetStateResponse)
async def get_research_state(session_id: str):
    """Get the current state of a research session."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = _sessions[session_id]
    return GetStateResponse(state=_state_to_response(state))
