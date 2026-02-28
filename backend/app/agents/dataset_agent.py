"""
Dataset Recommender Agent - Recommends REAL datasets with concrete details.

Instead of vague "use standard benchmark" suggestions, this agent provides:
- Specific dataset names (CIFAR-10, ImageNet, GLUE, etc.)
- Dataset sizes and statistics
- Download links or sources
- Preprocessing requirements
- Suitability assessment for the specific research gap

Agent Contract: Takes graph state, updates ONLY state["dataset_recommendation"], returns updated state.
"""
from typing import Dict, Any, List
from app.services.llm_service import llm_call_structured
from app.utils.prompts import (
    DATASET_SYSTEM_PROMPT,
    DATASET_RECOMMENDATION_PROMPT,
    DATASET_OUTPUT_SCHEMA
)

# Knowledge base of real datasets (for reference and validation)
KNOWN_DATASETS = {
    "image_classification": [
        {"name": "CIFAR-10", "size": "60,000 images", "classes": 10, "url": "https://www.cs.toronto.edu/~kriz/cifar.html"},
        {"name": "CIFAR-100", "size": "60,000 images", "classes": 100, "url": "https://www.cs.toronto.edu/~kriz/cifar.html"},
        {"name": "ImageNet", "size": "1.2M images", "classes": 1000, "url": "https://www.image-net.org/"},
        {"name": "MNIST", "size": "70,000 images", "classes": 10, "url": "http://yann.lecun.com/exdb/mnist/"},
        {"name": "Fashion-MNIST", "size": "70,000 images", "classes": 10, "url": "https://github.com/zalandoresearch/fashion-mnist"},
        {"name": "COCO", "size": "330K images", "classes": 80, "url": "https://cocodataset.org/"},
    ],
    "nlp": [
        {"name": "GLUE", "size": "Various", "tasks": "9 tasks", "url": "https://gluebenchmark.com/"},
        {"name": "SQuAD", "size": "100K+ questions", "type": "QA", "url": "https://rajpurkar.github.io/SQuAD-explorer/"},
        {"name": "IMDB Reviews", "size": "50,000 reviews", "type": "Sentiment", "url": "https://ai.stanford.edu/~amaas/data/sentiment/"},
        {"name": "WikiText-103", "size": "103M tokens", "type": "LM", "url": "https://www.salesforce.com/products/einstein/ai-research/the-wikitext-dependency-language-modeling-dataset/"},
    ],
    "medical": [
        {"name": "ChestX-ray14", "size": "112,000 X-rays", "type": "Classification", "url": "https://nihcc.app.box.com/v/ChestXray-NIHCC"},
        {"name": "ISIC Archive", "size": "70,000 dermoscopy", "type": "Skin lesion", "url": "https://challenge.isic-archive.com/"},
        {"name": "BraTS", "size": "2,000 MRI scans", "type": "Segmentation", "url": "https://www.med.upenn.edu/cbica/brats2020/"},
    ],
    "time_series": [
        {"name": "UCR Archive", "size": "128 datasets", "type": "Classification", "url": "https://www.cs.ucr.edu/~eamonn/time_series_data_2018/"},
        {"name": "ETT", "size": "2 years sensor data", "type": "Forecasting", "url": "https://github.com/zhouhaoyi/ETDataset"},
    ]
}


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dataset Recommender Agent: Suggests concrete datasets for the experiment.

    Args:
        state: Current graph state with "experiment", "gaps", "selected_gap" keys

    Returns:
        Updated state with "dataset_recommendation" key
    """
    experiment = state.get("experiment", {})
    gaps = state.get("gaps", [])
    selected_gap_idx = state.get("selected_gap", 0)
    research_goal = state.get("research_goal", "")

    if not experiment:
        state["error"] = "No experiment design available for dataset recommendation"
        return state

    # Get gap description
    gap_description = ""
    if gaps and selected_gap_idx < len(gaps):
        gap_description = gaps[selected_gap_idx].get("description", "")

    # Get current dataset suggestion from experiment
    current_suggestion = experiment.get("dataset_suggestion", "")

    try:
        # Generate concrete dataset recommendation
        user_prompt = DATASET_RECOMMENDATION_PROMPT.format(
            research_goal=research_goal,
            gap_description=gap_description,
            current_suggestion=current_suggestion,
            proposed_method=experiment.get("proposed_method", "")
        )

        result = llm_call_structured(
            system_prompt=DATASET_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=DATASET_OUTPUT_SCHEMA,
            temperature=0.3
        )

        # Validate and enrich with known URLs if available
        recommendation = _enrich_dataset_info(result)

        state["dataset_recommendation"] = recommendation

    except Exception as e:
        state["error"] = f"Dataset recommendation failed: {str(e)}"
        # Fallback recommendation
        state["dataset_recommendation"] = {
            "primary_dataset": "CIFAR-10",
            "description": "Standard benchmark dataset (fallback)",
            "size": "60,000 images",
            "url": "https://www.cs.toronto.edu/~kriz/cifar.html",
            "preprocessing": "Normalize to [0,1], data augmentation",
            "alternatives": ["MNIST", "ImageNet-subset"],
            "suitability_rationale": "Generic fallback dataset"
        }

    return state


def _enrich_dataset_info(recommendation: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich dataset recommendation with known URLs and validation."""
    primary = recommendation.get("primary_dataset", "")

    # Check if it's in our known datasets
    for category, datasets in KNOWN_DATASETS.items():
        for ds in datasets:
            if ds["name"].lower() in primary.lower() or primary.lower() in ds["name"].lower():
                # Add URL if not present
                if not recommendation.get("url"):
                    recommendation["url"] = ds.get("url", "")
                # Validate size if provided
                if recommendation.get("size") != ds.get("size"):
                    recommendation["size_verified"] = ds.get("size")
                break

    # Ensure all required fields exist
    defaults = {
        "primary_dataset": "Unknown Dataset",
        "description": "No description provided",
        "size": "Unknown",
        "url": "",
        "preprocessing": "Standard preprocessing",
        "alternatives": [],
        "suitability_rationale": "No rationale provided"
    }

    for key, value in defaults.items():
        if not recommendation.get(key):
            recommendation[key] = value

    return recommendation


def get_dataset_by_domain(domain: str) -> List[Dict[str, Any]]:
    """
    Get known datasets for a specific domain.

    Args:
        domain: Domain name (image_classification, nlp, medical, time_series)

    Returns:
        List of dataset dictionaries
    """
    return KNOWN_DATASETS.get(domain, [])


def recommend_datasets_for_experiment(
    research_goal: str,
    gap_description: str,
    proposed_method: str
) -> Dict[str, Any]:
    """
    Standalone function to get dataset recommendations.

    Args:
        research_goal: Research goal
        gap_description: Gap description
        proposed_method: Proposed method

    Returns:
        Dataset recommendation dictionary
    """
    state = {
        "research_goal": research_goal,
        "gaps": [{"description": gap_description}],
        "selected_gap": 0,
        "experiment": {
            "proposed_method": proposed_method,
            "dataset_suggestion": ""
        }
    }

    run(state)
    return state.get("dataset_recommendation", {})
