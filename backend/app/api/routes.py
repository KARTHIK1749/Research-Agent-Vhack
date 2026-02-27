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
    """Determine current step based on state content."""
    if state.get("review_feedback"):
        return ResearchStep.REVIEW

    if state.get("draft"):
        return ResearchStep.DRAFT

    if state.get("dataset_recommendation"):
        return ResearchStep.DATASET

    if state.get("refined_output"):
        return ResearchStep.REFLECTION

    if state.get("experiment"):
        return ResearchStep.EXPERIMENT

    if state.get("gaps"):
        return ResearchStep.GAP

    if state.get("related_work"):
        return ResearchStep.RELATED_WORK

    if state.get("papers"):
        return ResearchStep.LITERATURE

    if state.get("meta_optimization"):
        return ResearchStep.META

    return ResearchStep.META  # Start with meta agent

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
        "session_id": session_id,  # Add session_id for progress tracking
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

    # Initialize progress tracking
    from app.services.progress_service import get_progress_tracker
    tracker = get_progress_tracker(session_id)
    tracker.start_step("meta", "Optimizing search query")

    # Run meta agent first for query optimization
    from app.agents.meta_agent import run as meta_run
    state_after_meta = meta_run(initial_state)
    
    if state_after_meta.get("meta_optimization"):
        tracker.complete_step("meta", state_after_meta["meta_optimization"])
    else:
        tracker.fail_step("meta", "Query optimization failed")

    # Then run literature agent with optimized query
    from app.agents.literature_agent_optimized import run as literature_run
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
        ResearchStep.META: "meta",
        ResearchStep.LITERATURE: "literature",
        ResearchStep.RELATED_WORK: "related_work", 
        ResearchStep.GAP: "gap",
        ResearchStep.EXPERIMENT: "experiment",
        ResearchStep.REFLECTION: "reflection",
        ResearchStep.DATASET: "dataset",
        ResearchStep.DRAFT: "draft",
        ResearchStep.REVIEW: "review"
    }

    agent_step = step_mapping.get(current_step, current_step)

    # Initialize progress tracking for this step
    from app.services.progress_service import get_progress_tracker
    tracker = get_progress_tracker(request.session_id)
    tracker.start_step(agent_step, f"Starting {agent_step} step")

    # Execute the current step
    print(f"🔄 API: Executing step: {agent_step}")
    updated_state = run_step(
        state,
        step=agent_step,
        selected_gap=request.selected_gap
    )
    print(f"✅ API: Step completed: {agent_step}")
    
    # Update progress based on results
    if updated_state.get("error"):
        tracker.fail_step(agent_step, updated_state["error"])
    else:
        # Complete with step-specific details
        step_details = {}
        if agent_step == "literature":
            step_details = {
                "papers_found": len(updated_state.get("papers", [])),
                "summary_length": len(updated_state.get("literature_summary", ""))
            }
        elif agent_step == "gap":
            step_details = {"gaps_found": len(updated_state.get("gaps", []))}
        elif agent_step == "experiment":
            step_details = {"experiment_designed": bool(updated_state.get("experiment"))}
        
        tracker.complete_step(agent_step, step_details)
    
    # Debug: Check what was added to state
    if agent_step == "related_work":
        related_work = updated_state.get("related_work")
        if related_work:
            print(f"📝 API: Related work generated - {len(related_work.get('section_text', ''))} chars")
        else:
            print("❌ API: No related work generated")

    # Store updated state
    _sessions[request.session_id] = updated_state

    # Determine next step
    next_step = get_next_step(agent_step)
    if next_step == "meta":
        next_step = ResearchStep.META
    elif next_step == "literature":
        next_step = ResearchStep.LITERATURE
    elif next_step == "related_work":
        next_step = ResearchStep.RELATED_WORK
    elif next_step == "gap":
        next_step = ResearchStep.GAP
    elif next_step == "experiment":
        next_step = ResearchStep.EXPERIMENT
    elif next_step == "reflection":
        next_step = ResearchStep.REFLECTION
    elif next_step == "dataset":
        next_step = ResearchStep.DATASET
    elif next_step == "draft":
        next_step = ResearchStep.DRAFT
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
        related_work_data = updated_state.get("related_work", {})
        print(f"🔍 API: Related work data keys: {list(related_work_data.keys()) if related_work_data else 'None'}")
        print(f"🔍 API: Related work section length: {len(related_work_data.get('section_text', '')) if related_work_data else 0}")
        
        output = {
            "related_work": related_work_data
        }
        
        # Validate related work data
        if not related_work_data or not related_work_data.get("section_text"):
            print("⚠️ API: Related work data is empty or missing section_text")
            # Provide fallback
            output["related_work"] = {
                "section_text": "Related work section is being generated...",
                "papers_cited": len(updated_state.get("papers", [])),
                "word_count": 0
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
    elif agent_step == "reflection":
        output = {
            "refined_output": updated_state.get("refined_output", {}),
            "research_scores": updated_state.get("experiment", {}).get("research_scores", {})
        }
    elif agent_step == "dataset":
        output = {
            "dataset_recommendation": updated_state.get("dataset_recommendation", {})
        }
    elif agent_step == "draft":
        output = {
            "draft": updated_state.get("draft", {})
        }
    elif agent_step == "review":
        output = {
            "review_feedback": updated_state.get("review_feedback", {})
        }

    # Map completed step to enum
    completed_enum = {
        "meta": ResearchStep.LITERATURE,
        "literature": ResearchStep.RELATED_WORK,
        "related_work": ResearchStep.GAP,
        "gap": ResearchStep.EXPERIMENT,
        "experiment": ResearchStep.REFLECTION,
        "reflection": ResearchStep.DATASET,
        "dataset": ResearchStep.DRAFT,
        "draft": ResearchStep.REVIEW,
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


# Performance monitoring endpoints
@router.get("/performance/stats")
async def get_performance_stats():
    """Get performance statistics."""
    from app.services.performance_service import performance_monitor
    return performance_monitor.get_metrics_summary()

@router.get("/performance/system")
async def get_system_performance():
    """Get current system performance."""
    from app.services.performance_service import get_system_performance
    return get_system_performance()

@router.get("/performance/suggestions")
async def get_optimization_suggestions():
    """Get optimization suggestions."""
    from app.services.performance_service import optimize_suggestions
    return {"suggestions": optimize_suggestions()}


# Progress tracking endpoints
@router.get("/progress/{session_id}")
async def get_progress(session_id: str):
    """Get real-time progress for a research session."""
    from app.services.progress_service import get_progress_tracker
    tracker = get_progress_tracker(session_id)
    return tracker.get_progress_summary()

@router.post("/progress/{session_id}/reset")
async def reset_progress(session_id: str):
    """Reset progress for a session."""
    from app.services.progress_service import remove_progress_tracker
    remove_progress_tracker(session_id)
    return {"message": "Progress reset"}
