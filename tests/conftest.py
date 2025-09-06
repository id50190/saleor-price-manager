import pytest
import asyncio
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from faker import Faker

from app.core.config import settings
from main import app

fake = Faker()

# Override settings for testing
settings.SALEOR_APP_TOKEN = "test_token"
settings.REDIS_URL = "redis://localhost:6379/15"  # Test DB


@pytest.fixture
def client():
    """FastAPI test client"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    mock = MagicMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=1)
    return mock


@pytest.fixture
def mock_saleor_api():
    """Mock Saleor API responses"""
    mock = MagicMock()
    mock.list_channels = AsyncMock(return_value=[
        {
            "id": "Q2hhbm5lbDox",
            "name": "Default Channel",
            "slug": "default-channel",
            "metadata": [{"key": "price_markup_percent", "value": "0"}]
        },
        {
            "id": "Q2hhbm5lbDoy",
            "name": "Moscow Store",
            "slug": "moscow",
            "metadata": [{"key": "price_markup_percent", "value": "15"}]
        }
    ])
    mock.get_channel = AsyncMock()
    mock.update_channel_metadata = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def sample_channels():
    """Sample channel data for tests"""
    return [
        {
            "id": "Q2hhbm5lbDox",
            "name": "Default Channel",
            "slug": "default-channel",
            "markup_percent": "0",
            "metadata": [{"key": "price_markup_percent", "value": "0"}]
        },
        {
            "id": "Q2hhbm5lbDoy",
            "name": "Moscow Store",
            "slug": "moscow",
            "markup_percent": "15",
            "metadata": [{"key": "price_markup_percent", "value": "15"}]
        },
        {
            "id": "Q2hhbm5lbDoz",
            "name": "SPb Store",
            "slug": "spb",
            "markup_percent": "10",
            "metadata": [{"key": "price_markup_percent", "value": "10"}]
        }
    ]


@pytest.fixture
def sample_price_request():
    """Sample price calculation request"""
    return {
        "product_id": "UHJvZHVjdDox",
        "channel_id": "Q2hhbm5lbDoy",
        "base_price": 100.00
    }


@pytest.fixture
def sample_markup_request():
    """Sample markup update request"""
    return {
        "channel_id": "Q2hhbm5lbDox",
        "markup_percent": 25.0
    }


@pytest.fixture
def mock_rust_module():
    """Mock Rust price calculator module"""
    mock = MagicMock()
    mock.calculate_price = MagicMock(side_effect=lambda base, markup: 
        str(Decimal(base) * (Decimal('1') + Decimal(markup) / Decimal('100'))))
    mock.batch_calculate = MagicMock(return_value=[
        {"product_id": "test1", "final_price": "115.00"},
        {"product_id": "test2", "final_price": "55.00"}
    ])
    return mock


@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch, mock_redis, mock_saleor_api, mock_rust_module):
    """Auto-mock external dependencies for all tests"""
    # Mock Redis
    monkeypatch.setattr("app.services.markup_service.markup_service.redis", mock_redis)
    
    # Mock Saleor API functions
    monkeypatch.setattr("app.saleor.api.list_channels", mock_saleor_api.list_channels)
    monkeypatch.setattr("app.saleor.api.get_channel", mock_saleor_api.get_channel)
    monkeypatch.setattr("app.saleor.api.update_channel_metadata", mock_saleor_api.update_channel_metadata)
    
    # Mock Rust module
    monkeypatch.setattr("app.services.price_calculator.price_calculator", mock_rust_module)


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()