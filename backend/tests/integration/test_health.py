"""Integration tests for health endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test main health endpoint returns expected structure."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "environment" in data
        assert "services" in data

    def test_liveness_probe(self, client):
        """Test liveness probe returns 200."""
        response = client.get("/health/live")
        assert response.status_code == 200

    def test_readiness_probe(self, client):
        """Test readiness probe."""
        response = client.get("/health/ready")
        # May return 200 or 503 depending on service availability
        assert response.status_code in [200, 503]
