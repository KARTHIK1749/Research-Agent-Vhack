"""
LangGraph orchestration for the multi-agent research workflow.
Defines the graph structure: Literature -> Gap -> Experiment -> Draft
"""
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END

from app.agents import literature_agent, gap_agent, experiment_agent, drafting_agent, meta_agent, related_work_agent, dataset_agent, reviewer_agent


class ResearchGraphState(TypedDict, total=False):
    """Type definition for the graph state."""
    research_goal: str
    papers: list
    literature_summary: str
    gaps: list
    selected_gap: int
    experiment: dict
    draft: dict
    error: str
    meta_optimization: dict
    gap_scores: list
    validations: dict
    related_work: dict
    dataset_recommendation: dict
    review_feedback: dict


def create_research_graph() -> StateGraph:
    """
    Create the LangGraph workflow for research automation.

    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize the graph with our state type
    workflow = StateGraph(ResearchGraphState)

    # Add nodes (agents)
    workflow.add_node("meta_optimizer", meta_agent.run)
    workflow.add_node("literature", literature_agent.run)
    workflow.add_node("related_work", related_work_agent.run)
    workflow.add_node("gap_detection", gap_agent.run)
    workflow.add_node("experiment_design", experiment_agent.run)
    workflow.add_node("dataset_recommend", dataset_agent.run)
    workflow.add_node("drafting", drafting_agent.run)
    workflow.add_node("reviewer", reviewer_agent.run)

    # Define the flow with new agents
    workflow.set_entry_point("meta_optimizer")
    workflow.add_edge("meta_optimizer", "literature")
    workflow.add_edge("literature", "related_work")
    workflow.add_edge("related_work", "gap_detection")
    workflow.add_edge("gap_detection", "experiment_design")
    workflow.add_edge("experiment_design", "dataset_recommend")
    workflow.add_edge("dataset_recommend", "drafting")
    workflow.add_edge("drafting", "reviewer")
    workflow.add_edge("reviewer", END)

    return workflow.compile()


def run_full_workflow(research_goal: str) -> Dict[str, Any]:
    """
    Execute the complete research workflow from start to finish.

    Args:
        research_goal: The research topic/goal

    Returns:
        Final state after all agents have run
    """
    graph = create_research_graph()

    initial_state: ResearchGraphState = {
        "research_goal": research_goal,
        "papers": [],
        "literature_summary": "",
        "gaps": [],
        "selected_gap": None,  # Will be set by meta agent
        "experiment": None,
        "draft": None,
        
        "meta_optimization": None,
        "gap_scores": None,
        "validations": None,
        "related_work": None,
        "dataset_recommendation": None,
        "review_feedback": None,
        "error": None,
    }

    # Execute the graph
    final_state = graph.invoke(initial_state)
    return final_state


def run_step(
    state: Dict[str, Any],
    step: str,
    selected_gap: int = None
) -> Dict[str, Any]:
    """
    Run a single step of the workflow.

    Args:
        state: Current state
        step: Which step to run (literature, gap, experiment, draft)
        selected_gap: User-selected gap index (for experiment step)

    Returns:
        Updated state after the step
    """
    # Update selected_gap if provided
    if selected_gap is not None:
        state["selected_gap"] = selected_gap

    # Route to appropriate agent
    if step == "meta" or step == "meta_optimizer":
        return meta_agent.run(state)
    elif step == "literature":
        return literature_agent.run(state)
    elif step == "gap":
        return gap_agent.run(state)
    elif step == "experiment":
        return experiment_agent.run(state)
    elif step == "draft":
        return drafting_agent.run(state)
    else:
        state["error"] = f"Unknown step: {step}"
        return state


STEP_ORDER = ["meta", "literature", "related_work", "gap", "experiment", "dataset", "draft", "review"]

def get_next_step(current_step: str) -> str:
    """Get the next step in the sequence."""
    try:
        idx = STEP_ORDER.index(current_step)
        if idx + 1 < len(STEP_ORDER):
            return STEP_ORDER[idx + 1]
    except ValueError:
        pass
    return None
