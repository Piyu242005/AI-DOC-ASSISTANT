"""
gemini_provider.py – Google Gemini adapter using the official google-genai SDK.
Model: gemini-2.0-flash
"""
import time
from typing import Optional
from google import genai
from providers.base_provider import BaseProvider, ProviderResponse


class GeminiProvider(BaseProvider):
    name = "Gemini"
    icon = "🔵"
    color = "#3b82f6"
    model_id = "gemini-2.0-flash"

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._client = genai.Client(api_key=api_key) if api_key else None

    def is_configured(self) -> bool:
        return bool(self._api_key)

    def generate(self, prompt: str, timeout: int = 30) -> ProviderResponse:
        start = time.time()
        try:
            response = self._client.models.generate_content(
                model=self.model_id,
                contents=prompt,
            )
            return ProviderResponse(
                text=response.text,
                provider=self.name,
                model=self.model_id,
                response_time=round(time.time() - start, 2),
                token_usage=None,
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
