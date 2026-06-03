"""
base_provider.py – Abstract base class and unified response format.
All AI provider adapters must implement this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderResponse:
    """Unified response format returned by every provider adapter."""

    text: str
    provider: str
    model: str
    response_time: float  # seconds
    token_usage: Optional[dict]  # {"input_tokens": int, "output_tokens": int}
    success: bool
    error: Optional[str] = None
    fallback_used: bool = False  # True if this wasn't the originally selected provider
    first_token_time: float = 0.0  # seconds until first token was received


class BaseProvider(ABC):
    """Abstract base class for all AI provider adapters."""

    name: str = "BaseProvider"
    icon: str = "🤖"
    color: str = "#888888"

    @abstractmethod
    def generate(self, prompt: str, timeout: int = 30) -> ProviderResponse:
        """Send a prompt and return a unified ProviderResponse."""
        pass

    @abstractmethod
    def generate_stream(self, prompt: str, timeout: int = 30):
        """
        Yields strings (tokens) as they arrive.
        Finally yields a ProviderResponse object containing metadata.
        """
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True if the provider has a valid API key / config."""
        pass

    def get_status(self) -> str:
        """Return 'online' or 'offline' based on configuration."""
        return "online" if self.is_configured() else "offline"
