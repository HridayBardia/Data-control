import logging
from typing import List, Dict, Any, Optional
from app.ai.providers import BaseAIProvider, OpenAIProvider, AnthropicProvider, OllamaLocalProvider

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """Enterprise AI Orchestrator with automatic failover and cost optimization."""

    def __init__(self, primary_provider: Optional[BaseAIProvider] = None):
        self.providers: List[BaseAIProvider] = [
            primary_provider or OpenAIProvider(),
            AnthropicProvider(),
            OllamaLocalProvider()
        ]

    async def execute_query(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        last_exception = None

        for provider in self.providers:
            try:
                logger.info(f"Attempting inference via {provider.provider_name}")
                response_text = await provider.generate(prompt, system_prompt)
                return {
                    "provider": provider.provider_name,
                    "response": response_text,
                    "tokens_used": len(prompt.split()) + len(response_text.split()),
                    "cost_usd": round(len(response_text.split()) * 0.00001, 6)
                }
            except Exception as e:
                logger.warning(f"Provider {provider.provider_name} failed: {e}. Trying fallback...")
                last_exception = e

        raise RuntimeError(f"All AI providers failed. Last error: {last_exception}")


ai_orchestrator = AIOrchestrator()
