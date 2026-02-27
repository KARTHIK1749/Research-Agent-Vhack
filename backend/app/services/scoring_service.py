"""
Research Intelligence Score (RIS) Service - MARIS v2
Computes novelty, feasibility, impact scores and overall RIS.
"""
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import json
from app.services.llm_service import llm_call

# Global model instance (loaded once)
_embedding_model = None

def _get_embedding_model() -> SentenceTransformer:
    """Get or initialize the embedding model."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model


def compute_novelty_score(hypothesis_embedding: List[float], centroids: List[List[float]]) -> float:
    """
    Compute novelty score as maximum Euclidean distance from any cluster centroid.
    
    Args:
        hypothesis_embedding: Embedding vector for the hypothesis
        centroids: List of cluster centroid vectors
    
    Returns:
        Novelty score (0-10 scale, higher is more novel)
    """
    if not centroids:
        return 5.0  # Default score if no centroids
    
    hypothesis_vec = np.array(hypothesis_embedding)
    centroid_matrix = np.array(centroids)
    
    # Compute Euclidean distances to all centroids
    distances = np.linalg.norm(centroid_matrix - hypothesis_vec, axis=1)
    max_distance = np.max(distances)
    
    # Normalize to 0-10 scale (assuming typical distance ranges)
    # This is a heuristic normalization - may need tuning based on actual distances
    normalized_score = min(max_distance * 2.0, 10.0)  # Scale and cap at 10
    
    return float(normalized_score)


def compute_ris(novelty: float, feasibility: float, impact: float) -> float:
    """
    Compute Research Intelligence Score (RIS) using weighted formula.
    
    Args:
        novelty: Novelty score (0-10)
        feasibility: Feasibility score (0-10)
        impact: Impact score (0-10)
    
    Returns:
        RIS score (0-10)
    """
    # Normalize novelty to 0-10 scale (should already be normalized)
    novelty_normalized = max(0, min(novelty, 10))
    
    # Apply weighted formula: RIS = 0.4 * novelty + 0.3 * feasibility + 0.3 * impact
    ris = 0.4 * novelty_normalized + 0.3 * feasibility + 0.3 * impact
    
    return float(ris)


def generate_hypothesis_embedding(hypothesis: str) -> List[float]:
    """
    Generate embedding for a hypothesis text.
    
    Args:
        hypothesis: Hypothesis text string
    
    Returns:
        Embedding vector as list of floats
    """
    model = _get_embedding_model()
    embedding = model.encode([hypothesis], convert_to_numpy=True)
    return embedding[0].tolist()


def evaluate_research_metrics(hypothesis: str, gap_description: str, research_goal: str) -> Dict[str, float]:
    """
    Use Gemini to evaluate feasibility, impact, and risk of a research hypothesis.
    
    Args:
        hypothesis: The research hypothesis
        gap_description: Description of the research gap
        research_goal: Overall research goal
    
    Returns:
        Dictionary with scores (0-10 scale)
    """
    system_prompt = """You are a research evaluation expert. Score research hypotheses on feasibility, impact, and risk."""
    
    user_prompt = f"""Research Goal: {research_goal}

Research Gap: {gap_description}

Proposed Hypothesis: {hypothesis}

Evaluate this hypothesis on the following metrics (0-10 scale):

Feasibility: How realistic is this to implement? Consider technical complexity, resource requirements, timeline.
Impact: How significant would the results be if successful? Consider contribution to field, practical applications.
Risk: What is the probability of failure? Consider technical challenges, dependencies, uncertainty.

Output strictly as JSON:
{{
  "feasibility": 0-10,
  "impact": 0-10,
  "risk": 0-10
}}"""
    
    try:
        result = llm_call(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2
        )
        
        # Parse JSON response
        scores_data = json.loads(result)
        
        return {
            "feasibility": float(scores_data.get("feasibility", 5.0)),
            "impact": float(scores_data.get("impact", 5.0)),
            "risk": float(scores_data.get("risk", 5.0))
        }
        
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # Fallback scores
        return {
            "feasibility": 5.0,
            "impact": 5.0,
            "risk": 5.0
        }


def compute_complete_ris(
    hypothesis: str,
    gap_description: str,
    research_goal: str,
    centroids: List[List[float]]
) -> Dict[str, float]:
    """
    Compute complete RIS analysis including all components.
    
    Args:
        hypothesis: Research hypothesis text
        gap_description: Description of the research gap
        research_goal: Overall research goal
        centroids: List of cluster centroids from literature analysis
    
    Returns:
        Complete RIS analysis dictionary
    """
    # Step 1: Generate hypothesis embedding
    hypothesis_embedding = generate_hypothesis_embedding(hypothesis)
    
    # Step 2: Compute novelty score
    novelty = compute_novelty_score(hypothesis_embedding, centroids)
    
    # Step 3: Get human-like evaluation scores
    metrics = evaluate_research_metrics(hypothesis, gap_description, research_goal)
    
    # Step 4: Compute overall RIS
    ris = compute_ris(novelty, metrics["feasibility"], metrics["impact"])
    
    return {
        "novelty": novelty,
        "feasibility": metrics["feasibility"],
        "impact": metrics["impact"],
        "risk": metrics["risk"],
        "ris": ris
    }
