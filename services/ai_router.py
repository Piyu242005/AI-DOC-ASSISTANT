"""
ai_router.py – AI Router Service.
Builds configured provider instances and returns a ready AgentEngine.
"""

from typing import Dict

from providers.base_provider import BaseProvider
from providers.gemini_provider import GeminiProvider
from providers.groq_provider import GroqProvider
from providers.huggingface_provider import HuggingFaceProvider
from providers.openrouter_provider import OpenRouterProvider
from services.agent_engine import AgentEngine


def build_providers(env: Dict[str, str]) -> Dict[str, BaseProvider]:
    """
    Instantiate only providers that have API keys configured.
    Returns a dict mapping provider name → provider instance.
    """
    providers: Dict[str, BaseProvider] = {}

    if env.get("GEMINI_API_KEY"):
        providers["Gemini"] = GeminiProvider(env["GEMINI_API_KEY"])

    if env.get("GROQ_API_KEY"):
        providers["Groq"] = GroqProvider(env["GROQ_API_KEY"])

    if env.get("OPENROUTER_API_KEY"):
        providers["OpenRouter"] = OpenRouterProvider(env["OPENROUTER_API_KEY"])

    if env.get("HUGGINGFACE_API_KEY"):
        providers["Hugging Face"] = HuggingFaceProvider(env["HUGGINGFACE_API_KEY"])

    return providers


def get_agent(providers: Dict[str, BaseProvider], mode: str = "auto") -> AgentEngine:
    """Create and return an AgentEngine for the given mode."""
    return AgentEngine(providers=providers, mode=mode)


def get_all_provider_meta() -> list:
    """Return static metadata for all providers (for UI display)."""
    return [
        {
            "name": "Gemini",
            "icon": "🔵",
            "color": "#3b82f6",
            "key_env": "GEMINI_API_KEY",
        },
        {"name": "Groq", "icon": "⚡", "color": "#f59e0b", "key_env": "GROQ_API_KEY"},
        {
            "name": "OpenRouter",
            "icon": "🌐",
            "color": "#10b981",
            "key_env": "OPENROUTER_API_KEY",
        },
        {
            "name": "Hugging Face",
            "icon": "🤗",
            "color": "#f97316",
            "key_env": "HUGGINGFACE_API_KEY",
        },
    ]
