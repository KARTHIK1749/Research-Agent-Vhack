"""
Gemini Service - Centralized LLM wrapper for MARIS v2
Provides unified interface to Gemini API with JSON output enforcement and error handling.
"""
import os
import json
import time
from typing import Dict, Any, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Initialize Gemini
def _initialize_gemini():
    """Initialize Gemini with API key from environment."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    genai.configure(api_key=api_key)

# Initialize on module import
try:
    _initialize_gemini()
except Exception as e:
    print(f"Warning: Failed to initialize Gemini: {e}")

def call_gemini(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    max_retries: int = 3,
    model_name: str = "gemini-1.5-flash"
) -> str:
    """
    Call Gemini API with structured prompts and retry logic.
    
    Args:
        system_prompt: System prompt defining the role and behavior
        user_prompt: User prompt with the actual task
        temperature: Sampling temperature (0.0-1.0)
        max_retries: Maximum number of retry attempts
        model_name: Gemini model to use
    
    Returns:
        Raw text response from Gemini
    """
    for attempt in range(max_retries):
        try:
            # Configure model
            model = genai.GenerativeModel(
                model_name=model_name,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            
            # Combine prompts
            full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
            
            # Generate response
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=2048,
                )
            )
            
            # Extract text
            if response.text:
                return response.text.strip()
            else:
                raise ValueError("Empty response from Gemini")
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise Exception(f"Gemini API failed after {max_retries} attempts: {str(e)}")
            
            # Wait before retry (exponential backoff)
            wait_time = 2 ** attempt
            time.sleep(wait_time)
    
    return ""

def call_gemini_with_json_enforcement(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    max_retries: int = 3,
    model_name: str = "gemini-1.5-flash"
) -> Dict[str, Any]:
    """
    Call Gemini with strict JSON output enforcement.
    
    Args:
        system_prompt: System prompt defining the role and behavior
        user_prompt: User prompt with the actual task
        temperature: Sampling temperature (0.0-1.0)
        max_retries: Maximum number of retry attempts
        model_name: Gemini model to use
    
    Returns:
        Parsed JSON response as dictionary
    """
    # Add JSON enforcement to system prompt
    enhanced_system_prompt = f"""{system_prompt}

CRITICAL: You must output your response as valid JSON only. Do not include any explanations, apologies, or text outside the JSON structure. Your entire response must be parseable by json.loads()."""
    
    # Add JSON instruction to user prompt
    enhanced_user_prompt = f"""{user_prompt}

Remember: Output ONLY valid JSON. No other text."""
    
    for attempt in range(max_retries):
        try:
            response_text = call_gemini(
                system_prompt=enhanced_system_prompt,
                user_prompt=enhanced_user_prompt,
                temperature=temperature,
                max_retries=1,  # Handle retries at this level
                model_name=model_name
            )
            
            # Try to parse JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                # If JSON parsing fails, try to extract JSON from response
                try:
                    # Look for JSON between ```json and ```
                    if "```json" in response_text:
                        json_start = response_text.find("```json") + 7
                        json_end = response_text.find("```", json_start)
                        if json_end != -1:
                            json_text = response_text[json_start:json_end].strip()
                            return json.loads(json_text)
                    
                    # Look for JSON between { and }
                    if "{" in response_text and "}" in response_text:
                        json_start = response_text.find("{")
                        json_end = response_text.rfind("}") + 1
                        json_text = response_text[json_start:json_end]
                        return json.loads(json_text)
                    
                    raise json.JSONDecodeError(f"Could not extract JSON from response: {e}")
                    
                except json.JSONDecodeError:
                    if attempt == max_retries - 1:
                        # Return error structure as fallback
                        return {
                            "error": "JSON parsing failed",
                            "raw_response": response_text,
                            "attempt": attempt + 1
                        }
                    
                    # Retry with stronger JSON enforcement
                    enhanced_system_prompt += "\n\nOUTPUT VALID JSON ONLY. NO OTHER TEXT."
                    continue
                    
        except Exception as e:
            if attempt == max_retries - 1:
                return {
                    "error": f"Gemini call failed: {str(e)}",
                    "attempt": attempt + 1
                }
            
            # Wait before retry
            time.sleep(2 ** attempt)
    
    return {"error": "All retry attempts failed"}

# Legacy compatibility functions
def llm_call(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    """
    Legacy compatibility function for existing code.
    
    Args:
        system_prompt: System prompt
        user_prompt: User prompt
        temperature: Sampling temperature
    
    Returns:
        Text response from Gemini
    """
    return call_gemini(system_prompt, user_prompt, temperature)

def llm_call_structured(system_prompt: str, user_prompt: str, output_schema: Dict[str, Any], temperature: float = 0.2) -> Dict[str, Any]:
    """
    Legacy compatibility function for structured output.
    
    Args:
        system_prompt: System prompt
        user_prompt: User prompt
        output_schema: Expected output schema (ignored, using JSON enforcement)
        temperature: Sampling temperature
    
    Returns:
        Parsed JSON response as dictionary
    """
    return call_gemini_with_json_enforcement(system_prompt, user_prompt, temperature)

def test_gemini_connection() -> bool:
    """
    Test Gemini API connection.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        response = call_gemini(
            system_prompt="You are a helpful assistant.",
            user_prompt="Respond with 'OK' to confirm connection.",
            temperature=0.1,
            max_retries=1
        )
        return "OK" in response.upper()
    except Exception as e:
        print(f"Gemini connection test failed: {e}")
        return False
