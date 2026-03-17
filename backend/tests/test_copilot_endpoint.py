"""Integration tests for copilot endpoint."""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from backend.main import app


def test_copilot_chat_endpoint_exists():
    """Test that copilot chat endpoint is accessible."""
    client = TestClient(app)

    # Mock the LLM adapter to avoid needing a real LLM
    with patch("backend.dependencies.get_llm_adapter") as mock_get_llm:
        mock_llm = MagicMock()

        # Mock the stream method to return test tokens
        async def mock_stream(*args, **kwargs):
            for token in ["Hello", " ", "World"]:
                yield token

        mock_llm.stream = mock_stream
        mock_get_llm.return_value = mock_llm

        response = client.post(
            "/v1/copilot/chat",
            json={"message": "Hello", "session_id": "test"},
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
