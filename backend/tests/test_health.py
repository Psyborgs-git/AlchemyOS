from fastapi.testclient import TestClient

from backend.main import app


def test_health_endpoint_returns_phase_one_status() -> None:
    """Test health endpoint returns Phase 1 status."""
    client = TestClient(app)
    response = client.get("/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
    assert data["phase"] == 1
    assert "plugins" in data
    assert isinstance(data["plugins"], list)
