"""Ollama API Client"""

import httpx
import logging
from typing import Generator
from app.config import OLLAMA_BASE_URL

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for communicating with Ollama API"""

    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.timeout = 300.0

    def is_running(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            return False

    def list_models(self) -> list[str]:
        """List available models from Ollama"""
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=20)
            response.raise_for_status()
            data = response.json()
            models = [item.get("name") for item in data.get("models", [])]
            return models
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def generate(self, model: str, prompt: str, stream: bool = False) -> str | Generator:
        """Generate response from model

        Args:
            model: Model name
            prompt: Input prompt
            stream: Whether to stream response

        Returns:
            Generated response text or generator for streaming
        """
        payload = {"model": model, "prompt": prompt, "stream": stream}

        try:
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

            if stream:
                return self._stream_response(response)
            else:
                data = response.json()
                return data.get("response", "").strip()
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise

    def _stream_response(self, response: httpx.Response) -> Generator:
        """Stream response from Ollama"""
        for line in response.iter_lines():
            if line:
                data = httpx.Response(content=line).json()
                chunk = data.get("response", "")
                if chunk:
                    yield chunk
