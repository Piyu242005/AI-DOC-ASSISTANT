"""
helpers.py – Shared utility functions for the Multi-LLM Agent platform.
"""
from typing import Optional


def format_token_usage(token_usage: Optional[dict]) -> str:
    """Format token usage dict into a readable string."""
    if not token_usage:
        return "N/A"
    inp = token_usage.get("input_tokens", "?")
    out = token_usage.get("output_tokens", "?")
    return f"↑ {inp} in · ↓ {out} out"


def status_badge(is_configured: bool) -> str:
    """Return a coloured status label."""
    return "🟢 Online" if is_configured else "⚫ Offline"


def task_type_label(task_type: str) -> str:
    """Human-friendly label for a task type."""
    labels = {
        "coding": "💻 Coding",
        "reasoning": "🧠 Reasoning",
        "experimentation": "🔬 Experimentation",
        "general": "💬 General Q&A",
        "manual": "🎛️ Manual Selection",
    }
    return labels.get(task_type, task_type.title())
