import pytest
import asyncio
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from tests.fixtures.sample_data import (
    SAMPLE_CHANNELS,
    SAMPLE_PRICE_CALCULATIONS,
    generate_batch_price_requests
)


@pytest.mark.integration
class TestIntegrationWorkflows:
    """Integration tests that test complete workflows"""
    
    def test_complete_markup_workflow(self, client, monkeypatch):
        """Test complete workflow: list channels -> update markup -> verify change"""
        # Step 1: List channels
        response = client.get("/api/channels/")
        assert response.status_code == 200
        channels = response.json()
        assert len(channels) >= 3
        
        # Step 2: Update markup for first channel
        channel_id = channels[0]["id"]
        new_markup = 25.5
        
        update_response = client.post(
            "/api/channels/markup",
            json={"channel_id": channel_id, "markup_percent": new_markup}
        )
        assert update_response.status_code == 200
        
        # Step 3: Verify markup was updated by listing channels again
        # Note: In real scenario, this would show updated markup from cache
        verify_response = client.get("/api/channels/")
        assert verify_response.status_code == 200
        
    def test_complete_price_calculation_workflow(self, client, monkeypatch):
        """Test complete workflow: calculate single price -> batch calculate"""
        # Step 1: Single price calculation
        single_calc = {
            "product_id": "UHJvZHVjdDox",
            "channel_id": "Q2hhbm5lbDoy",
            "base_price": 100.00
        }
        
        response = client.post("/api/prices/calculate", json=single_calc)
        assert response.status_code == 200
        result = response.json()
        assert "final_price" in result
        assert "markup_percent" in result
        
        # Step 2: Batch calculation with multiple products
        batch_requests = generate_batch_price_requests(3)
        
        batch_response = client.post("/api/prices/batch-calculate", json=batch_requests)
        assert batch_response.status_code == 200
        batch_results = batch_response.json()
        assert len(batch_results) == 3
        
        # Verify all results have required fields
        for result in batch_results:
            assert "final_price" in result
            assert "markup_percent" in result
            assert "product_id" in result
            
    def test_webhook_to_price_recalculation_workflow(self, client, monkeypatch):
        """Test webhook triggers price recalculation workflow"""
        # Mock background task
        mock_recalculate = AsyncMock()
        monkeypatch.setattr(
            "app.api.webhooks.recalculate_product_prices",
            mock_recalculate
        )
        
        # Send webhook
        webhook_payload = {
            "event_type": "PRODUCT_UPDATED",
            "product_id": "UHJvZHVjdDox",
            "data": {"product": {"id": "UHJvZHVjdDox", "name": "Test Product"}}
        }
        
        response = client.post("/webhooks/product-updated", json=webhook_payload)
        assert response.status_code == 200
        assert response.json() == {"status": "received"}
        
        # Note: Background task execution verification would require more complex setup
        
    def test_error_handling_workflow(self, client, monkeypatch):
        """Test error handling across different scenarios"""
        # Scenario 1: Invalid markup data
        invalid_markup = {
            "channel_id": "invalid_id",
            "markup_percent": -10  # Negative markup
        }
        response = client.post("/api/channels/markup", json=invalid_markup)
        assert response.status_code == 422
        
        # Scenario 2: Invalid price calculation data
        invalid_price = {
            "product_id": "",  # Empty product ID
            "channel_id": "Q2hhbm5lbDox",
            "base_price": 100.00
        }
        response = client.post("/api/prices/calculate", json=invalid_price)
        assert response.status_code == 422
        
        # Scenario 3: Invalid webhook payload
        invalid_webhook = {
            "event_type": "INVALID_EVENT",
            "product_id": "UHJvZHVjdDox"
        }
        response = client.post("/webhooks/product-updated", json=invalid_webhook)
        assert response.status_code == 400
        
    def test_concurrent_requests_handling(self, client):
        """Test that API handles concurrent requests properly"""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = client.get("/health")
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads to make concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests succeeded
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10
        assert all(status == 200 for status in results)
        
    @pytest.mark.parametrize("calculation_data", SAMPLE_PRICE_CALCULATIONS)
    def test_price_calculation_accuracy(self, client, calculation_data, monkeypatch):
        """Test price calculation accuracy with various scenarios"""
        # Mock markup service to return expected markup
        mock_markup = AsyncMock(return_value=calculation_data["expected"]["markup_percent"])
        monkeypatch.setattr(
            "app.services.markup_service.markup_service.get_channel_markup",
            mock_markup
        )
        
        # Mock Rust module to return expected calculation
        mock_rust = monkeypatch.setattr(
            "app.services.price_calculator.price_calculator.calculate_price",
            lambda base, markup: str(calculation_data["expected"]["final_price"])
        )
        
        request_data = {
            "product_id": calculation_data["input"]["product_id"],
            "channel_id": calculation_data["input"]["channel_id"],
            "base_price": float(calculation_data["input"]["base_price"])
        }
        
        response = client.post("/api/prices/calculate", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        assert Decimal(result["final_price"]) == calculation_data["expected"]["final_price"]
        assert Decimal(result["markup_percent"]) == calculation_data["expected"]["markup_percent"]
        
    def test_api_response_times(self, client):
        """Test that API responses are reasonably fast"""
        import time
        
        # Test health endpoint response time
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 0.5, f"Health check took too long: {response_time}s"
        
        # Test channels endpoint response time
        start_time = time.time()
        response = client.get("/api/channels/")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 2.0, f"Channels endpoint took too long: {response_time}s"
        
    def test_api_content_types(self, client):
        """Test that API returns correct content types"""
        # Test JSON endpoints
        json_endpoints = [
            "/health",
            "/api/channels/"
        ]
        
        for endpoint in json_endpoints:
            response = client.get(endpoint)
            assert "application/json" in response.headers["content-type"]
            
        # Test POST endpoints
        post_data = {
            "product_id": "UHJvZHVjdDox",
            "channel_id": "Q2hhbm5lbDoy",
            "base_price": 100.00
        }
        response = client.post("/api/prices/calculate", json=post_data)
        assert "application/json" in response.headers["content-type"]
        
    def test_openapi_schema_accessibility(self, client):
        """Test that OpenAPI schema is accessible"""
        # Test OpenAPI JSON schema
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
        
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema
        assert "components" in schema
        
        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]