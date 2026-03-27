import json
import logging
from typing import Any

from langchain_groq import ChatGroq

from app.agent.state import AgentState
from app.agent.tools import fetch_country, CountryNotFoundError, CountryAPIError
from app.config import get_settings

logger = logging.getLogger(__name__)

MODEL = "llama-3.3-70b-versatile"


def _get_llm() -> ChatGroq:
    settings = get_settings()
    return ChatGroq(model=MODEL, api_key=settings.groq_api_key, temperature=0)


async def extract_country(state: AgentState) -> dict[str, Any]:
    llm = _get_llm()
    prompt = (
        "Extract the country name and the user's intent from this question.\n"
        'Respond ONLY with valid JSON: {"country": "...", "intent": "..."}\n'
        "If no country is mentioned, set country to null.\n\n"
        f"Question: {state['question']}"
    )

    try:
        response = await llm.ainvoke(prompt)
        parsed = json.loads(response.content)
        country = parsed.get("country")
        intent = parsed.get("intent", "general info")

        if not country:
            return {
                "error": "Could not identify a country in your question. "
                "Please mention a specific country."
            }

        logger.info("Extracted country=%s intent=%s", country, intent)
        return {"country": country, "intent": intent}

    except (json.JSONDecodeError, KeyError) as exc:
        logger.error("LLM extraction failed: %s", exc)
        return {
            "error": "Failed to understand the question. "
            "Please rephrase with a specific country name."
        }


async def fetch_data(state: AgentState) -> dict[str, Any]:
    if state.get("error"):
        return {}

    try:
        data, cached = await fetch_country(state["country"])
        return {"country_data": data, "cached": cached}
    except CountryNotFoundError:
        return {
            "error": f"Country '{state['country']}' not found. Please check the spelling."
        }
    except CountryAPIError as exc:
        logger.error("Country API error: %s", exc)
        return {
            "error": "External data source is temporarily unavailable. Please try again later."
        }


async def synthesize_answer(state: AgentState) -> dict[str, Any]:
    if state.get("error"):
        return {"answer": state["error"]}

    llm = _get_llm()
    prompt = (
        "Answer the user's question using the country data below.\n"
        "Be concise, accurate, and helpful. Use the data provided — do not make up facts.\n\n"
        f"Question: {state['question']}\n"
        f"Country data: {json.dumps(state['country_data'], indent=2)}"
    )

    response = await llm.ainvoke(prompt)
    return {"answer": response.content}