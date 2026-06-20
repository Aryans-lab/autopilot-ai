"""
NanoCorp v3.0 - AI Provider

Real AI integration with multiple LLM backends.
Supports: Anthropic Claude, OpenAI GPT, Ollama (free)
"""
from __future__ import annotations
from typing import Dict, List, Optional, Any, AsyncIterator
from abc import ABC, abstractmethod
import os
import asyncio
from dataclasses import dataclass

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class AIResponse:
    """Response from AI provider."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None


class AIProvider(ABC):
    """Base class for AI providers."""
    
    @abstractmethod
    async def chat(self, prompt: str, system: Optional[str] = None, **kwargs) -> AIResponse:
        """Send a chat message."""
        pass
    
    @abstractmethod
    async def stream(self, prompt: str, system: Optional[str] = None, **kwargs) -> AsyncIterator[str]:
        """Stream a chat response."""
        pass


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20240620"):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
    
    async def chat(self, prompt: str, system: Optional[str] = None, **kwargs) -> AIResponse:
        """Send chat via Anthropic."""
        if not self.client:
            return AIResponse(content="[Anthropic API key not configured]", model=self.model)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system or "You are a helpful AI assistant.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return AIResponse(
            content=response.content[0].text,
            model=self.model,
            usage={"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
        )
    
    async def stream(self, prompt: str, system: Optional[str] = None, **kwargs) -> AsyncIterator[str]:
        """Stream chat via Anthropic."""
        if not self.client:
            yield "[Anthropic API key not configured]"
            return
        
        with self.client.messages.stream(
            model=self.model,
            max_tokens=4096,
            system=system or "You are a helpful AI assistant.",
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                yield text


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    async def chat(self, prompt: str, system: Optional[str] = None, **kwargs) -> AIResponse:
        """Send chat via OpenAI."""
        if not self.client:
            return AIResponse(content="[OpenAI API key not configured]", model=self.model)
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        
        return AIResponse(
            content=response.choices[0].message.content,
            model=self.model,
            usage={"input_tokens": response.usage.prompt_tokens, "output_tokens": response.usage.completion_tokens}
        )
    
    async def stream(self, prompt: str, system: Optional[str] = None, **kwargs) -> AsyncIterator[str]:
        """Stream chat via OpenAI."""
        if not self.client:
            yield "[OpenAI API key not configured]"
            return
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            **kwargs
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class OllamaProvider(AIProvider):
    """Ollama - free local AI."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url
        self.model = model
    
    async def chat(self, prompt: str, system: Optional[str] = None, **kwargs) -> AIResponse:
        """Send chat via Ollama."""
        import httpx
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={"model": self.model, "messages": messages, "stream": False}
                )
                response.raise_for_status()
                data = response.json()
                return AIResponse(content=data["message"]["content"], model=self.model)
        except Exception as e:
            return AIResponse(content=f"[Ollama not available: {e}]", model=self.model)
    
    async def stream(self, prompt: str, system: Optional[str] = None, **kwargs) -> AsyncIterator[str]:
        """Stream chat via Ollama."""
        import httpx
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json={"model": self.model, "messages": messages, "stream": True}
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            import json
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
        except Exception as e:
            yield f"[Ollama error: {e}]"


class LiteLLMProvider(AIProvider):
    """LiteLLM - unified API for many AI providers."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "anthropic/claude-3-5-sonnet"):
        self.api_key = api_key or os.environ.get("LITELLM_KEY") or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.base_url = "https://api.litellm.io"
    
    async def chat(self, prompt: str, system: Optional[str] = None, **kwargs) -> AIResponse:
        """Send chat via LiteLLM."""
        import httpx
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json={"model": self.model, "messages": messages},
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                data = response.json()
                return AIResponse(
                    content=data["choices"][0]["message"]["content"],
                    model=data["model"]
                )
        except Exception as e:
            return AIResponse(content=f"[LiteLLM error: {e}]", model=self.model)
    
    async def stream(self, prompt: str, system: Optional[str] = None, **kwargs) -> AsyncIterator[str]:
        """Stream chat via LiteLLM."""
        import httpx
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    json={"model": self.model, "messages": messages, "stream": True},
                    headers={"Authorization": f"Bearer {self.api_key}"}
                ) as response:
                    async for line in response.aiter_lines():
                        if line and line.startswith("data:"):
                            import json
                            data = json.loads(line[5:])
                            if "choices" in data and data["choices"][0].get("delta", {}).get("content"):
                                yield data["choices"][0]["delta"]["content"]
        except Exception as e:
            yield f"[LiteLLM error: {e}]"


class SimulationProvider(AIProvider):
    """Simulated AI for demo purposes when no API key is available."""
    
    def __init__(self, model: str = "simulated"):
        self.model = model
        self._responses = {
            "hello": "Hello! I'm your AI assistant. How can I help you today?",
            "hi": "Hi there! I'm your AI assistant. How can I help you today?",
            "test": "This is a simulated response. Add ANTHROPIC_API_KEY or OPENAI_API_KEY to enable real AI.",
        }
    
    async def chat(self, prompt: str, system: Optional[str] = None, **kwargs) -> AIResponse:
        """Simulate AI response."""
        prompt_lower = prompt.lower()
        for key, response in self._responses.items():
            if key in prompt_lower:
                return AIResponse(content=response, model=self.model)
        return AIResponse(
            content=f"[SIMULATED AI] Prompt: {prompt[:50]}...\n\nThis is a simulation. Add ANTHROPIC_API_KEY or OPENAI_API_KEY to enable real AI responses.",
            model=self.model
        )
    
    async def stream(self, prompt: str, system: Optional[str] = None, **kwargs) -> AsyncIterator[str]:
        """Simulate streaming."""
        response = (await self.chat(prompt, system, **kwargs)).content
        for char in response:
            yield char
            await asyncio.sleep(0.01)


class AIHub:
    """
    Central AI hub that auto-detects the best available provider.
    Priority: Anthropic > OpenAI > Ollama > Simulation
    """
    
    def __init__(self):
        self.providers: Dict[str, AIProvider] = {}
        self._default = None
        self._setup_providers()
    
    def _setup_providers(self):
        """Setup all available providers."""
        has_api = False
        
        # Try Anthropic
        if ANTHROPIC_AVAILABLE and os.environ.get("ANTHROPIC_API_KEY"):
            self.providers["anthropic"] = AnthropicProvider()
            self._default = "anthropic"
            has_api = True
        
        # Try OpenAI
        if OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
            self.providers["openai"] = OpenAIProvider()
            if not self._default:
                self._default = "openai"
            has_api = True
        
        # Always add Ollama
        self.providers["ollama"] = OllamaProvider()
        
        # Add simulation as fallback
        self.providers["simulation"] = SimulationProvider()
        if not self._default:
            self._default = "simulation"
        
        # Set litellm if available but no other API key
        if not has_api:
            self.providers["litellm"] = LiteLLMProvider()
    
    async def chat(
        self,
        prompt: str,
        system: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Send chat with auto-selected provider."""
        provider_name = provider or self._default
        if provider_name not in self.providers:
            provider_name = self._default
        
        return await self.providers[provider_name].chat(prompt, system, **kwargs)
    
    async def stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat with auto-selected provider."""
        provider_name = provider or self._default
        if provider_name not in self.providers:
            provider_name = self._default
        
        async for chunk in self.providers[provider_name].stream(prompt, system, **kwargs):
            yield chunk
    
    def list_providers(self) -> List[str]:
        """List available providers."""
        return list(self.providers.keys())
    
    def get_default(self) -> str:
        """Get default provider."""
        return self._default


# Global AI hub
_ai_hub: Optional[AIHub] = None

def get_ai_hub() -> AIHub:
    """Get global AI hub."""
    global _ai_hub
    if _ai_hub is None:
        _ai_hub = AIHub()
    return _ai_hub

def create_ai_provider(provider: str = "auto", **kwargs) -> AIProvider:
    """Create a specific AI provider."""
    if provider == "auto":
        return get_ai_hub()
    
    if provider == "anthropic":
        return AnthropicProvider(**kwargs)
    elif provider == "openai":
        return OpenAIProvider(**kwargs)
    elif provider == "ollama":
        return OllamaProvider(**kwargs)
    elif provider == "litellm":
        return LiteLLMProvider(**kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider}")
