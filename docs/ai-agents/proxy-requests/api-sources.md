# API Source Proxy Requests

API sources allow your AI agents to query data from RESTful APIs and SaaS platforms in real-time using Airbyte as a proxy. This enables on-demand data access without running full syncs.

## Overview

API source proxy requests are ideal for:
- Real-time customer data queries (CRM, e-commerce)
- On-demand analytics and metrics
- Dynamic content retrieval
- Event-driven data access

## Supported API Sources

The following API sources support proxy requests. Each connector must be configured in your workspace before making proxy requests.

### E-Commerce Platforms

#### Shopify
**Use Case:** Query orders, customers, products, and inventory in real-time

**Authentication:** OAuth 2.0 or API Password

**Available Streams:**
- `orders` - Customer orders and order details
- `customers` - Customer information
- `products` - Product catalog
- `inventory_levels` - Real-time inventory
- `abandoned_checkouts` - Cart abandonment data

**Configuration Example:**
```json
{
  "workspaceId": "workspace_123",
  "name": "My Shopify Store",
  "sourceDefinitionId": "9da77001-af33-4bcd-be46-6252bf9342b9",
  "configuration": {
    "shop": "mystore.myshopify.com",
    "credentials": {
      "auth_method": "api_password",
      "api_password": "shppa_xxxxxxxxxxxx"
    },
    "start_date": "2024-01-01"
  }
}
```

**Proxy Request Example:**
```bash
curl -X POST https://api.airbyte.com/v1/proxy/sources/{sourceId}/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "stream": "orders",
    "filters": {
      "status": "fulfilled",
      "financial_status": "paid",
      "limit": 20
    }
  }'
```

**Python Example:**
```python
def get_recent_orders(source_id, status="fulfilled", limit=10):
    """Fetch recent Shopify orders."""
    response = requests.post(
        f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json={
            "stream": "orders",
            "filters": {
                "status": status,
                "limit": limit,
                "order": "created_at desc"
            }
        }
    )
    return response.json()
```

---

### CRM Platforms

#### Salesforce
**Use Case:** Query contacts, leads, opportunities, and custom objects

**Authentication:** OAuth 2.0

**Available Streams:**
- `Account` - Account records
- `Contact` - Contact information
- `Lead` - Lead records
- `Opportunity` - Sales opportunities
- `Case` - Support cases
- Custom objects (e.g., `CustomObject__c`)

**Configuration Example:**
```json
{
  "workspaceId": "workspace_123",
  "name": "Salesforce CRM",
  "sourceDefinitionId": "b117307c-14b6-41aa-9422-947e34922962",
  "configuration": {
    "auth_type": "Client",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "refresh_token": "YOUR_REFRESH_TOKEN",
    "is_sandbox": false
  }
}
```

**Proxy Request Example:**
```python
def search_contacts(source_id, email_domain):
    """Search Salesforce contacts by email domain."""
    return requests.post(
        f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json={
            "stream": "Contact",
            "filters": {
                "where": f"Email LIKE '%@{email_domain}%'",
                "limit": 50
            }
        }
    ).json()
```

---

#### HubSpot
**Use Case:** Marketing automation, contacts, deals, and engagement data

**Authentication:** OAuth 2.0 or API Key

**Available Streams:**
- `contacts` - Contact records
- `companies` - Company information
- `deals` - Deal pipeline data
- `tickets` - Support tickets
- `email_events` - Email engagement metrics

**Configuration Example:**
```json
{
  "workspaceId": "workspace_123",
  "name": "HubSpot Marketing",
  "sourceDefinitionId": "36c891d9-4bd9-43ac-bad2-10e12756272c",
  "configuration": {
    "credentials": {
      "credentials_title": "OAuth Credentials",
      "client_id": "YOUR_CLIENT_ID",
      "client_secret": "YOUR_CLIENT_SECRET",
      "refresh_token": "YOUR_REFRESH_TOKEN"
    },
    "start_date": "2024-01-01T00:00:00Z"
  }
}
```

**Proxy Request Example:**
```javascript
async function getRecentDeals(sourceId, stage) {
  const response = await fetch(
    `https://api.airbyte.com/v1/proxy/sources/${sourceId}/query`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${ACCESS_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        stream: 'deals',
        filters: {
          dealstage: stage,
          limit: 25,
          sort: 'createdate:desc'
        }
      })
    }
  );
  return await response.json();
}
```

---

### Payment Platforms

#### Stripe
**Use Case:** Payment data, customer billing, subscriptions

**Authentication:** API Key

**Available Streams:**
- `charges` - Payment charges
- `customers` - Customer records
- `subscriptions` - Subscription data
- `invoices` - Invoice records
- `payment_intents` - Payment intents
- `refunds` - Refund records

**Configuration Example:**
```json
{
  "workspaceId": "workspace_123",
  "name": "Stripe Payments",
  "sourceDefinitionId": "e094cb9a-26de-4645-8761-65c0c425d1de",
  "configuration": {
    "account_id": "acct_xxxxxxxxxxxxxxxx",
    "client_secret": "sk_live_xxxxxxxxxxxxxxxx",
    "start_date": "2024-01-01T00:00:00Z"
  }
}
```

**Proxy Request Example:**
```python
def get_customer_charges(source_id, customer_id):
    """Get all charges for a specific customer."""
    response = requests.post(
        f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json={
            "stream": "charges",
            "filters": {
                "customer": customer_id,
                "limit": 100
            }
        }
    )
    return response.json()
```

---

### Analytics Platforms

#### Google Analytics 4
**Use Case:** Website traffic, user behavior, conversion metrics

**Authentication:** OAuth 2.0 or Service Account

**Available Streams:**
- `website_overview` - Traffic overview
- `traffic_sources` - Traffic source breakdown
- `pages` - Page views and engagement
- `events` - Custom event tracking
- `conversions` - Conversion data

**Configuration Example:**
```json
{
  "workspaceId": "workspace_123",
  "name": "Website Analytics",
  "sourceDefinitionId": "3cc2eafd-84aa-4dca-93af-322d9dfeec1a",
  "configuration": {
    "property_id": "123456789",
    "credentials": {
      "auth_type": "Service",
      "credentials_json": "{\"type\":\"service_account\",...}"
    },
    "date_ranges_start_date": "2024-01-01"
  }
}
```

**Proxy Request Example:**
```python
def get_page_views(source_id, page_path, start_date, end_date):
    """Get page views for a specific page."""
    return requests.post(
        f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json={
            "stream": "pages",
            "filters": {
                "page_path": page_path,
                "start_date": start_date,
                "end_date": end_date
            }
        }
    ).json()
```

---

### Databases

#### PostgreSQL
**Use Case:** Query custom application databases

**Authentication:** Username/Password, SSL options

**Available Streams:**
- Any table in the configured database
- Custom SQL queries (read-only)

**Configuration Example:**
```json
{
  "workspaceId": "workspace_123",
  "name": "Application Database",
  "sourceDefinitionId": "decd338e-5647-4c0b-adf4-da0e75f5a750",
  "configuration": {
    "host": "db.example.com",
    "port": 5432,
    "database": "production",
    "schemas": ["public"],
    "username": "readonly_user",
    "password": "secure_password",
    "ssl_mode": {
      "mode": "require"
    }
  }
}
```

**Proxy Request Example:**
```python
def query_users(source_id, email):
    """Query users table by email."""
    return requests.post(
        f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json={
            "stream": "public.users",
            "filters": {
                "where": f"email = '{email}'",
                "limit": 1
            }
        }
    ).json()
```

---

## Common Patterns

### Pattern 1: Real-Time Customer Lookup

Query customer data across multiple sources:

```python
def lookup_customer(email):
    """Look up customer across CRM and e-commerce."""

    # Search Salesforce
    sf_contacts = search_contacts(
        source_id="sf_source_id",
        email_domain=email.split('@')[1]
    )

    # Search Shopify
    shopify_customers = requests.post(
        f"https://api.airbyte.com/v1/proxy/sources/shopify_source_id/query",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json={
            "stream": "customers",
            "filters": {"email": email}
        }
    ).json()

    return {
        "crm_data": sf_contacts,
        "ecommerce_data": shopify_customers
    }
```

### Pattern 2: Multi-Source Aggregation

Combine data from multiple sources:

```python
def get_customer_360(customer_email):
    """Build 360-degree customer view."""

    # Get CRM data
    crm_data = query_hubspot_contact(customer_email)

    # Get payment history
    stripe_data = query_stripe_customer(customer_email)

    # Get support tickets
    support_data = query_zendesk_tickets(customer_email)

    return {
        "contact": crm_data,
        "payments": stripe_data,
        "support": support_data
    }
```

### Pattern 3: Conditional Data Fetching

Fetch data based on conditions:

```python
def get_high_value_customers(source_id, min_total_spent=10000):
    """Get customers who spent more than threshold."""

    all_customers = []
    page_token = None

    while True:
        payload = {
            "stream": "customers",
            "filters": {
                "total_spent": {"$gte": min_total_spent},
                "limit": 100
            }
        }

        if page_token:
            payload["page_token"] = page_token

        response = requests.post(
            f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            json=payload
        ).json()

        all_customers.extend(response["records"])

        page_token = response.get("next_page_token")
        if not page_token:
            break

    return all_customers
```

## Authentication Best Practices

### OAuth 2.0 Sources
For sources using OAuth (Shopify, Salesforce, HubSpot, GA4):

1. **Token Refresh**
   - Implement automatic token refresh logic
   - Store refresh tokens securely
   - Handle token expiration gracefully

2. **Scope Management**
   - Request only necessary scopes
   - Document required permissions
   - Handle insufficient scope errors

```python
def refresh_oauth_token(refresh_token, client_id, client_secret):
    """Refresh expired OAuth token."""
    response = requests.post(
        "https://oauth.provider.com/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret
        }
    )
    return response.json()["access_token"]
```

### API Key Sources
For API key-based sources (Stripe):

1. **Key Rotation**
   - Rotate keys regularly
   - Update Airbyte configuration when keys change
   - Monitor for compromised keys

2. **Environment-Specific Keys**
   - Use test keys in development
   - Separate keys per environment
   - Never commit keys to version control

## Rate Limiting

Different sources have different rate limits:

| Source | Rate Limit | Window |
|--------|-----------|--------|
| Shopify | 2 requests/second | Per store |
| Salesforce | 15,000 requests/day | Per org |
| HubSpot | 100 requests/10 seconds | Per app |
| Stripe | 100 requests/second | Per account |
| Google Analytics | 10 requests/second | Per property |

### Handling Rate Limits

```python
import time
from functools import wraps

def rate_limit_handler(max_retries=3):
    """Decorator to handle rate limiting."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        retry_after = int(e.response.headers.get('Retry-After', 2 ** attempt))
                        print(f"Rate limited. Waiting {retry_after}s...")
                        time.sleep(retry_after)
                    else:
                        raise
            raise Exception("Max retries exceeded")
        return wrapper
    return decorator

@rate_limit_handler(max_retries=5)
def query_source(source_id, stream, filters):
    """Query source with rate limit handling."""
    response = requests.post(
        f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json={"stream": stream, "filters": filters}
    )
    response.raise_for_status()
    return response.json()
```

## Error Handling

### Common Errors

```python
class ProxyRequestError(Exception):
    """Base exception for proxy request errors."""
    pass

class AuthenticationError(ProxyRequestError):
    """Source authentication failed."""
    pass

class RateLimitError(ProxyRequestError):
    """Rate limit exceeded."""
    pass

class SourceUnavailableError(ProxyRequestError):
    """Source API is unavailable."""
    pass

def safe_query(source_id, stream, filters):
    """Query with comprehensive error handling."""
    try:
        response = requests.post(
            f"https://api.airbyte.com/v1/proxy/sources/{source_id}/query",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            json={"stream": stream, "filters": filters},
            timeout=30
        )

        if response.status_code == 401:
            raise AuthenticationError("Invalid access token")
        elif response.status_code == 403:
            raise AuthenticationError("Source credentials invalid")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        elif response.status_code >= 500:
            raise SourceUnavailableError("Source API unavailable")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        raise ProxyRequestError("Request timeout")
    except requests.exceptions.ConnectionError:
        raise ProxyRequestError("Connection failed")
```

## Performance Optimization

### Caching

Implement caching for frequently accessed data:

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Simple in-memory cache with TTL
_cache = {}

def cached_query(source_id, stream, filters, ttl_seconds=300):
    """Query with caching."""
    cache_key = f"{source_id}:{stream}:{str(filters)}"

    # Check cache
    if cache_key in _cache:
        cached_data, cached_time = _cache[cache_key]
        if datetime.now() - cached_time < timedelta(seconds=ttl_seconds):
            return cached_data

    # Fetch fresh data
    data = query_source(source_id, stream, filters)

    # Update cache
    _cache[cache_key] = (data, datetime.now())

    return data
```

### Batch Requests

Minimize requests by batching when possible:

```python
def batch_query(source_id, queries):
    """Execute multiple queries in batch."""
    results = []

    for query in queries:
        try:
            result = query_source(
                source_id,
                query["stream"],
                query["filters"]
            )
            results.append({"status": "success", "data": result})
        except Exception as e:
            results.append({"status": "error", "error": str(e)})

    return results
```

## Testing

### Unit Testing Proxy Requests

```python
import unittest
from unittest.mock import patch, Mock

class TestProxyRequests(unittest.TestCase):

    @patch('requests.post')
    def test_successful_query(self, mock_post):
        """Test successful proxy request."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "records": [{"id": 1, "name": "Test"}]
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = query_source("src_123", "customers", {})

        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["records"][0]["name"], "Test")

    @patch('requests.post')
    def test_rate_limit_error(self, mock_post):
        """Test rate limit handling."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_post.return_value = mock_response

        with self.assertRaises(RateLimitError):
            safe_query("src_123", "customers", {})
```

## Next Steps

- **[File Storage Sources](./file-storage-sources.md)** - Learn about file storage proxying
- **[Quickstart Guide](../quickstart.md)** - Build your first integration
- **[Authentication](../embedded/api/authentication.md)** - Set up secure authentication

## Additional Resources

- [Airbyte Connector Catalog](https://docs.airbyte.com/integrations)
- [API Reference](https://reference.airbyte.com)
- [Shopify Connector Documentation](https://docs.airbyte.com/integrations/sources/shopify)
- [Salesforce Connector Documentation](https://docs.airbyte.com/integrations/sources/salesforce)
- [HubSpot Connector Documentation](https://docs.airbyte.com/integrations/sources/hubspot)
