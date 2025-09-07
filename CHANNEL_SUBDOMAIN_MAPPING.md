# Channel Subdomain Mapping

## Overview

Saleor Price Manager supports multiple subdomains per channel through metadata configuration. This allows you to route different subdomains to the same pricing channel with specific markups.

## Configuration

### In Saleor Dashboard

Add metadata to your channels:

1. **Single subdomain**: 
   - Key: `subdomain`
   - Value: `moscow`

2. **Multiple subdomains**:
   - Key: `subdomains` 
   - Value: `moscow,msk,ru-moscow`

3. **Markup configuration**:
   - Key: `price_markup_percent`
   - Value: `15` (for 15% markup)

### Example Channel Setup

```json
{
  "id": "Q2hhbm5lbDoy",
  "name": "Moscow Store",
  "slug": "moscow", 
  "metadata": [
    {
      "key": "price_markup_percent",
      "value": "15"
    },
    {
      "key": "subdomains", 
      "value": "moscow,msk,ru-moscow"
    }
  ]
}
```

## API Usage

### Get channel by subdomain

```bash
# Any of these subdomains will return the Moscow Store channel
curl "http://localhost:8000/api/channels/?subdomain=moscow"
curl "http://localhost:8000/api/channels/?subdomain=msk" 
curl "http://localhost:8000/api/channels/?subdomain=ru-moscow"
```

### Frontend Integration

The frontend automatically loads all available subdomains from the API and displays them in a dropdown selector with appropriate icons and channel names.

## Fallback Mechanism

- If no token configured → uses demo channels
- If API unavailable → falls back to demo channels  
- If no subdomain match → tries to match by channel slug
- If no metadata → adds default `price_markup_percent: "0"`

## Real Saleor Integration

Set your Saleor API URL in `.env`:

```env
SALEOR_API_URL=https://your-store.eu.saleor.cloud/graphql/
SALEOR_APP_TOKEN=your_app_token_here
```

The system will automatically use real channels from your Saleor instance.
