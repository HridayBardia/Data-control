import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from app.ai.providers import (
    BaseAIProvider,
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    GroqProvider,
    AzureOpenAIProvider,
    AWSBedrockProvider,
    OpenRouterProvider,
    OllamaLocalProvider
)

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """
    Enterprise AI Orchestrator supporting:
    - Multi-provider dynamic routing (OpenAI, Anthropic, Gemini, Groq, Azure, Bedrock, OpenRouter, Ollama)
    - Automatic fallback cascade
    - Token budgeting & cost estimation metrics
    - Real-time SSE token streaming
    """

    def __init__(self, primary_provider: Optional[BaseAIProvider] = None):
        self.providers: List[BaseAIProvider] = [
            primary_provider or OpenAIProvider(),
            AnthropicProvider(),
            GeminiProvider(),
            GroqProvider(),
            AzureOpenAIProvider(),
            AWSBedrockProvider(),
            OpenRouterProvider(),
            OllamaLocalProvider()
        ]

    def select_provider(self, provider_name: str) -> BaseAIProvider:
        p_name = provider_name.lower()
        for p in self.providers:
            if p_name in p.provider_name.lower():
                return p
        return self.providers[0]

    async def execute_query(
        self, prompt: str, system_prompt: Optional[str] = None, preferred_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        last_exception = None

        providers_to_try = self.providers
        if preferred_provider:
            selected = self.select_provider(preferred_provider)
            providers_to_try = [selected] + [p for p in self.providers if p != selected]

        for provider in providers_to_try:
            try:
                logger.info(f"Attempting LLM inference via {provider.provider_name}")
                response_text = await provider.generate(prompt, system_prompt)
                tokens_used = len(prompt.split()) + len(response_text.split()) + 25
                cost_usd = round(tokens_used * 0.000005, 6)

                return {
                    "provider": provider.provider_name,
                    "response": response_text,
                    "tokens_used": tokens_used,
                    "cost_usd": cost_usd,
                    "status": "SUCCESS"
                }
            except Exception as e:
                logger.warning(f"Provider {provider.provider_name} failed: {e}. Cascading to next fallback provider...")
                last_exception = e

        raise RuntimeError(f"All enterprise AI providers failed. Last exception: {last_exception}")

    async def stream_query(
        self, prompt: str, system_prompt: Optional[str] = None, preferred_provider: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        provider = self.select_provider(preferred_provider or "openai")
        async for token in provider.stream_generate(prompt, system_prompt):
            yield token


ai_orchestrator = AIOrchestrator()
