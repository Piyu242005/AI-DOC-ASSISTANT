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

    def generate_stream(self, prompt: str, timeout: int = 30):
        start = time.time()
        first_token_time = 0.0
        full_text = []

        # Note: exceptions here bubble up on the first next() call
        stream = self._client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            timeout=timeout,
            stream=True,
        )

        try:
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    if first_token_time == 0.0:
                        first_token_time = time.time() - start
                    full_text.append(content)
                    yield content

            response_time = time.time() - start
            final_text = "".join(full_text)
            # Approximate usage
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
