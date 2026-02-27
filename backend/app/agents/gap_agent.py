"""
Gap Detection Agent - Analyzes papers and identifies research gaps using cluster analysis.
Agent Contract: Takes graph state, updates ONLY state["gaps"], returns updated state.
"""
from typing import Dict, Any, List
import json
from app.services.llm_service import llm_call
from app.utils.prompts import (
    GAP_DETECTION_SYSTEM_PROMPT,
    GAP_DETECTION_PROMPT,
    GAP_OUTPUT_SCHEMA
)


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gap Detection Agent: Identifies research gaps using cluster analysis.
    
    Args:
        state: Current graph state with "research_goal", "literature_summary", and "cluster_analysis" keys
    
    Returns:
        Updated state with "analytical_gaps" key containing cluster-based gap analysis
    """
    research_goal = state.get("research_goal", "")
    literature_summary = state.get("literature_summary", "")
    cluster_analysis = state.get("cluster_analysis", {})
    
    if not literature_summary:
        state["error"] = "No literature summary available for gap detection"
        return state
    
    if not cluster_analysis:
        state["error"] = "No cluster analysis available"
        return state
    
    # Extract cluster information
    cluster_density = cluster_analysis.get("density", {})
    sparsest_cluster = cluster_analysis.get("sparsest_cluster")
    sparsest_papers = cluster_analysis.get("sparsest_cluster_papers", [])
    
    # Create summary of sparsest cluster papers
    sparsest_summary = ""
    if sparsest_papers:
        sparsest_summary = "\n\n".join([
            f"Paper {i+1}:\nTitle: {p.get('title', 'N/A')}\nSummary: {p.get('summary', 'N/A')[:300]}..."
            for i, p in enumerate(sparsest_papers[:3])
        ])
    
    # Construct structured Gemini prompt for analytical gap detection
    system_prompt = """You are a scientific research analyst. You are given structural cluster information about research areas. Identify underexplored regions based on low-density clusters."""
    
    user_prompt = f"""Research Goal: {research_goal}

Cluster Density Map: {json.dumps(cluster_density, indent=2)}

Sparsest Cluster: {sparsest_cluster}

Summary of Papers in Sparsest Cluster:
{sparsest_summary}

Based on this cluster analysis, identify 3-5 research gaps in the sparsest research areas. Focus on underexplored regions that show promise for investigation.

For each gap provide:
- title: Short descriptive title
- description: What is the gap?
- justification: Why is this a gap based on the cluster analysis?
- confidence: Confidence score 0.0-1.0

Output strictly as JSON:
{{
  "identified_gaps": [
    {{
      "title": "...",
      "description": "...", 
      "justification": "...",
      "confidence": 0.0-1.0
    }}
  ]
}}"""
    
    try:
        result = llm_call(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3
        )
        
        # Parse JSON response
        try:
            gaps_data = json.loads(result)
            analytical_gaps = gaps_data.get("identified_gaps", [])
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            analytical_gaps = []
        
        # Validate gap structure
        validated_gaps = []
        for gap in analytical_gaps:
            if isinstance(gap, dict) and all(k in gap for k in ["title", "description", "justification", "confidence"]):
                validated_gaps.append(gap)
        
        state["analytical_gaps"] = validated_gaps
        
        # Also keep traditional gaps for compatibility
        state["gaps"] = [
            {
                "description": gap.get("description", ""),
                "rationale": gap.get("justification", ""),
                "impact": f"Cluster-based gap with confidence {gap.get('confidence', 0.0)}"
            }
            for gap in validated_gaps
        ]
        
    except Exception as e:
        state["error"] = f"Analytical gap detection failed: {str(e)}"
        # Provide fallback gaps
        state["analytical_gaps"] = [
            {
                "title": "Underexplored Research Direction",
                "description": "Limited exploration in sparsest research cluster",
                "justification": "Cluster analysis shows low density in this area",
                "confidence": 0.5
            }
        ]
        state["gaps"] = [
            {
                "description": "Limited exploration in sparsest research cluster",
                "rationale": "Cluster analysis shows low density in this area",
                "impact": "Could enable new research directions"
            }
        ]
    
    return state
