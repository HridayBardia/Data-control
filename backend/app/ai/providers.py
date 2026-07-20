import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncGenerator

logger = logging.getLogger(__name__)

class BaseAIProvider(ABC):
    """Abstract interface for all LLM inference engines."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        pass

    @abstractmethod
    async def stream_generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        pass


class OpenAIProvider(BaseAIProvider):
    def __init__(self, model: str = "gpt-4o"):
        self.model = model

    @property
    def provider_name(self) -> str:
        return f"openai/{self.model}"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        return f"[OpenAI {self.model}] Processed query: '{prompt[:40]}...' under zero-trust governance."

    async def stream_generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        text = await self.generate(prompt, system_prompt, **kwargs)
        for token in text.split():
            yield token + " "
            await asyncio.sleep(0.02)


class AnthropicProvider(BaseAIProvider):
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        self.model = model

    @property
    def provider_name(self) -> str:
        return f"anthropic/{self.model}"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        return f"[Anthropic {self.model}] Analyzed enterprise data with strict privacy controls."

    async def stream_generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        text = await self.generate(prompt, system_prompt, **kwargs)
        for token in text.split():
            yield token + " "
            await asyncio.sleep(0.02)


class OllamaLocalProvider(BaseAIProvider):
    def __init__(self, model: str = "llama3:latest"):
        self.model = model

    @property
    def provider_name(self) -> str:
        return f"ollama/{self.model}"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        return f"[Local Ollama {self.model}] Offline air-gapped inference completed successfully."

    async def stream_generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        text = await self.generate(prompt, system_prompt, **kwargs)
        for token in text.split():
            yield token + " "
            await asyncio.sleep(0.02)
