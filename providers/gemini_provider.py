"""
gemini_provider.py – Google Gemini adapter using the official google-genai SDK.
Model: gemini-1.5-flash
"""

import time

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

    def generate_stream(self, prompt: str, timeout: int = 30):
        start = time.time()
        first_token_time = 0.0
        full_text = []

        stream = self._client.models.generate_content_stream(
            model=self.model_id,
            contents=prompt,
        )

        try:
            for chunk in stream:
                content = chunk.text
                if content:
                    if first_token_time == 0.0:
                        first_token_time = time.time() - start
                    full_text.append(content)
                    yield content

            response_time = time.time() - start
            final_text = "".join(full_text)
            usage = {
                "input_tokens": len(prompt) // 4,
                "output_tokens": len(final_text) // 4,
            }
            return ProviderResponse(
                text=final_text,
                provider=self.name,
                model=self.model_id,
                response_time=round(response_time, 2),
                token_usage=usage,
                success=True,
                first_token_time=round(first_token_time, 2),
            )
        except Exception as e:
            response_time = time.time() - start
            yield f"\n\n[Stream Error: {str(e)}]"
            return ProviderResponse(
                text="".join(full_text),
                provider=self.name,
                model=self.model_id,
                response_time=round(response_time, 2),
                token_usage=None,
                success=False,
                error=str(e),
                first_token_time=round(first_token_time, 2),
            )
