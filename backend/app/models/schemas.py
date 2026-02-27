"""
Pydantic models for request/response schemas.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel , Field
from enum import Enum


class ResearchStep(str, Enum):
    """Steps in the research workflow."""
    META = "meta"
    LITERATURE = "literature" 
    RELATED_WORK = "related_work"
    GAP = "gap"
    EXPERIMENT = "experiment"
    REFLECTION = "reflection"
    DATASET = "dataset"
    DRAFT = "draft"
    REVIEW = "review"
    COMPLETE = "complete"


class Paper(BaseModel):
    """Represents a research paper from arXiv."""
    id: str
    title: str
    authors: List[str]
    summary: str
    published: str
    pdf_url: Optional[str] = None
    primary_category: Optional[str] = None


class Gap(BaseModel):
    """Represents a research gap identified."""
    description: str
    rationale: str
    impact: str


class Experiment(BaseModel):
    """Represents an experiment design."""
    hypothesis: str
    dataset_suggestion: str
    metrics: List[str]
    baseline_methods: List[str]
    proposed_method: str


class Draft(BaseModel):
    """Represents a paper draft."""
    title: str
    abstract: str
    outline: List[str]


class ResearchState(BaseModel):
    """Current state of the research workflow."""
    research_goal: str
    current_step: ResearchStep = ResearchStep.LITERATURE
    papers: List[Paper] = Field(default_factory = list)
    gaps: List[Gap] = Field(default_factory = list)
    selected_gap: Optional[int] = None
    experiment: Optional[Experiment] = None
    draft: Optional[Draft] = None
    error: Optional[str] = None
    # Meta Agent outputs
    meta_optimization: Optional[Dict[str, Any]] = None
    gap_scores: Optional[List[Dict[str, Any]]] = None
    validations: Optional[Dict[str, Any]] = None
    # New agent outputs
    related_work: Optional[Dict[str, Any]] = None
    dataset_recommendation: Optional[Dict[str, Any]] = None
    review_feedback: Optional[Dict[str, Any]] = None


class StartResearchRequest(BaseModel):
    """Request to start a new research session."""
    research_goal: str


class StartResearchResponse(BaseModel):
    """Response after starting research."""
    session_id: str
    state: ResearchState


class StepRequest(BaseModel):
    """Request to execute the next step."""
    session_id: str
    selected_gap: Optional[int] = None  # User selects a gap to pursue


class StepResponse(BaseModel):
    """Response after executing a step."""
    state: ResearchState
    step_completed: ResearchStep
    next_step: Optional[ResearchStep]
    output: Dict[str, Any]


class GetStateRequest(BaseModel):
    """Request to get current state."""
    session_id: str


class GetStateResponse(BaseModel):
    """Response with current state."""
    state: ResearchState
