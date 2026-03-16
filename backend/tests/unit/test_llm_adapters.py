"""Unit tests for LLM adapters."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.adapters.outbound.llm.ollama_adapter import OllamaAdapter
from backend.core.ports.outbound.i_llm_port import Message


@pytest.mark.asyncio
async def test_ollama_adapter_complete():
    """Test Ollama adapter completion."""
    adapter = OllamaAdapter(base_url="http://localhost:11434", model="mistral:7b-instruct")

    # Mock the OpenAI client
    with patch.object(adapter.client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_create.return_value = mock_response

        # Test completion
        messages = [Message(role="user", content="Hello")]
        result = await adapter.complete(messages)

        assert result == "Test response"
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_ollama_adapter_stream():
    """Test Ollama adapter streaming."""
    adapter = OllamaAdapter(base_url="http://localhost:11434", model="mistral:7b-instruct")

    # Mock the OpenAI client stream
    async def mock_stream():
        for token in ["Hello", " ", "World"]:
            chunk = MagicMock()
            chunk.choices = [MagicMock()]
            chunk.choices[0].delta.content = token
            yield chunk

    with patch.object(adapter.client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_stream()

        messages = [Message(role="user", content="Hello")]
        tokens = []
        async for token in adapter.stream(messages):
            tokens.append(token)

        assert tokens == ["Hello", " ", "World"]
