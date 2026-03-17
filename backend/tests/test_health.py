from fastapi.testclient import TestClient

from backend.main import app


def test_health_endpoint_returns_phase_two_status() -> None:
    """Test health endpoint returns Phase 2 status."""
    client = TestClient(app)
    response = client.get("/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
    assert data["phase"] == 2
    assert "plugins" in data
    assert isinstance(data["plugins"], list)
    assert "modules" in data
    assert data["modules"]["chemistry_engine"] == "active"
    assert data["modules"]["safety"] == "active"
    assert data["modules"]["smiles_nl"] == "active"
