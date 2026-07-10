from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from app.core.config import settings


class LLMProvider(ABC):
    """Abstract Base Class for a unified interaction interface with various LLM endpoints."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """Run single prompt generation."""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """Run chat message list generation."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API Provider implementation."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o") -> None:
        self.client = AsyncOpenAI(
            api_key=api_key or settings.OPENAI_API_KEY or "mock-key"
        )
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self.chat(messages, temperature, max_tokens, **kwargs)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {str(e)}")


class ClaudeProvider(LLMProvider):
    """Anthropic Claude API Provider stub implementation."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet"
    ) -> None:
        self.api_key = api_key
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        return f"Mock response from Claude ({self.model}) for: {prompt}"

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        return f"Mock conversation response from Claude ({self.model})"


class GeminiProvider(LLMProvider):
    """Google Gemini API Provider stub implementation."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "gemini-1.5-pro"
    ) -> None:
        self.api_key = api_key
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        return f"Mock response from Gemini ({self.model}) for: {prompt}"

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        return f"Mock conversation response from Gemini ({self.model})"


class LocalLlamaProvider(LLMProvider):
    """Local Llama API Provider stub implementation."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.1",
    ) -> None:
        self.base_url = base_url
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        return f"Mock response from Local Llama ({self.model}) for: {prompt}"

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        return f"Mock conversation response from Local Llama ({self.model})"
