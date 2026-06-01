"""
groq_provider.py – Groq adapter using the official groq Python SDK.
Model: llama-3.1-8b-instant (fast, great for coding tasks)
"""

import time

from providers.base_provider import BaseProvider, ProviderResponse


class GroqProvider(BaseProvider):
    name = "Groq"
    icon = "⚡"
    color = "#f59e0b"
    model_id = "llama-3.1-8b-instant"

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._client = None
        if api_key:
            from groq import Groq

            self._client = Groq(api_key=api_key)

    def is_configured(self) -> bool:
        return bool(self._api_key)

    def generate(self, prompt: str, timeout: int = 30) -> ProviderResponse:
        start = time.time()
        try:
            resp = self._client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout,
            )
            usage = None
            if resp.usage:
                usage = {
                    "input_tokens": resp.usage.prompt_tokens,
                    "output_tokens": resp.usage.completion_tokens,
                }
            return ProviderResponse(
                text=resp.choices[0].message.content,
                provider=self.name,
                model=self.model_id,
                response_time=round(time.time() - start, 2),
                token_usage=usage,
                success=True,
            )
        except Exception as e:
            return ProviderResponse(
                text="",
                provider=self.name,
                model=self.model_id,
                response_time=round(time.time() - start, 2),
                token_usage=None,
                success=False,
                error=str(e),
            )
