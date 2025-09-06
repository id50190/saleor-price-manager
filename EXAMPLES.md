# 📚 Saleor Price Manager - Usage Examples

## 🚀 Getting Started

### Start the Full Application
```bash
# 1. Deploy and setup
./DEPLOY

# 2. Start both backend + frontend
./BANG

# 3. Open in browser
open http://localhost:3000  # 🌐 Frontend UI
open http://localhost:8000/docs  # 📊 API Documentation

# 4. Verify backend is running
curl http://localhost:8000/health
# {"status":"ok"}
```

### Alternative: Start Components Separately
```bash
# Terminal 1: Backend only
./BANG_BACKEND_ONLY

# Terminal 2: Frontend only 
./START_FRONTEND
```

---

## 🎆 Demo Mode Examples

> 💡 **No Saleor token needed!** All examples work immediately in demo mode.

### List Available Channels
```bash
curl -s http://localhost:8000/api/channels/ | jq .
```

**Response:**
```json
[
  {
    "id": "Q2hhbm5lbDox",
    "name": "Default Channel", 
    "slug": "default-channel",
    "markup_percent": "0"
  },
  {
    "id": "Q2hhbm5lbDoy",
    "name": "Moscow Store",
    "slug": "moscow", 
    "markup_percent": "15"
  },
  {
    "id": "Q2hhbm5lbDoz",
    "name": "SPb Store",
    "slug": "spb",
    "markup_percent": "10" 
  }
]
```

### Calculate Product Price with Markup
```bash
curl -X POST http://localhost:8000/api/prices/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "UHJvZHVjdDox",
    "channel_id": "Q2hhbm5lbDoy",
    "base_price": 100.00
  }'
```

**Response:**
```json
{
  "product_id": "UHJvZHVjdDox",
  "channel_id": "Q2hhbm5lbDoy", 
  "base_price": "100.0",
  "markup_percent": "15",
  "final_price": "115.00",
  "currency": "USD"
}
```

### Set New Markup for Channel
```bash
curl -X POST http://localhost:8000/api/channels/markup \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "Q2hhbm5lbDox",
    "markup_percent": 25.0
  }'
```

**Response:**
```json
{
  "success": true,
  "markup": {
    "channel_id": "Q2hhbm5lbDox",
    "markup_percent": 25.0
  }
}
```

---

## 🔄 Batch Operations

### Calculate Prices for Multiple Products
```bash
curl -X POST http://localhost:8000/api/prices/batch-calculate \
  -H "Content-Type: application/json" \
  -d '[
    {
      "product_id": "UHJvZHVjdDox",
      "channel_id": "Q2hhbm5lbDoy",
      "base_price": 100.00
    },
    {
      "product_id": "UHJvZHVjdDoy",
      "channel_id": "Q2hhbm5lbDoz", 
      "base_price": 50.00
    }
  ]'
```

**Response:**
```json
[
  {
    "product_id": "UHJvZHVjdDox",
    "base_price": "100.0",
    "markup_percent": "15",
    "final_price": "115.00"
  },
  {
    "product_id": "UHJvZHVjdDoy", 
    "base_price": "50.0",
    "markup_percent": "10",
    "final_price": "55.00"
  }
]
```

---

## 🌐 Real Saleor Integration

### 1. Configure Your Saleor Instance
```bash
# Edit .env file
vim .env
```

```env
# Replace with your actual Saleor Cloud instance
SALEOR_API_URL=https://your-store.eu.saleor.cloud/graphql/
SALEOR_APP_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
CORS_ORIGINS='["https://your-store.eu.saleor.cloud"]'
```

### 2. Test Real Connection
```bash
# Restart application with real credentials
./BANG

# Test connection with authorization
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/channels/
```

---

## 🔌 Webhook Integration

### Simulate Saleor Webhooks

**Product Updated:**
```bash
curl -X POST http://localhost:8000/webhooks/product-updated \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "PRODUCT_UPDATED",
    "product_id": "UHJvZHVjdDox",
    "data": {
      "product": {
        "id": "UHJvZHVjdDox",
        "name": "Sample Product"
      }
    }
  }'
```

**Channel Created:**
```bash
curl -X POST http://localhost:8000/webhooks/channel-created \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "CHANNEL_CREATED",
    "channel_id": "Q2hhbm5lbDo0",
    "data": {
      "channel": {
        "id": "Q2hhbm5lbDo0",
        "name": "New Store",
        "slug": "new-store"
      }
    }
  }'
```

---

## 📊 Interactive Documentation & UI

### 🌐 Frontend Interface
```bash
# Visual channel management interface:
open http://localhost:3000
```

**Frontend Features:**
- ✅ **Visual Channel Management** - See all channels at a glance
- ✅ **Interactive Markup Editor** - Update markups with instant feedback
- ✅ **Price Calculator** - Test calculations in real-time
- ✅ **Demo Data** - 3 sample channels ready to use
- ✅ **API Integration** - Direct connection to FastAPI backend

### 📊 API Documentation
```bash
# Swagger UI - Interactive API testing:
open http://localhost:8000/docs

# ReDoc - Beautiful API documentation:
open http://localhost:8000/redoc
```

**API Features:**
- ✅ Try all endpoints interactively
- ✅ See request/response examples
- ✅ Test with different parameters
- ✅ Download OpenAPI specification

---

## 🔍 Testing & Debugging

### Health Check
```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### Check Application Logs
```bash
# Run with verbose logging
DEBUG=true ./BANG

# Or check logs in background mode
tail -f /var/log/saleor-price-manager.log
```

### Test Rust Module Performance
```bash
# Test the Rust price calculator directly
python3 -c "
import price_calculator
result = price_calculator.calculate_price('100.00', '15.0')
print(f'Rust calculation: ${result}')
"
```

---

## 🤖 Advanced Usage

### Custom Markup Rules
```python
# Example: Dynamic markup based on product category
# This would be implemented as a custom service

def calculate_dynamic_markup(product_id, channel_id, base_price):
    # Custom business logic here
    if is_luxury_product(product_id):
        return base_price * 1.30  # 30% markup
    elif is_sale_item(product_id):
        return base_price * 0.90  # 10% discount
    else:
        return base_price * 1.15  # Default 15% markup
```

### Integration with External Systems
```bash
# Example: Sync prices with external inventory system
curl -X POST http://localhost:8000/api/prices/batch-calculate \
  -H "Content-Type: application/json" \
  -d "$(cat inventory-export.json)" \
  | jq '.[] | {sku: .product_id, price: .final_price}' \
  > updated-prices.json
```

### Monitoring Setup
```bash
# Health check with monitoring
watch -n 10 'curl -s http://localhost:8000/health | jq .'

# Performance monitoring
curl 'http://localhost:8000/health?set-process-time=true' \
  -w "Response time: %{time_total}s\n"
```

---

## 💰 Pricing Examples by Channel

| Product | Base Price | Channel | Markup | Final Price |
|---------|------------|---------|--------|--------------|
| T-Shirt | $20.00 | Default | 0% | $20.00 |
| T-Shirt | $20.00 | Moscow | 15% | $23.00 |
| T-Shirt | $20.00 | SPb | 10% | $22.00 |
| Jeans | $80.00 | Moscow | 15% | $92.00 |
| Shoes | $150.00 | SPb | 10% | $165.00 |

**Bulk calculation for catalog:**
```bash
# Calculate prices for entire product catalog
curl -X POST http://localhost:8000/api/prices/batch-calculate \
  -H "Content-Type: application/json" \
  -d '[
    {"product_id": "tshirt_001", "channel_id": "moscow", "base_price": 20.00},
    {"product_id": "jeans_001", "channel_id": "moscow", "base_price": 80.00},
    {"product_id": "shoes_001", "channel_id": "spb", "base_price": 150.00}
  ]' | jq '.[] | "\(.product_id): $\(.final_price)"'
```

---

**🎆 Ready to integrate with your Saleor store!** 

For more examples, check the [API Documentation](docs/api/README.md) or try the interactive Swagger UI at http://localhost:8000/docs