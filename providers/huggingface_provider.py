"""
huggingface_provider.py – Hugging Face Inference API adapter via REST.
Model: HuggingFaceH4/zephyr-7b-beta
"""

import time

import requests

from providers.base_provider import BaseProvider, ProviderResponse


class HuggingFaceProvider(BaseProvider):
    name = "Hugging Face"
    icon = "🤗"
    color = "#f97316"
    model_id = "HuggingFaceH4/zephyr-7b-beta"
    BASE_URL = "https://api-inference.huggingface.co/models"

    def __init__(self, api_key: str):
        self._api_key = api_key

    def is_configured(self) -> bool:
        return bool(self._api_key)

    def generate(self, prompt: str, timeout: int = 30) -> ProviderResponse:
        start = time.time()
        try:
            resp = requests.post(
                f"{self.BASE_URL}/{self.model_id}",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "inputs": prompt,
                    "parameters": {"max_new_tokens": 512, "return_full_text": False},
                },
                timeout=timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            # Handle list or dict response
            if isinstance(data, list):
                text = data[0].get("generated_text", "").strip()
            else:
                text = str(data)
            return ProviderResponse(
                text=text,
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
