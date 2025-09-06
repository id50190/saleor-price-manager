import pytest


@pytest.mark.unit
class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test successful health check"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        
    def test_health_check_headers(self, client):
        """Test health check response headers"""
        response = client.get("/health")
        
        assert "application/json" in response.headers["content-type"]
        assert response.headers["content-length"] == "15"