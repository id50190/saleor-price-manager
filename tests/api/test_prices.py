import pytest
from decimal import Decimal
from unittest.mock import AsyncMock


@pytest.mark.unit
class TestPricesEndpoint:
    """Test price calculation API endpoints"""
    
    def test_calculate_price_success(self, client, sample_price_request):
        """Test successful price calculation"""
        response = client.post(
            "/api/prices/calculate",
            json=sample_price_request
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == "UHJvZHVjdDox"
        assert data["channel_id"] == "Q2hhbm5lbDoy"
        assert data["base_price"] == "100.0"
        assert "final_price" in data
        assert "markup_percent" in data
        
    def test_calculate_price_with_markup(self, client, mock_rust_module, monkeypatch):
        """Test price calculation with specific markup"""
        # Mock markup service to return 15%
        mock_markup = AsyncMock(return_value=Decimal('15'))
        monkeypatch.setattr(
            "app.services.markup_service.markup_service.get_channel_markup",
            mock_markup
        )
        
        # Mock rust calculation
        mock_rust_module.calculate_price.return_value = "115.00"
        
        request_data = {
            "product_id": "UHJvZHVjdDox",
            "channel_id": "Q2hhbm5lbDoy",
            "base_price": 100.00
        }
        
        response = client.post("/api/prices/calculate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["final_price"] == "115.00"
        assert data["markup_percent"] == "15"
        
        # Verify rust module was called correctly
        mock_rust_module.calculate_price.assert_called_once_with("100.0", "15")
        
    def test_calculate_price_invalid_data(self, client):
        """Test price calculation with invalid data"""
        response = client.post(
            "/api/prices/calculate",
            json={
                "product_id": "invalid",
                "channel_id": "invalid",
                "base_price": -10  # Negative price
            }
        )
        
        assert response.status_code == 422  # Validation error
        
    def test_calculate_price_missing_fields(self, client):
        """Test price calculation with missing required fields"""
        response = client.post(
            "/api/prices/calculate",
            json={"product_id": "UHJvZHVjdDox"}
        )
        
        assert response.status_code == 422
        
    def test_batch_calculate_success(self, client, mock_rust_module, monkeypatch):
        """Test successful batch price calculation"""
        # Mock markup service
        mock_markup = AsyncMock(return_value=Decimal('15'))
        monkeypatch.setattr(
            "app.services.markup_service.markup_service.get_channel_markup",
            mock_markup
        )
        
        batch_request = [
            {
                "product_id": "UHJvZHVjdDox",
                "channel_id": "Q2hhbm5lbDoy",
                "base_price": 100.00
            },
            {
                "product_id": "UHJvZHVjdDoy",
                "channel_id": "Q2hhbm5lbDox",
                "base_price": 50.00
            }
        ]
        
        response = client.post("/api/prices/batch-calculate", json=batch_request)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("final_price" in item for item in data)
        assert all("markup_percent" in item for item in data)
        
    def test_batch_calculate_empty_list(self, client):
        """Test batch calculation with empty list"""
        response = client.post("/api/prices/batch-calculate", json=[])
        
        assert response.status_code == 200
        assert response.json() == []
        
    def test_calculate_price_service_error(self, client, sample_price_request, monkeypatch):
        """Test price calculation when service throws error"""
        # Mock service to raise exception
        mock_service = AsyncMock(side_effect=Exception("Service unavailable"))
        monkeypatch.setattr(
            "app.services.markup_service.markup_service.get_channel_markup",
            mock_service
        )
        
        response = client.post("/api/prices/calculate", json=sample_price_request)
        
        assert response.status_code == 400
        assert "Price calculation failed" in response.json()["detail"]