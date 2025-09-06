"""Sample data fixtures for testing"""

from decimal import Decimal
from faker import Faker
from typing import List, Dict, Any

fake = Faker()

# Sample Channels
SAMPLE_CHANNELS = [
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
    },
    {
        "id": "Q2hhbm5lbDo0",
        "name": "Kazan Store",
        "slug": "kazan",
        "markup_percent": "12.5",
        "metadata": [{"key": "price_markup_percent", "value": "12.5"}]
    }
]

# Sample Products
SAMPLE_PRODUCTS = [
    {
        "id": "UHJvZHVjdDox",
        "name": "Basic T-Shirt",
        "slug": "basic-tshirt",
        "base_price": Decimal('29.99')
    },
    {
        "id": "UHJvZHVjdDoy",
        "name": "Premium Jeans",
        "slug": "premium-jeans",
        "base_price": Decimal('89.99')
    },
    {
        "id": "UHJvZHVjdDoz",
        "name": "Sports Sneakers",
        "slug": "sports-sneakers",
        "base_price": Decimal('149.99')
    },
    {
        "id": "UHJvZHVjdDo0",
        "name": "Winter Jacket",
        "slug": "winter-jacket",
        "base_price": Decimal('199.99')
    }
]

# Sample Webhook Payloads
SAMPLE_WEBHOOKS = {
    "product_updated": {
        "event_type": "PRODUCT_UPDATED",
        "product_id": "UHJvZHVjdDox",
        "data": {
            "product": {
                "id": "UHJvZHVjdDox",
                "name": "Updated T-Shirt",
                "slug": "updated-tshirt",
                "variants": [
                    {
                        "id": "UHJvZHVjdFZhcmlhbnQ6MQ==",
                        "channelListings": [
                            {
                                "channel": {"id": "Q2hhbm5lbDox", "name": "Default"},
                                "price": {"amount": 29.99, "currency": "USD"}
                            }
                        ]
                    }
                ]
            }
        }
    },
    "channel_created": {
        "event_type": "CHANNEL_CREATED",
        "channel_id": "Q2hhbm5lbDo1",
        "data": {
            "channel": {
                "id": "Q2hhbm5lbDo1",
                "name": "New Regional Store",
                "slug": "new-regional",
                "isActive": True,
                "metadata": []
            }
        }
    }
}

# Sample Price Calculations
SAMPLE_PRICE_CALCULATIONS = [
    {
        "input": {
            "product_id": "UHJvZHVjdDox",
            "channel_id": "Q2hhbm5lbDox",  # 0% markup
            "base_price": Decimal('100.00')
        },
        "expected": {
            "final_price": Decimal('100.00'),
            "markup_percent": Decimal('0')
        }
    },
    {
        "input": {
            "product_id": "UHJvZHVjdDox",
            "channel_id": "Q2hhbm5lbDoy",  # 15% markup
            "base_price": Decimal('100.00')
        },
        "expected": {
            "final_price": Decimal('115.00'),
            "markup_percent": Decimal('15')
        }
    },
    {
        "input": {
            "product_id": "UHJvZHVjdDoy",
            "channel_id": "Q2hhbm5lbDoz",  # 10% markup
            "base_price": Decimal('50.00')
        },
        "expected": {
            "final_price": Decimal('55.00'),
            "markup_percent": Decimal('10')
        }
    },
    {
        "input": {
            "product_id": "UHJvZHVjdDoz",
            "channel_id": "Q2hhbm5lbDo0",  # 12.5% markup
            "base_price": Decimal('200.00')
        },
        "expected": {
            "final_price": Decimal('225.00'),
            "markup_percent": Decimal('12.5')
        }
    }
]

# Error Response Samples
SAMPLE_ERROR_RESPONSES = {
    "validation_error": {
        "detail": [
            {
                "loc": ["body", "markup_percent"],
                "msg": "ensure this value is greater than or equal to 0",
                "type": "value_error.number.not_ge",
                "ctx": {"limit_value": 0}
            }
        ]
    },
    "channel_not_found": {
        "detail": "Channel not found"
    },
    "saleor_api_error": {
        "detail": "Failed to update channel markup: Saleor API error"
    },
    "redis_connection_error": {
        "detail": "Redis connection failed"
    }
}


def generate_random_channel() -> Dict[str, Any]:
    """Generate random channel data for testing"""
    return {
        "id": fake.uuid4(),
        "name": f"{fake.city()} Store",
        "slug": fake.slug(),
        "markup_percent": str(fake.pydecimal(left_digits=2, right_digits=1, positive=True, min_value=0, max_value=50)),
        "metadata": [{"key": "price_markup_percent", "value": str(fake.random_int(0, 30))}]
    }


def generate_random_product() -> Dict[str, Any]:
    """Generate random product data for testing"""
    return {
        "id": fake.uuid4(),
        "name": fake.catch_phrase(),
        "slug": fake.slug(),
        "base_price": fake.pydecimal(left_digits=3, right_digits=2, positive=True, min_value=10, max_value=500)
    }


def generate_batch_price_requests(count: int = 5) -> List[Dict[str, Any]]:
    """Generate batch price calculation requests"""
    requests = []
    for _ in range(count):
        channel = fake.random_element(SAMPLE_CHANNELS)
        product = fake.random_element(SAMPLE_PRODUCTS)
        requests.append({
            "product_id": product["id"],
            "channel_id": channel["id"],
            "base_price": float(product["base_price"])
        })
    return requests


def generate_saleor_graphql_response(channels: List[Dict] = None) -> Dict[str, Any]:
    """Generate mock Saleor GraphQL API response"""
    if channels is None:
        channels = SAMPLE_CHANNELS
    
    return {
        "data": {
            "channels": channels
        },
        "extensions": {
            "cost": {
                "requestedQueryCost": 1,
                "maximumAvailable": 50000
            }
        }
    }


def generate_saleor_error_response(error_message: str = "Permission denied") -> Dict[str, Any]:
    """Generate mock Saleor GraphQL error response"""
    return {
        "errors": [
            {
                "message": error_message,
                "locations": [{"line": 1, "column": 1}],
                "path": ["channels"],
                "extensions": {
                    "exception": {
                        "code": "PermissionDenied"
                    }
                }
            }
        ],
        "data": {"channels": None}
    }