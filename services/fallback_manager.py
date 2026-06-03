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

    def execute_stream_with_fallback(
        self,
        prompt: str,
        preferred_provider: str,
        timeout: int = 30,
        status_callback=None,
    ):
        fallback_log: List[str] = []
        order = [preferred_provider] + [
            p for p in FALLBACK_CHAIN if p != preferred_provider
        ]

        for provider_name in order:
            provider = self.providers.get(provider_name)
            if not provider:
                fallback_log.append(f"{provider_name}: ⚪ Not configured (no API key)")
                continue

            if status_callback:
                if provider_name == preferred_provider:
                    status_callback(f"⚡ Streaming via {provider_name}...")
                else:
                    status_callback(f"🔄 Switching to {provider_name}...")

            try:
                gen = provider.generate_stream(prompt, timeout=timeout)
                # Test connection by pulling first chunk
                first_chunk = next(gen)

                # Connection successful!
                def stream_wrapper():
                    yield first_chunk
                    try:
                        while True:
                            yield next(gen)
                    except StopIteration as e:
                        response = e.value
                        response.fallback_used = provider_name != preferred_provider
                        return response

                return stream_wrapper(), fallback_log

            except StopIteration as ex:
                # Generator immediately returned without yielding
                response = ex.value
                response.fallback_used = provider_name != preferred_provider

                def empty_wrapper():
                    yield ""  # Just to be a valid generator
                    return response

                return empty_wrapper(), fallback_log
            except Exception as e:
                if status_callback:
                    status_callback(f"⚠️ {provider_name} unavailable")
                err = str(e)
                if "429" in err or "quota" in err.lower() or "rate" in err.lower():
                    status = "🟡 Rate Limited"
                else:
                    status = "🔴 Error"
                fallback_log.append(f"{provider_name}: {status} – {err[:120]}")

        # All providers failed
        def failed_stream():
            yield "❌ All AI providers failed. Please check your API keys."
            return ProviderResponse(
                text="❌ All AI providers failed. Please check your API keys.",
                provider="None",
                model="None",
                response_time=0.0,
                token_usage=None,
                success=False,
                error="All providers exhausted",
            )

        return failed_stream(), fallback_log
