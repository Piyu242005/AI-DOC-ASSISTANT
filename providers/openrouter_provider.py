"""
openrouter_provider.py – OpenRouter adapter via REST API (no extra SDK needed).
Model: meta-llama/llama-3-8b-instruct:free (free tier)
"""

import time

import requests

from providers.base_provider import BaseProvider, ProviderResponse


class OpenRouterProvider(BaseProvider):
    name = "OpenRouter"
    icon = "🌐"
    color = "#10b981"
    model_id = "meta-llama/llama-3-8b-instruct:free"
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str):
        self._api_key = api_key

    def is_configured(self) -> bool:
        return bool(self._api_key)

    def generate(self, prompt: str, timeout: int = 30) -> ProviderResponse:
        start = time.time()
        try:
            resp = requests.post(
                self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://ai-doc-assistant.app",
                },
                json={
                    "model": self.model_id,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            usage_raw = data.get("usage", {})
            usage = (
                {
                    "input_tokens": usage_raw.get("prompt_tokens"),
                    "output_tokens": usage_raw.get("completion_tokens"),
                }
                if usage_raw
                else None
            )
            return ProviderResponse(
                text=data["choices"][0]["message"]["content"],
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

    def generate_stream(self, prompt: str, timeout: int = 30):
        # Pseudo-streaming for REST APIs
        start = time.time()
        response = self.generate(prompt, timeout=timeout)

        if not response.success:
            yield f"\n\n[Stream Error: {response.error}]"
            response.first_token_time = round(time.time() - start, 2)
            return response

        first_token_time = time.time() - start

        # Stream word by word
        words = response.text.split(" ")
        for i, word in enumerate(words):
            # yield with trailing space, except last word
            content = word + " " if i < len(words) - 1 else word
            yield content
            time.sleep(0.01)  # tiny delay to simulate streaming effect

        response.first_token_time = round(first_token_time, 2)
        return response
