"""
Ollama LLM client for local AI inference.
Supports tool use with compatible models (qwen2.5, llama3.1, etc.)
"""

import json
import httpx
from typing import Optional, List, Dict, Any, AsyncGenerator, Callable
from dataclasses import dataclass

from .config import settings


@dataclass
class ToolCall:
    """Tool call from LLM."""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    """Structured LLM response."""
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    model: str = ""
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None


class LLMClient:
    """
    Ollama client with tool use support.
    Compatible with models that support function calling.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None
    ):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.api_key = api_key or settings.OLLAMA_API_KEY
        self.default_model = default_model or settings.OLLAMA_MODEL
        self._http_client: Optional[httpx.AsyncClient] = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._http_client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=settings.AGENT_TIMEOUT_SECONDS
            )
        return self._http_client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    def _format_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format tools for Ollama API.
        Ollama uses OpenAI-compatible format.
        """
        formatted = []
        for tool in tools:
            formatted.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                }
            })
        return formatted

    def _parse_tool_calls(self, response_data: Dict) -> Optional[List[ToolCall]]:
        """Parse tool calls from Ollama response."""
        message = response_data.get("message", {})
        tool_calls = message.get("tool_calls")

        if not tool_calls:
            return None

        parsed = []
        for i, tc in enumerate(tool_calls):
            if "function" in tc:
                func = tc["function"]
                try:
                    args = json.loads(func.get("arguments", "{}"))
                except json.JSONDecodeError:
                    args = {}

                parsed.append(ToolCall(
                    id=f"call_{i}",
                    name=func.get("name", ""),
                    arguments=args
                ))

        return parsed if parsed else None

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """
        Send chat request to Ollama.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name to use (defaults to OLLAMA_MODEL)
            tools: Optional list of tool definitions
            temperature: Sampling temperature (0-2)
            stream: Whether to stream response
            max_tokens: Maximum tokens to generate

        Returns:
            LLMResponse with content and optional tool calls
        """
        import time
        start_time = time.time()

        payload: Dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature or settings.AGENT_TEMPERATURE,
            }
        }

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        if tools:
            payload["tools"] = self._format_tools(tools)

        try:
            response = await self.http_client.post(
                "/api/chat",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            latency = (time.time() - start_time) * 1000

            message = data.get("message", {})
            content = message.get("content", "")

            # Parse tool calls
            tool_calls = self._parse_tool_calls(data)

            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                model=data.get("model", payload["model"]),
                tokens_used=data.get("eval_count"),  # Ollama token count
                latency_ms=latency
            )

        except httpx.HTTPStatusError as e:
            raise LLMError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise LLMError(f"Request error: {str(e)}")
        except json.JSONDecodeError as e:
            raise LLMError(f"Invalid JSON response: {str(e)}")

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response from Ollama.

        Args:
            messages: List of message dicts
            model: Model name to use
            temperature: Sampling temperature

        Yields:
            Content chunks as they're generated
        """
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature or settings.AGENT_TEMPERATURE,
            }
        }

        try:
            async with self.http_client.stream(
                "POST",
                "/api/chat",
                json=payload
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data:
                                content = data["message"].get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue

        except httpx.HTTPStatusError as e:
            raise LLMError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise LLMError(f"Request error: {str(e)}")

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Simple text generation (non-chat endpoint).

        Args:
            prompt: The prompt text
            model: Model to use
            system: Optional system prompt
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        payload: Dict[str, Any] = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature or settings.AGENT_TEMPERATURE,
            }
        }

        if system:
            payload["system"] = system

        try:
            response = await self.http_client.post(
                "/api/generate",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            return data.get("response", "")

        except httpx.HTTPStatusError as e:
            raise LLMError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise LLMError(f"Request error: {str(e)}")

    async def list_models(self) -> List[str]:
        """List available models from Ollama server."""
        try:
            response = await self.http_client.get("/api/tags")
            response.raise_for_status()
            data = response.json()

            models = data.get("models", [])
            return [m.get("name") for m in models if m.get("name")]

        except Exception as e:
            raise LLMError(f"Failed to list models: {str(e)}")

    def is_tool_capable(self, model: Optional[str] = None) -> bool:
        """Check if model supports tool use."""
        tool_capable_models = [
            "qwen2.5", "llama3.1", "llama3.2", "mistral-nemo",
            "nemotron", "mixtral", "command-r", "hermes3"
        ]
        check_model = (model or self.default_model).lower()
        return any(tc in check_model for tc in tool_capable_models)


class LLMError(Exception):
    """LLM client error."""
    pass


# Global client instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def reset_llm_client() -> None:
    """Reset the client (useful for testing)."""
    global _llm_client
    if _llm_client:
        # Can't properly close async client here, but clear reference
        _llm_client = None
