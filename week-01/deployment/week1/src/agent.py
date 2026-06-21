"""Conference assistant agent — deployed to Google Cloud Run.

Same shape as Lab 6: an ADK `LlmAgent` with a handful of tools, model routed
through Cohere via LiteLLM.

The variable name `root_agent` is the convention ADK looks for.
"""

from datetime import date, datetime, timedelta

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm


def calculator(expression: str) -> dict:
    """Evaluates a Python expression and returns the result.

    Supports arithmetic (e.g. '23 * 47') AND date math via date.fromisoformat('YYYY-MM-DD').
    To compute days between two dates:
        (date.fromisoformat('2026-09-14') - date.fromisoformat('2026-05-14')).days

    Do NOT pass raw quoted date strings like "'2026-09-14' - '2026-05-14'" —
    that's string subtraction and will fail.

    ONLY pass date expressions or arithmetic expressions.

    Args:
        expression: A Python expression to evaluate.
    """
    safe_globals = {
        "__builtins__": {},
        "date":      date,
        "datetime":  datetime,
        "timedelta": timedelta,
        "abs": abs, "min": min, "max": max, "round": round,
    }
    return {"result": eval(expression, safe_globals, {})}


KB = {
    "price_per_ticket": 89,
    "attendees":        47,
    "conference_date":  "2026-09-14",
    "venue":            "Lisbon Congress Center",
}


def lookup(key: str) -> dict:
    """Looks up a fact in the conference knowledge base.

    Args:
        key: The key to look up. Available keys: 'attendees', 'price_per_ticket', 'conference_date', 'venue'.
    """
    return {
        "value": KB.get(key, f"unknown key: {key}"),
        "available_keys": list[str](KB.keys()),
    }


def get_today() -> dict:
    """Returns today's date in ISO format (YYYY-MM-DD).

    Use this whenever the question depends on knowing the current date — relative
    dates, days until an event, etc.
    """
    return {"today": date.today().isoformat()}


root_agent = LlmAgent(
    name="conference_assistant",
    model=LiteLlm(model="cohere_chat/command-a-03-2025"),
    instruction=(
        "You are a precise conference assistant. Use the tools to gather facts and to "
        "do any arithmetic. Prefer the conference knowledge base for conference facts. "
        "When you have enough information, stop calling tools and answer."
        "When calling the calculator tool, ALWAYS pass a single-line expression with no "
        "comments, no newlines, and no variable assignments."
    ),
    tools=[calculator, lookup, get_today],
)
