---
products: embedded
---

# Authentication

Airbyte Embedded uses OAuth 2.0 Bearer tokens for API authentication. This guide explains the different token types, how to generate them, and best practices for secure implementation.

## Token Types

Airbyte Embedded uses three types of tokens, each with different permission levels:

### 1. Access Token (Organization-Level)

**Purpose:** Full administrative access to your organization

**Permissions:**
- Create and manage source templates
- Create and manage connection templates
- Generate scoped tokens for customers
- Access all workspaces in your organization
- Manage organization settings

**Lifetime:** Long-lived (does not expire automatically)

**When to Use:**
- Backend server operations
- Template management
- Administrative tasks
- Generating scoped tokens

**Security:**
- 🔐 **Never** expose to end-users
- 🔐 **Never** include in frontend code
- 🔐 **Never** commit to version control
- ✅ **Store** securely in environment variables
- ✅ **Use** only in trusted backend services

**How to Get:**
1. Log in to [cloud.airbyte.com](https://cloud.airbyte.com)
2. Navigate to Settings → Applications
3. Create or copy your API credentials
4. Store the access token securely

### 2. Scoped Token (User-Level)

**Purpose:** Limited access for individual end-users

**Permissions:**
- Configure sources in a single workspace
- View source configuration
- Check connection status
- Limited to one workspace (specified by external_id)

**Lifetime:** Short-lived (typically 1-24 hours, configurable)

**When to Use:**
- Embedded widget authentication
- Customer-facing operations
- Frontend applications
- Mobile applications

**Security:**
- ✅ **Safe** to use in frontend code
- ✅ **Safe** to pass to end-users
- ✅ **Automatically expires**
- ⚠️ **Limited** to one workspace only

**How to Generate:**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/embedded/scoped-token' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "external_id": "customer-123",
    "selected_source_template_tags": ["production"],
    "selected_connection_template_tags": ["production"]
  }'
```

**Response:**
```json
{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2024-10-10T19:00:00Z",
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 3. Widget Token

**Purpose:** Specialized token for the Embedded Widget UI component

**Permissions:**
- Display widget UI
- Configure sources through widget
- All permissions of a scoped token

**Lifetime:** Short-lived (matches scoped token lifetime)

**When to Use:**
- When embedding the Airbyte Widget in your app
- For visual source configuration UIs

**How to Generate:**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/embedded/widget-token' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "external_id": "customer-123",
    "selected_source_template_tags": ["production"],
    "selected_connection_template_tags": ["production"]
  }'
```

## Authentication Flow

### Backend-to-Backend Authentication

For server-to-server API calls:

```
Your Backend                          Airbyte API
     |                                     |
     |  POST /api/v1/integrations/...     |
     |  Authorization: Bearer ACCESS_TOKEN |
     |------------------------------------>|
     |                                     |
     |         200 OK + Response           |
     |<------------------------------------|
```

**Example:**
```bash
curl -X GET 'https://api.airbyte.ai/api/v1/embedded/source-templates' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

### Customer-Facing Authentication

For end-user operations:

```
Your Backend          Your Frontend          Airbyte API
     |                      |                      |
     | 1. Request token     |                      |
     |<---------------------|                      |
     |                      |                      |
     | 2. Generate scoped   |                      |
     |    token with        |                      |
     |    ACCESS_TOKEN      |                      |
     |------------------------------------>|
     |                      |                      |
     |    Scoped Token      |                      |
     |<------------------------------------|
     |                      |                      |
     | 3. Return token      |                      |
     |--------------------->|                      |
     |                      |                      |
     |                      | 4. API calls with    |
     |                      |    scoped token      |
     |                      |--------------------->|
     |                      |                      |
     |                      |    Response          |
     |                      |<---------------------|
```

## Implementation Examples

### Backend Token Management (Node.js)

```javascript
// Store access token securely
const AIRBYTE_ACCESS_TOKEN = process.env.AIRBYTE_ACCESS_TOKEN;

// Generate scoped token for customer
async function generateCustomerToken(customerId) {
  const response = await fetch(
    'https://api.airbyte.ai/api/v1/embedded/scoped-token',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${AIRBYTE_ACCESS_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        external_id: customerId,
        selected_source_template_tags: ['production'],
        selected_connection_template_tags: ['production'],
      }),
    }
  );

  const data = await response.json();
  return {
    token: data.token,
    expiresAt: data.expires_at,
    workspaceId: data.workspace_id,
  };
}
```

### Frontend Token Usage (React)

```javascript
// In your React component
function SourceConfiguration({ customerId }) {
  const [scopedToken, setScopedToken] = useState(null);

  useEffect(() => {
    // Call your backend to get scoped token
    fetch(`/api/customer/${customerId}/airbyte-token`)
      .then(res => res.json())
      .then(data => setScopedToken(data.token));
  }, [customerId]);

  if (!scopedToken) return <div>Loading...</div>;

  // Use scoped token for API calls
  return (
    <ConfigureSource
      airbyteToken={scopedToken}
      customerId={customerId}
    />
  );
}
```

### Token Caching and Refresh

```javascript
class TokenManager {
  constructor(accessToken) {
    this.accessToken = accessToken;
    this.tokenCache = new Map();
  }

  async getScopedToken(customerId) {
    // Check cache
    const cached = this.tokenCache.get(customerId);
    if (cached && new Date(cached.expiresAt) > new Date()) {
      return cached.token;
    }

    // Generate new token
    const response = await fetch(
      'https://api.airbyte.ai/api/v1/embedded/scoped-token',
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          external_id: customerId,
          selected_source_template_tags: ['production'],
          selected_connection_template_tags: ['production'],
        }),
      }
    );

    const data = await response.json();

    // Cache the token
    this.tokenCache.set(customerId, {
      token: data.token,
      expiresAt: data.expires_at,
    });

    return data.token;
  }

  clearExpiredTokens() {
    const now = new Date();
    for (const [customerId, cached] of this.tokenCache.entries()) {
      if (new Date(cached.expiresAt) <= now) {
        this.tokenCache.delete(customerId);
      }
    }
  }
}
```

## Security Best Practices

### Token Storage

**Access Tokens (Organization-Level):**
- ✅ Store in environment variables
- ✅ Use secrets management (AWS Secrets Manager, HashiCorp Vault)
- ✅ Rotate periodically
- ❌ Never commit to Git
- ❌ Never log in plaintext
- ❌ Never expose to frontend

**Scoped Tokens (User-Level):**
- ✅ Generate on-demand
- ✅ Let them expire naturally
- ✅ Safe to pass to frontend
- ⚠️ Still avoid logging if possible
- ⚠️ Implement rate limiting for token generation

### API Call Security

```javascript
// ✅ Good: Backend generates scoped token
app.post('/api/customer/:id/token', async (req, res) => {
  const scopedToken = await generateScopedToken(req.params.id);
  res.json({ token: scopedToken });
});

// ❌ Bad: Exposing access token to frontend
app.get('/api/config', (req, res) => {
  res.json({
    airbyteToken: process.env.AIRBYTE_ACCESS_TOKEN // NEVER DO THIS!
  });
});
```

### Rate Limiting

Implement rate limiting for scoped token generation:

```javascript
const rateLimit = require('express-rate-limit');

const tokenLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each customer to 100 token requests per window
  keyGenerator: (req) => req.params.customerId,
  message: 'Too many token requests, please try again later.',
});

app.post('/api/customer/:customerId/token',
  tokenLimiter,
  generateTokenHandler
);
```

### Token Validation

Always validate tokens before use:

```javascript
async function validateScopedToken(token) {
  try {
    const response = await fetch(
      'https://api.airbyte.ai/api/v1/embedded/scoped-token/info',
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error('Invalid token');
    }

    const info = await response.json();
    return {
      isValid: true,
      workspaceId: info.workspace_id,
      expiresAt: info.expires_at,
    };
  } catch (error) {
    return { isValid: false };
  }
}
```

## Troubleshooting

### "Unauthorized" (401) Errors

**Possible causes:**
1. Token is expired
2. Token is invalid or malformed
3. Token type doesn't match required permissions
4. Token was revoked

**Solutions:**
- Check token expiration timestamp
- Verify you're using the correct token type
- Generate a new token
- Ensure Bearer token format: `Authorization: Bearer <token>`

### "Forbidden" (403) Errors

**Possible causes:**
1. Scoped token trying to access different workspace
2. Insufficient permissions for operation
3. Resource doesn't exist in the workspace

**Solutions:**
- Verify external_id matches the target workspace
- Check if operation is allowed with scoped token
- Use access token for administrative operations
- Ensure resource exists before accessing

### Token Expiration Handling

```javascript
async function makeAuthenticatedRequest(url, scopedToken, customerId) {
  let response = await fetch(url, {
    headers: { 'Authorization': `Bearer ${scopedToken}` }
  });

  // If token expired, get new one and retry
  if (response.status === 401) {
    const newToken = await generateScopedToken(customerId);
    response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${newToken}` }
    });
  }

  return response;
}
```

## API Reference

For complete authentication API documentation:
- [Scoped Token Generation](https://api.airbyte.ai/api/v1/docs#/Embedded/post_api_v1_embedded_scoped_token)
- [Widget Token Generation](https://api.airbyte.ai/api/v1/docs#/Embedded/post_api_v1_embedded_widget_token)
- [Token Info Endpoint](https://api.airbyte.ai/api/v1/docs#/Embedded/get_api_v1_embedded_scoped_token_info)

## Next Steps

- Implement [Workspace Management](./workspace-management.md)
- Configure [Source Templates](./source-templates.md)
- Set up [Connection Templates](./connection-templates.md)
- Use the [Embedded Widget](../widget/README.md)
