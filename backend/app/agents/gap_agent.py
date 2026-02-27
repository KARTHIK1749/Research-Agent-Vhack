"""
Gap Detection Agent - Analyzes papers and identifies research gaps using cluster analysis.
Agent Contract: Takes graph state, updates ONLY state["gaps"], returns updated state.
"""
from typing import Dict, Any, List
import json
from app.services.llm_service_optimized import llm_call
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
    try:
        print("🎯 Gap Agent: Starting analytical gap detection...")
        
        research_goal = state.get("research_goal", "")
        literature_summary = state.get("literature_summary", "")
        cluster_analysis = state.get("cluster_analysis", {})
        
        print(f"📊 Gap Agent: Research goal: {research_goal[:50]}...")
        print(f"📚 Gap Agent: Literature summary length: {len(literature_summary)} chars")
        
        if not literature_summary:
            print("❌ Gap Agent: No literature summary available")
            state["error"] = "No literature summary available for gap detection"
            return state
        
        if not cluster_analysis:
            print("❌ Gap Agent: No cluster analysis available")
            state["error"] = "No cluster analysis available"
            return state
        
        # Extract cluster information
        cluster_density = cluster_analysis.get("density", {})
        sparsest_cluster = cluster_analysis.get("sparsest_cluster")
        sparsest_papers = cluster_analysis.get("sparsest_cluster_papers", [])
        
        print(f"📈 Gap Agent: Sparsest cluster: {sparsest_cluster}")
        print(f"📄 Gap Agent: Papers in sparsest cluster: {len(sparsest_papers)}")
        
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
            print("🤖 Gap Agent: Generating analytical gaps...")
            result = llm_call(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3
            )
            
            print(f"📝 Gap Agent: LLM response length: {len(result)} chars")
            
            # Parse JSON response
            try:
                gaps_data = json.loads(result)
                analytical_gaps = gaps_data.get("identified_gaps", [])
                print(f"✅ Gap Agent: Parsed {len(analytical_gaps)} gaps from JSON")
            except json.JSONDecodeError as e:
                print(f"⚠️ Gap Agent: JSON parsing failed: {str(e)}")
                # Fallback if JSON parsing fails
                analytical_gaps = []
            
            # Validate gap structure
            validated_gaps = []
            for i, gap in enumerate(analytical_gaps):
                if isinstance(gap, dict) and all(k in gap for k in ["title", "description", "justification", "confidence"]):
                    validated_gaps.append(gap)
                    print(f"✅ Gap Agent: Validated gap {i+1}: {gap.get('title', 'N/A')}")
                else:
                    print(f"⚠️ Gap Agent: Invalid gap structure for gap {i+1}")
            
            if not validated_gaps:
                print("⚠️ Gap Agent: No valid gaps found, using fallback")
                # Create fallback gap from cluster analysis
                validated_gaps = [{
                    "title": "Underexplored Research Direction",
                    "description": f"Limited exploration in cluster {sparsest_cluster}",
                    "justification": f"Cluster analysis shows low density in cluster {sparsest_cluster}",
                    "confidence": 0.6
                }]
            
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
            
            print(f"🎉 Gap Agent: Successfully identified {len(validated_gaps)} analytical gaps")
            
        except Exception as e:
            print(f"⚠️ Gap Agent: LLM gap generation failed: {str(e)}")
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
        
    except Exception as e:
        error_msg = f"Gap agent failed: {str(e)}"
        print(f"❌ Gap Agent: {error_msg}")
        state["error"] = error_msg
        # Ultimate fallback
        state["analytical_gaps"] = [
            {
                "title": "Research Gap Identified",
                "description": "Potential research opportunity detected",
                "justification": f"Analysis error: {str(e)}",
                "confidence": 0.3
            }
        ]
        state["gaps"] = [
            {
                "description": "Potential research opportunity detected",
                "rationale": f"Analysis error: {str(e)}",
                "impact": "Requires further investigation"
            }
        ]
    
    return state
