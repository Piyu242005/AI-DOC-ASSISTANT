"""
fallback_manager.py – Fault-tolerant fallback chain executor.
Tries the preferred provider first, then walks the fallback chain on failure.
"""
from typing import Dict, List, Tuple
from providers.base_provider import BaseProvider, ProviderResponse

# Global fallback order
FALLBACK_CHAIN = ["Groq", "Gemini", "OpenRouter", "Hugging Face"]


class FallbackManager:
    """Executes prompts with automatic fallback across available providers."""

    def __init__(self, providers: Dict[str, BaseProvider]):
        self.providers = providers

    def execute_with_fallback(
        self,
        prompt: str,
        preferred_provider: str,
        timeout: int = 30,
    ) -> Tuple[ProviderResponse, List[str]]:
        """
        Try preferred_provider first, then fall through FALLBACK_CHAIN.
        Returns (ProviderResponse, fallback_log).
        """
        fallback_log: List[str] = []

        # Build execution order: preferred first, then the rest
        order = [preferred_provider] + [
            p for p in FALLBACK_CHAIN if p != preferred_provider
        ]

        for provider_name in order:
            provider = self.providers.get(provider_name)
            if not provider:
                fallback_log.append(f"{provider_name}: ⚪ Not configured (no API key)")
                continue

            response = provider.generate(prompt, timeout=timeout)
            if response.success:
                # Mark fallback_used if we ended up on a different provider
                response.fallback_used = provider_name != preferred_provider
                return response, fallback_log
            else:
                # Classify error type for status display
                err = response.error or ""
                if "429" in err or "quota" in err.lower() or "rate" in err.lower():
                    status = "🟡 Rate Limited"
                else:
                    status = "🔴 Error"
                fallback_log.append(f"{provider_name}: {status} – {err[:120]}")

        # All providers failed
        all_failed = ProviderResponse(
            text="❌ All AI providers failed. Please check your API keys.",
            provider="None",
            model="None",
            response_time=0.0,
            token_usage=None,
            success=False,
            error="All providers exhausted",
        )
        return all_failed, fallback_log
