"""
Experiment Design Agent - Converts a gap into a concrete experiment plan with RIS scoring.
Agent Contract: Takes graph state, updates ONLY state["experiment"], returns updated state.
"""
from typing import Dict, Any
from app.services.llm_service_optimized import llm_call
from app.services.scoring_service import compute_complete_ris
from app.utils.prompts import (
    EXPERIMENT_SYSTEM_PROMPT,
    EXPERIMENT_DESIGN_PROMPT,
    EXPERIMENT_OUTPUT_SCHEMA
)


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Experiment Design Agent: Creates a concrete experiment plan and computes RIS scores.

    Args:
        state: Current graph state with "research_goal", "gaps", "selected_gap", and "cluster_analysis" keys

    Returns:
        Updated state with "experiment" and "research_scores" keys
    """
    try:
        print("🧪 Experiment Agent: Starting experiment design...")
        
        research_goal = state.get("research_goal", "")
        gaps = state.get("gaps", [])
        selected_gap_idx = state.get("selected_gap")
        cluster_analysis = state.get("cluster_analysis", {})

        print(f"📊 Experiment Agent: Research goal: {research_goal[:50]}...")
        print(f"🎯 Experiment Agent: Available gaps: {len(gaps)}")
        print(f"📍 Experiment Agent: Selected gap index: {selected_gap_idx}")

        if selected_gap_idx is None or not gaps or selected_gap_idx >= len(gaps):
            print("❌ Experiment Agent: No valid gap selected")
            state["error"] = "No gap selected for experiment design"
            return state

        selected_gap = gaps[selected_gap_idx]
        gap_description = selected_gap.get("description", "")
        centroids = cluster_analysis.get("centroids", [])
        
        print(f"🎯 Experiment Agent: Gap: {gap_description[:50]}...")
        print(f"📈 Experiment Agent: Available centroids: {len(centroids)}")

        # Generate experiment design using LLM
        user_prompt = EXPERIMENT_DESIGN_PROMPT.format(
            research_goal=research_goal,
            gap_description=gap_description
        )

        try:
            print("🤖 Experiment Agent: Generating experiment design...")
            experiment_result = llm_call(
                system_prompt=EXPERIMENT_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.3
            )

            print(f"📝 Experiment Agent: LLM response length: {len(experiment_result)} chars")

            # Parse JSON response
            import json
            try:
                experiment = json.loads(experiment_result)
                print("✅ Experiment Agent: Successfully parsed JSON experiment design")
            except json.JSONDecodeError as e:
                print(f"⚠️ Experiment Agent: JSON parsing failed: {str(e)}")
                # Fallback if JSON parsing fails
                experiment = {}

            # Validate experiment structure
            required_keys = ["hypothesis", "dataset_suggestion", "metrics", "baseline_methods", "proposed_method"]
            missing_keys = []
            for key in required_keys:
                if key not in experiment:
                    missing_keys.append(key)
                    experiment[key] = f"Default {key} for addressing: {gap_description}"
            
            if missing_keys:
                print(f"⚠️ Experiment Agent: Added missing keys: {missing_keys}")

            hypothesis = experiment.get("hypothesis", "")
            print(f"💡 Experiment Agent: Hypothesis: {hypothesis[:100]}...")

            # Compute RIS scores if we have a hypothesis and centroids
            if hypothesis and centroids:
                print("📊 Experiment Agent: Computing RIS scores...")
                try:
                    research_scores = compute_complete_ris(
                        hypothesis=hypothesis,
                        gap_description=gap_description,
                        research_goal=research_goal,
                        centroids=centroids
                    )
                    state["research_scores"] = research_scores
                    print(f"✅ Experiment Agent: RIS computed - Overall: {research_scores.get('ris', 'N/A')}")
                except Exception as e:
                    print(f"⚠️ Experiment Agent: RIS computation failed: {str(e)}")
                    # Default scores if computation fails
                    state["research_scores"] = {
                        "novelty": 5.0,
                        "feasibility": 5.0,
                        "impact": 5.0,
                        "risk": 5.0,
                        "ris": 5.0
                    }
            else:
                print("⚠️ Experiment Agent: No hypothesis or centroids available for RIS")
                # Default scores if computation fails
                state["research_scores"] = {
                    "novelty": 5.0,
                    "feasibility": 5.0,
                    "impact": 5.0,
                    "risk": 5.0,
                    "ris": 5.0
                }

            state["experiment"] = experiment
            print("🎉 Experiment Agent: Experiment design completed successfully")

        except Exception as e:
            print(f"⚠️ Experiment Agent: LLM experiment design failed: {str(e)}")
            # Provide fallback experiment
            print("🔄 Experiment Agent: Using fallback experiment design...")
            fallback_experiment = {
                "hypothesis": f"Addressing the gap in '{gap_description}' will improve performance",
                "dataset_suggestion": "Standard benchmark dataset for this domain",
                "metrics": ["Accuracy", "F1-Score", "Runtime"],
                "baseline_methods": ["Existing Method A", "Existing Method B"],
                "proposed_method": "Novel approach targeting the identified gap"
            }
            state["experiment"] = fallback_experiment
            
            # Default scores for fallback
            state["research_scores"] = {
                "novelty": 5.0,
                "feasibility": 5.0,
                "impact": 5.0,
                "risk": 5.0,
                "ris": 5.0
            }

    except Exception as e:
        error_msg = f"Experiment agent failed: {str(e)}"
        print(f"❌ Experiment Agent: {error_msg}")
        state["error"] = error_msg
        
        # Ultimate fallback
        fallback_experiment = {
            "hypothesis": f"Research hypothesis for gap (error: {str(e)})",
            "dataset_suggestion": "Standard benchmark dataset",
            "metrics": ["Accuracy", "F1-Score"],
            "baseline_methods": ["Baseline Method"],
            "proposed_method": "Proposed Method"
        }
        state["experiment"] = fallback_experiment
        
        # Default scores for fallback
        state["research_scores"] = {
            "novelty": 5.0,
            "feasibility": 5.0,
            "impact": 5.0,
            "risk": 5.0,
            "ris": 5.0
        }

    return state
