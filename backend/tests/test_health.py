from fastapi.testclient import TestClient

from backend.main import app


def test_health_endpoint_returns_phase_zero_status() -> None:
    client = TestClient(app)
    response = client.get("/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0", "phase": 0}
