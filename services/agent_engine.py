"""
agent_engine.py – Agent Decision Engine.
Decides which provider to use (auto or manual) and returns a structured AgentDecision.
"""

from dataclasses import dataclass
from typing import Dict, List

from providers.base_provider import BaseProvider, ProviderResponse
from services.fallback_manager import FallbackManager
from services.task_classifier import classify_task


@dataclass
class AgentDecision:
    """Full decision record returned after each agent run."""

    task_type: str
    selected_provider: str  # Provider the agent intended to use
    actual_provider: str  # Provider that actually responded
    reason: str  # Why this provider was chosen
    response: ProviderResponse
    fallback_log: List[str]
    fallback_used: bool


class StreamWrapper:
    """Wraps a generator to catch its final return value (ProviderResponse)."""

    def __init__(self, generator, task_type, preferred, reason, fallback_log):
        self.generator = generator
        self.task_type = task_type
        self.preferred = preferred
        self.reason = reason
        self.fallback_log = fallback_log
        self.final_decision = None

    def __iter__(self):
        try:
            while True:
                yield next(self.generator)
        except StopIteration as e:
            response = e.value
            self.final_decision = AgentDecision(
                task_type=self.task_type,
                selected_provider=self.preferred,
                actual_provider=response.provider,
                reason=self.reason,
                response=response,
                fallback_log=self.fallback_log,
                fallback_used=response.fallback_used,
            )


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
            reason = "Manually selected by user"

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

    def run_stream(self, prompt: str, status_callback=None) -> StreamWrapper:
        if self.mode == "auto":
            task_type, preferred, reason = classify_task(prompt)
        else:
            task_type = "manual"
            preferred = self.mode
            reason = "Manually selected by user"

        generator, fallback_log = self._fallback_manager.execute_stream_with_fallback(
            prompt=prompt,
            preferred_provider=preferred,
            status_callback=status_callback,
        )

        return StreamWrapper(generator, task_type, preferred, reason, fallback_log)
