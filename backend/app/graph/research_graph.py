"""
LangGraph orchestration for MARIS v2 multi-agent research workflow.
Updated workflow: Literature -> Gap -> Experiment -> Reflection -> Final Output
Includes Analytical Gap Engine, RIS scoring, and self-reflection loop.
"""
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END

from app.agents import literature_agent_optimized as literature_agent, gap_agent, experiment_agent, drafting_agent, meta_agent, related_work_agent, dataset_agent, reviewer_agent


class ResearchGraphState(TypedDict, total=False):
    """Type definition for the MARIS v2 graph state."""
    research_goal: str
    papers: list
    literature_summary: str
    gaps: list
    analytical_gaps: list  # New v2 cluster-based gaps
    selected_gap: int
    experiment: dict
    research_scores: dict  # New v2 RIS scores
    refined_output: dict   # New v2 reflection results
    refined_experiment: dict  # New v2 refined experiment
    draft: dict
    error: str
    meta_optimization: dict
    gap_scores: list
    validations: dict
    related_work: dict
    dataset_recommendation: dict
    review_feedback: dict
    cluster_analysis: dict  # New v2 clustering results
    paper_embeddings: list  # New v2 paper embeddings


def create_research_graph() -> StateGraph:
    """
    Create the MARIS v2 LangGraph workflow with reflection loop.

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
    workflow.add_node("reflection", reviewer_agent.run)  # Now Reflection Agent
    workflow.add_node("dataset_recommend", dataset_agent.run)
    workflow.add_node("drafting", drafting_agent.run)

    # Define MARIS v2 flow with reflection loop
    workflow.set_entry_point("meta_optimizer")
    workflow.add_edge("meta_optimizer", "literature")
    workflow.add_edge("literature", "related_work")
    workflow.add_edge("related_work", "gap_detection")
    workflow.add_edge("gap_detection", "experiment_design")
    workflow.add_edge("experiment_design", "reflection")  # New reflection step
    workflow.add_edge("reflection", "dataset_recommend")
    workflow.add_edge("dataset_recommend", "drafting")
    workflow.add_edge("drafting", END)

    return workflow.compile()


def run_full_workflow(research_goal: str) -> Dict[str, Any]:
    """
    Execute the complete MARIS v2 research workflow with reflection.

    Args:
        research_goal: The research topic/goal

    Returns:
        Final state with v2 features including RIS scores and refined output
    """
    graph = create_research_graph()

    initial_state: ResearchGraphState = {
        "research_goal": research_goal,
        "papers": [],
        "literature_summary": "",
        "gaps": [],
        "analytical_gaps": [],  # v2 cluster-based gaps
        "selected_gap": None,  # Will be set by meta agent
        "experiment": None,
        "research_scores": {},  # v2 RIS scores
        "refined_output": {},   # v2 reflection results
        "refined_experiment": {},  # v2 refined experiment
        "draft": None,
        
        "meta_optimization": None,
        "gap_scores": None,
        "validations": None,
        "related_work": None,
        "dataset_recommendation": None,
        "review_feedback": None,
        "cluster_analysis": {},  # v2 clustering results
        "paper_embeddings": [],  # v2 paper embeddings
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
    Run a single step of the MARIS v2 workflow.

    Args:
        state: Current state
        step: Which step to run (meta, literature, gap, experiment, reflection, draft)
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
    elif step == "reflection":  # New v2 step
        return reviewer_agent.run(state)
    elif step == "draft":
        return drafting_agent.run(state)
    else:
        state["error"] = f"Unknown step: {step}"
        return state


# Updated step order for MARIS v2
STEP_ORDER = ["meta", "literature", "related_work", "gap", "experiment", "reflection", "dataset", "draft"]

def get_next_step(current_step: str) -> str:
    """Get the next step in the sequence."""
    try:
        idx = STEP_ORDER.index(current_step)
        if idx + 1 < len(STEP_ORDER):
            return STEP_ORDER[idx + 1]
    except ValueError:
        pass
    return None
