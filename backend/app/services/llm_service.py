"""
Legacy LLM Service - MARIS v2 (Gemini Only)
This service now forwards all calls to the centralized Gemini service.
"""
from typing import Dict, Any
from app.services.gemini_service import call_gemini, call_gemini_with_json_enforcement

def llm_call(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 2048
) -> str:
    """
    Legacy compatibility function - forwards to Gemini service.
    
    Args:
        system_prompt: System instructions
        user_prompt: User input/question
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate (ignored, using Gemini defaults)
    
    Returns:
        Generated text response
    """
    return call_gemini(system_prompt, user_prompt, temperature)


def llm_call_structured(
    system_prompt: str,
    user_prompt: str,
    output_schema: Dict[str, Any],
    temperature: float = 0.2
) -> Dict[str, Any]:
    """
    Legacy compatibility function - forwards to Gemini service with JSON enforcement.
    
    Args:
        system_prompt: System instructions
        user_prompt: User input
        output_schema: Description of expected output structure (ignored, using JSON enforcement)
        temperature: Sampling temperature
    
    Returns:
        Parsed JSON as dictionary
    """
    return call_gemini_with_json_enforcement(system_prompt, user_prompt, temperature)
