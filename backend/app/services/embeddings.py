import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

class EmbeddingProvider(ABC):
    """Abstract interface for all embedding model providers."""
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def default_dimension(self) -> int:
        pass

    @abstractmethod
    async def embed_texts(self, texts: List[str], dimension: Optional[int] = None) -> List[List[float]]:
        """Embed a batch of texts asynchronously."""
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI Embedding Provider (text-embedding-3-small, text-embedding-3-large)."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model
        
    @property
    def provider_name(self) -> str:
        return f"openai-{self.model}"

    @property
    def default_dimension(self) -> int:
        return 1536 if "small" in self.model else 3072

    async def embed_texts(self, texts: List[str], dimension: Optional[int] = None) -> List[List[float]]:
        if not self.api_key:
            # Fallback deterministic mock for offline/dev environments
            return self._mock_embed(texts, dimension or self.default_dimension)

        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload: Dict[str, Any] = {
            "input": texts,
            "model": self.model
        }
        if dimension:
            payload["dimensions"] = dimension

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]

    def _mock_embed(self, texts: List[str], dim: int) -> List[List[float]]:
        embeddings = []
        for text in texts:
            seed = sum(ord(c) for c in text)
            vec = [(seed * (i + 1) % 1000) / 1000.0 for i in range(dim)]
            norm = (sum(x * x for x in vec) ** 0.5) or 1.0
            embeddings.append([x / norm for x in vec])
        return embeddings


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Local Ollama Embedding Provider (nomic-embed-text, mxbai-embed-large)."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "nomic-embed-text"):
        self.base_url = base_url.rstrip('/')
        self.model = model

    @property
    def provider_name(self) -> str:
        return f"ollama-{self.model}"

    @property
    def default_dimension(self) -> int:
        return 768

    async def embed_texts(self, texts: List[str], dimension: Optional[int] = None) -> List[List[float]]:
        embeddings = []
        url = f"{self.base_url}/api/embeddings"
        async with httpx.AsyncClient(timeout=60.0) as client:
            for text in texts:
                resp = await client.post(url, json={"model": self.model, "prompt": text})
                if resp.status_code == 200:
                    embeddings.append(resp.json()["embedding"])
                else:
                    # Deterministic fallback vector
                    seed = sum(ord(c) for c in text)
                    dim = dimension or self.default_dimension
                    vec = [(seed * (i + 1) % 1000) / 1000.0 for i in range(dim)]
                    embeddings.append(vec)
        return embeddings


class VoyageEmbeddingProvider(EmbeddingProvider):
    """Voyage AI Embedding Provider (voyage-3, voyage-code-3)."""

    def __init__(self, api_key: str, model: str = "voyage-3"):
        self.api_key = api_key
        self.model = model

    @property
    def provider_name(self) -> str:
        return f"voyage-{self.model}"

    @property
    def default_dimension(self) -> int:
        return 1024

    async def embed_texts(self, texts: List[str], dimension: Optional[int] = None) -> List[List[float]]:
        if not self.api_key:
            return OpenAIEmbeddingProvider("")._mock_embed(texts, dimension or self.default_dimension)

        url = "https://api.voyageai.com/v1/embeddings"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json={"input": texts, "model": self.model})
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]


class ResilientEmbeddingService:
    """Enterprise Embedding Router with batching, exponential backoff, and fallback chain."""

    def __init__(self, providers: List[EmbeddingProvider], target_dimension: int = 1536):
        self.providers = providers
        self.target_dimension = target_dimension
        self._cache: Dict[str, List[float]] = {}

    async def embed_query(self, query: str) -> List[float]:
        res = await self.embed_texts([query])
        return res[0]

    async def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        if not texts:
            return []

        results: List[List[float]] = [[] for _ in texts]
        uncached_indices = []
        uncached_texts = []

        # Check cache
        for idx, text in enumerate(texts):
            if text in self._cache:
                results[idx] = self._cache[text]
            else:
                uncached_indices.append(idx)
                uncached_texts.append(text)

        if not uncached_texts:
            return results

        # Process batches asynchronously across providers with retries
        for i in range(0, len(uncached_texts), batch_size):
            batch_texts = uncached_texts[i:i + batch_size]
            batch_indices = uncached_indices[i:i + batch_size]

            embedded_batch = await self._embed_batch_with_fallback(batch_texts)

            for idx, vec in zip(batch_indices, embedded_batch):
                results[idx] = vec
                self._cache[texts[idx]] = vec

        return results

    async def _embed_batch_with_fallback(self, batch_texts: List[str]) -> List[List[float]]:
        for provider in self.providers:
            for attempt in range(3):
                try:
                    embeddings = await provider.embed_texts(batch_texts, dimension=self.target_dimension)
                    return self._adapt_dimensions(embeddings, self.target_dimension)
                except Exception as e:
                    logger.warning(f"Embedding provider {provider.provider_name} failed attempt {attempt+1}: {e}")
                    await asyncio.sleep(0.2 * (2 ** attempt))
        
        # Absolute fallback: mock generator
        logger.error("All configured embedding providers failed. Using emergency fallback.")
        return OpenAIEmbeddingProvider("")._mock_embed(batch_texts, self.target_dimension)

    def _adapt_dimensions(self, embeddings: List[List[float]], target_dim: int) -> List[List[float]]:
        adapted = []
        for vec in embeddings:
            if len(vec) == target_dim:
                adapted.append(vec)
            elif len(vec) > target_dim:
                # Truncate and normalize
                sub = vec[:target_dim]
                norm = (sum(x * x for x in sub) ** 0.5) or 1.0
                adapted.append([x / norm for x in sub])
            else:
                # Zero pad
                padded = vec + [0.0] * (target_dim - len(vec))
                adapted.append(padded)
        return adapted
