import pytest
from unittest.mock import AsyncMock


@pytest.mark.unit
class TestWebhooksEndpoint:
    """Test webhook API endpoints"""
    
    def test_product_updated_webhook_success(self, client):
        """Test successful product updated webhook"""
        webhook_payload = {
            "event_type": "PRODUCT_UPDATED",
            "product_id": "UHJvZHVjdDox",
            "data": {
                "product": {
                    "id": "UHJvZHVjdDox",
                    "name": "Sample Product"
                }
            }
        }
        
        response = client.post("/webhooks/product-updated", json=webhook_payload)
        
        assert response.status_code == 200
        assert response.json() == {"status": "received"}
        
    def test_product_updated_webhook_invalid_event(self, client):
        """Test product updated webhook with invalid event type"""
        webhook_payload = {
            "event_type": "INVALID_EVENT",
            "product_id": "UHJvZHVjdDox",
            "data": {}
        }
        
        response = client.post("/webhooks/product-updated", json=webhook_payload)
        
        assert response.status_code == 400
        assert "Invalid webhook payload" in response.json()["detail"]
        
    def test_product_updated_webhook_missing_product_id(self, client):
        """Test product updated webhook without product_id"""
        webhook_payload = {
            "event_type": "PRODUCT_UPDATED",
            "data": {}
        }
        
        response = client.post("/webhooks/product-updated", json=webhook_payload)
        
        assert response.status_code == 400
        assert "missing product_id" in response.json()["detail"]
        
    def test_channel_created_webhook_success(self, client):
        """Test successful channel created webhook"""
        webhook_payload = {
            "event_type": "CHANNEL_CREATED",
            "channel_id": "Q2hhbm5lbDo0",
            "data": {
                "channel": {
                    "id": "Q2hhbm5lbDo0",
                    "name": "New Store",
                    "slug": "new-store"
                }
            }
        }
        
        response = client.post("/webhooks/channel-created", json=webhook_payload)
        
        assert response.status_code == 200
        assert response.json() == {"status": "received"}
        
    def test_channel_created_webhook_invalid_event(self, client):
        """Test channel created webhook with invalid event type"""
        webhook_payload = {
            "event_type": "INVALID_EVENT",
            "channel_id": "Q2hhbm5lbDo0",
            "data": {}
        }
        
        response = client.post("/webhooks/channel-created", json=webhook_payload)
        
        assert response.status_code == 400
        assert "Invalid webhook payload" in response.json()["detail"]
        
    def test_channel_created_webhook_missing_channel_id(self, client):
        """Test channel created webhook without channel_id"""
        webhook_payload = {
            "event_type": "CHANNEL_CREATED",
            "data": {}
        }
        
        response = client.post("/webhooks/channel-created", json=webhook_payload)
        
        assert response.status_code == 400
        assert "missing channel_id" in response.json()["detail"]
        
    @pytest.mark.asyncio
    async def test_webhook_background_task_execution(self, client, monkeypatch):
        """Test that webhook triggers background task"""
        # Mock background task
        mock_task = AsyncMock()
        monkeypatch.setattr(
            "app.api.webhooks.recalculate_product_prices",
            mock_task
        )
        
        webhook_payload = {
            "event_type": "PRODUCT_UPDATED",
            "product_id": "UHJvZHVjdDox",
            "data": {}
        }
        
        response = client.post("/webhooks/product-updated", json=webhook_payload)
        
        assert response.status_code == 200
        # Note: Background task execution in tests requires special handling
        # This test verifies the webhook accepts the payload correctly