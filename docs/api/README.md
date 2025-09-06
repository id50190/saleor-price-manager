# Saleor Price Manager API Documentation

This directory contains the OpenAPI specification and documentation for the Saleor Price Manager service.

## Files Structure

- `saleor-price-manager.yaml` - Complete OpenAPI 3.1 specification with detailed documentation
- `current-openapi.json` - Auto-generated JSON schema from FastAPI (initial version)
- `updated-openapi.json` - Auto-generated JSON schema from FastAPI (with improvements)

## API Overview

The Saleor Price Manager is a FastAPI service that provides:

- **Multi-channel pricing management** with percentage-based markups
- **Real-time price calculations** via REST API
- **Saleor webhook integration** for automated updates
- **Redis caching** for performance optimization

## Quick Start

### 1. View Interactive Documentation

```bash
# Start the service
uvicorn main:app --host 0.0.0.0 --port 8000

# Open Swagger UI
open http://localhost:8000/docs

# Or ReDoc
open http://localhost:8000/redoc
```

### 2. API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/health` | GET | Service health check | No |
| `/api/channels/` | GET | List all channels with markups | Yes |
| `/api/channels/markup` | POST | Set channel markup percentage | Yes |
| `/api/prices/calculate` | POST | Calculate single product price | Yes |
| `/api/prices/batch-calculate` | POST | Batch calculate multiple prices | Yes |
| `/webhooks/product-updated` | POST | Handle Saleor product updates | No |
| `/webhooks/channel-created` | POST | Handle Saleor channel creation | No |

### 3. Authentication

Most endpoints require Bearer token authentication:

```bash
curl -H "Authorization: Bearer YOUR_SALEOR_APP_TOKEN" \
     http://localhost:8000/api/channels/
```

### 4. Example Usage

#### Set Channel Markup

```bash
curl -X POST http://localhost:8000/api/channels/markup \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "channel_id": "Q2hhbm5lbDox",
    "markup_percent": 15.5
  }'
```

#### Calculate Price

```bash
curl -X POST http://localhost:8000/api/prices/calculate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "product_id": "UHJvZHVjdDox",
    "channel_id": "Q2hhbm5lbDox",
    "base_price": 100.00
  }'
```

## OpenAPI Specification Features

### Enhanced Documentation

Our OpenAPI spec includes:

- **Detailed descriptions** for all endpoints and parameters
- **Request/response examples** with realistic data
- **Error response documentation** with status codes
- **Authentication requirements** clearly marked
- **Background task explanations** for webhook processing

### Schema Validation

- **Pydantic models** with validation rules
- **Field descriptions** and examples
- **Type safety** with proper OpenAPI 3.1 types
- **Decimal precision** for financial calculations

### Integration Examples

- **Curl commands** for testing
- **Webhook payload examples** from Saleor
- **Multi-channel scenarios** with different markups
- **Batch processing** examples

## Development Workflow

### Updating API Documentation

1. **Modify FastAPI endpoints** with enhanced docstrings and response models
2. **Update Pydantic models** with Field descriptions and examples
3. **Test changes** by running the server and checking `/docs`
4. **Export updated spec**: `curl http://localhost:8000/api/v1/openapi.json > updated-spec.json`
5. **Commit changes** to version control

### Validation Tools

```bash
# Install OpenAPI tools
npm install -g @apidevtools/swagger-cli

# Validate specification
swagger-cli validate docs/api/saleor-price-manager.yaml

# Generate documentation
swagger-cli bundle docs/api/saleor-price-manager.yaml --outfile bundled-spec.json
```

## Best Practices

### 1. Keep Documentation Current
- Update docstrings when changing endpoint behavior
- Include realistic examples in schema definitions
- Document error conditions and status codes

### 2. Version Management
- Use semantic versioning for API changes
- Maintain backward compatibility when possible
- Document breaking changes in release notes

### 3. Security Documentation
- Clearly mark authenticated vs public endpoints
- Document token requirements and scopes
- Explain webhook signature validation

### 4. Performance Notes
- Document caching behavior
- Explain background task processing
- Include rate limiting information

## Integration with External Tools

### Postman Collection
Generate a Postman collection from the OpenAPI spec:
```bash
postman-collection-generator -s docs/api/saleor-price-manager.yaml -o saleor-price-manager.postman.json
```

### Client SDK Generation
Generate client libraries using OpenAPI Generator:
```bash
npx @openapitools/openapi-generator-cli generate \
  -i docs/api/saleor-price-manager.yaml \
  -g python \
  -o client-sdk/python
```

### Testing Tools
Use OpenAPI spec for automated API testing:
```bash
# Install schemathesis for property-based testing
pip install schemathesis

# Run API tests
schemathesis run http://localhost:8000/api/v1/openapi.json
```

---

## Related Documentation

- [Project README](../../README.md) - General project information
- [AI Instructions](../../AI.md) - Development guidelines
- [Deployment Guide](../../DEPLOY) - Deployment instructions
