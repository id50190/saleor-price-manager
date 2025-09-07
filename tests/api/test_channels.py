import pytest
from unittest.mock import AsyncMock


@pytest.mark.unit
class TestChannelsEndpoint:
    """Test channels API endpoints"""
    
    def test_list_channels_success(self, client, sample_channels, mock_saleor_api):
        """Test successful channel listing - now returns Pool demo data"""
        mock_saleor_api.list_channels.return_value = sample_channels
        
        response = client.get("/api/channels/")
        
        assert response.status_code == 200
        data = response.json()
        # With Pool demo data fallback, we should get 4 pools
        assert len(data) == 4
        assert data[0]["name"] == "Pool #1"
        assert data[1]["markup_percent"] == "10"  # Pool #2 has 10% markup
        
    def test_list_channels_empty(self, client, mock_saleor_api):
        """Test channel listing when no channels exist - returns demo Pool data as fallback"""
        mock_saleor_api.list_channels.return_value = []
        
        response = client.get("/api/channels/")
        
        assert response.status_code == 200
        data = response.json()
        # With fallback to Pool demo data, we should get 4 pools
        assert len(data) >= 4  # Should have Pool #1-4 as fallback
        assert any("Pool #" in channel["name"] for channel in data)
        
    def test_set_markup_success(self, client, sample_markup_request):
        """Test successful markup update"""
        response = client.post(
            "/api/channels/markup",
            json=sample_markup_request
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["markup"]["markup_percent"] == "25.00"
        
    def test_set_markup_invalid_data(self, client):
        """Test markup update with invalid data"""
        response = client.post(
            "/api/channels/markup",
            json={"channel_id": "invalid", "markup_percent": -5}
        )
        
        assert response.status_code == 422  # Validation error
        
    def test_set_markup_missing_fields(self, client):
        """Test markup update with missing required fields"""
        response = client.post(
            "/api/channels/markup",
            json={"channel_id": "Q2hhbm5lbDox"}
        )
        
        assert response.status_code == 422
        
    def test_set_markup_service_failure(self, client, sample_markup_request, monkeypatch):
        """Test markup update when service fails"""
        # Mock service failure
        mock_service = AsyncMock(return_value=False)
        monkeypatch.setattr(
            "app.services.markup_service.markup_service.set_channel_markup",
            mock_service
        )
        
        response = client.post(
            "/api/channels/markup",
            json=sample_markup_request
        )
        
        assert response.status_code == 400
        assert "Failed to update channel markup" in response.json()["detail"]