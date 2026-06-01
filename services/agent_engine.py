"""
agent_engine.py – Agent Decision Engine.
Decides which provider to use (auto or manual) and returns a structured AgentDecision.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from providers.base_provider import BaseProvider, ProviderResponse
from services.task_classifier import classify_task
from services.fallback_manager import FallbackManager


@dataclass
class AgentDecision:
    """Full decision record returned after each agent run."""
    task_type: str
    selected_provider: str       # Provider the agent intended to use
    actual_provider: str         # Provider that actually responded
    reason: str                  # Why this provider was chosen
    response: ProviderResponse
    fallback_log: List[str]
    fallback_used: bool


class AgentEngine:
    """
    Orchestrates task classification → provider selection → execution with fallback.
    Mode 'auto': uses task_classifier to pick the best provider.
    Mode '<provider_name>': forces that specific provider, still falls back on failure.
    """

    def __init__(self, providers: Dict[str, BaseProvider], mode: str = "auto"):
        self.providers = providers
        self.mode = mode
        self._fallback_manager = FallbackManager(providers)

    def run(self, prompt: str) -> AgentDecision:
        if self.mode == "auto":
            task_type, preferred, reason = classify_task(prompt)
        else:
            task_type = "manual"
            preferred = self.mode
            reason = f"Manually selected by user"

        response, fallback_log = self._fallback_manager.execute_with_fallback(
            prompt=prompt,
            preferred_provider=preferred,
        )

        return AgentDecision(
            task_type=task_type,
            selected_provider=preferred,
            actual_provider=response.provider,
            reason=reason,
            response=response,
            fallback_log=fallback_log,
            fallback_used=response.fallback_used,
        )
