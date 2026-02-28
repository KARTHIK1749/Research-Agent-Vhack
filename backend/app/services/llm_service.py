"""
Service for LLM calls using Gemini or OpenAI.
"""
import os
from typing import List, Dict, Any, Optional
import json

# Try to import available LLM clients
try:
    from langchain_google_genai import ChatGoogleGenerativeAI 
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False

try:
    from langchain_openai import ChatOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from langchain_core.messages import HumanMessage, SystemMessage

# Global LLM instance
_llm = None


def _get_llm():
    """Get or initialize the LLM client."""
    global _llm
    if _llm is None:
        # Prefer Gemini if available, fallback to OpenAI
        if HAS_GOOGLE and os.getenv("GOOGLE_API_KEY"):
            _llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.3,
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
        elif HAS_OPENAI and os.getenv("OPENAI_API_KEY"):
            _llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.3,
                api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            raise ValueError("No LLM API key found. Set GOOGLE_API_KEY or OPENAI_API_KEY in .env")
    return _llm


def llm_call(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 2048
) -> str:
    """
    Call the LLM with a system and user prompt.

    Args:
        system_prompt: System instructions
        user_prompt: User input/question
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Generated text response
    """
    llm = _get_llm()

    # Update temperature and max_tokens for this call
    if hasattr(llm, 'temperature'):
        llm.temperature = temperature

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = llm.invoke(messages)
    return response.content


def llm_call_structured(
    system_prompt: str,
    user_prompt: str,
    output_schema: Dict[str, Any],
    temperature: float = 0.2
) -> Dict[str, Any]:
    """
    Call LLM and return structured JSON output.

    Args:
        system_prompt: System instructions
        user_prompt: User input
        output_schema: Description of expected output structure
        temperature: Sampling temperature

    Returns:
        Parsed JSON as dictionary
    """
    schema_desc = json.dumps(output_schema, indent=2)

    structured_prompt = f"""{system_prompt}

You must respond with ONLY a valid JSON object matching this schema:
{schema_desc}

Do not include any markdown formatting, explanations, or code blocks. Return raw JSON only."""

    response = llm_call(structured_prompt, user_prompt, temperature)

    # Clean up response (remove markdown code blocks if present)
    response = response.strip()
    if response.startswith("```json"):
        response = response[7:]
    if response.startswith("```"):
        response = response[3:]
    if response.endswith("```"):
        response = response[:-3]
    response = response.strip()

    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        # Fallback: try to extract JSON from the response
        try:
            start = response.index("{")
            end = response.rindex("}") + 1
            return json.loads(response[start:end])
        except (ValueError, json.JSONDecodeError):
            raise ValueError(f"Failed to parse LLM response as JSON: {e}\nResponse: {response[:200]}")
