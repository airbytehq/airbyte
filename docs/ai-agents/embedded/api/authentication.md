# Authentication

The Airbyte Embedded API uses a hierarchical authentication system with three types of tokens, each designed for specific use cases and security requirements.

## Token Types Overview

| Token Type | Use Case | Scope | Access Level |
|------------|----------|-------|--------------|
| **Operator Bearer Token** | Organization management, template creation | Organization-wide | Full access to organization resources |
| **Scoped Token** | API integration, programmatic workspace access | Single workspace | Limited to specific workspace |
| **Widget Token** | Embedded widget integration | Single workspace + origin validation | Limited to specific workspace with CORS protection |

## Operator Bearer Token

The Operator Bearer Token provides full organization-level access and is used for administrative operations.

### Use Cases

- Creating and managing source templates
- Creating and managing connection templates
- Managing workspaces across the organization
- Generating scoped tokens and widget tokens
- Administrative API operations

### Usage

Include the operator token in the `Authorization` header:

```bash
curl https://api.airbyte.ai/api/v1/integrations/templates/sources \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json'
```

### Security Best Practices

- **Never expose operator tokens in client-side code**
- Store securely in environment variables or secrets management systems
- Use scoped tokens for end-user operations
- Rotate tokens periodically
- Limit token distribution to trusted administrators only

## Scoped Token

Scoped tokens provide workspace-level access and are designed for API integrations where end-users need to interact with a specific workspace.

### Use Cases

- API integrations for specific workspaces
- Programmatic access to workspace resources
- Backend services managing user workspaces
- Mobile applications or CLI tools

### Features

- Workspace-scoped access (cannot access other workspaces)
- Automatically creates workspace if it doesn't exist
- Region selection support (US or EU)
- Embedded in JWT with `io.airbyte.auth.workspace_scope` claim

### Generate Scoped Token

#### Endpoint

```
POST https://api.airbyte.ai/api/v1/embedded/scoped-token
```

#### Authentication

Requires **Operator Bearer Token**

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workspace_name` | string | Yes | Name of the workspace to create or use |
| `region_id` | UUID | No | Region where workspace should be created (defaults to US) |

#### Region IDs

| Region | Region ID |
|--------|-----------|
| US (Default) | `645a183f-b12b-4c6e-8ad3-99e165603450` |
| EU | `b9e48d61-f082-4a14-a8d0-799a907938cb` |

#### Request Example

**Create scoped token for US workspace:**

```bash
curl -X POST https://api.airbyte.ai/api/v1/embedded/scoped-token \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_name": "customer_workspace_123"
  }'
```

**Create scoped token for EU workspace:**

```bash
curl -X POST https://api.airbyte.ai/api/v1/embedded/scoped-token \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_name": "eu_customer_workspace",
    "region_id": "b9e48d61-f082-4a14-a8d0-799a907938cb"
  }'
```

#### Response Example

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Behavior Notes

- If the workspace already exists, returns a token for the existing workspace
- If the workspace doesn't exist:
  - Checks if a workspace with the same name exists in Airbyte Cloud
  - If found in cloud, creates local database record
  - If not found, creates new workspace in both Airbyte Cloud and local database
- The `region_id` is only used when creating a new workspace

### Using Scoped Tokens

Once generated, use scoped tokens to access workspace-specific endpoints:

```bash
# List sources in the workspace
curl https://api.airbyte.ai/api/v1/embedded/sources \
  -H 'Authorization: Bearer <scoped_token>'

# Create a source
curl -X POST https://api.airbyte.ai/api/v1/embedded/sources \
  -H 'Authorization: Bearer <scoped_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "source_template_id": "template-123",
    "name": "My Data Source"
  }'
```

### Get Scoped Token Information

Retrieve organization and workspace information from a scoped token.

#### Endpoint

```
GET https://api.airbyte.ai/api/v1/embedded/scoped-token/info
```

#### Authentication

Requires **Scoped Token**

#### Request Example

```bash
curl https://api.airbyte.ai/api/v1/embedded/scoped-token/info \
  -H 'Authorization: Bearer <scoped_token>'
```

#### Response Example

```json
{
  "organization_id": "12345678-1234-1234-1234-123456789012",
  "workspace_id": "a1b2c3d4-e5f6-7890-ab12-cd34ef567890"
}
```

#### Deprecated Endpoints

The following endpoints also return scoped token information but are deprecated:

- `GET /api/v1/embedded/scoped-token-info` (deprecated)
- `GET /api/v1/embedded/organizations/current-scoped` (deprecated)

Use `/api/v1/embedded/scoped-token/info` for new implementations.

## Widget Token

Widget tokens are specialized tokens designed for embedded widget integration with enhanced security features.

### Use Cases

- Embedding the Airbyte configuration widget in your application
- Providing end-users with a UI to configure data sources
- Multi-tenant applications with isolated workspaces

### Features

- All features of scoped tokens
- **Origin validation** for CORS protection via `allowed_origin`
- **Template filtering** via tags (both source and connection templates)
- Base64-encoded payload containing token and pre-configured widget URL
- Tag selection modes: `any` (at least one tag) or `all` (all tags required)

### Generate Widget Token

#### Endpoint

```
POST https://api.airbyte.ai/api/v1/embedded/widget-token
```

#### Authentication

Requires **Operator Bearer Token**

#### Request Body

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `workspace_name` | string | Yes | - | Name of the workspace to create or use |
| `allowed_origin` | string | Yes | - | The allowed origin for CORS (e.g., `https://yourapp.com`) |
| `region_id` | UUID | No | US region | Region where workspace should be created |
| `selected_source_template_tags` | array of strings | No | `[]` | Tags to filter which source templates are available |
| `selected_source_template_tags_mode` | string | No | `any` | Tag selection mode: `any` or `all` |
| `selected_connection_template_tags` | array of strings | No | `[]` | Tags to filter which connection templates are available |
| `selected_connection_template_tags_mode` | string | No | `any` | Tag selection mode: `any` or `all` |

#### Tag Selection Modes

| Mode | Behavior | Example |
|------|----------|---------|
| `any` | Template must have **at least one** of the specified tags | Tags: `["crm", "sales"]` matches templates with either "crm" OR "sales" |
| `all` | Template must have **all** of the specified tags | Tags: `["crm", "sales"]` matches only templates with both "crm" AND "sales" |

#### Request Examples

**Basic widget token:**

```bash
curl -X POST https://api.airbyte.ai/api/v1/embedded/widget-token \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_name": "customer_workspace_123",
    "allowed_origin": "https://yourapp.com"
  }'
```

**Widget token with source template filtering:**

```bash
curl -X POST https://api.airbyte.ai/api/v1/embedded/widget-token \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_name": "customer_workspace_123",
    "allowed_origin": "https://yourapp.com",
    "selected_source_template_tags": ["crm", "sales"],
    "selected_source_template_tags_mode": "any"
  }'
```

**Widget token with both source and connection template filtering:**

```bash
curl -X POST https://api.airbyte.ai/api/v1/embedded/widget-token \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_name": "customer_workspace_123",
    "allowed_origin": "https://yourapp.com",
    "selected_source_template_tags": ["crm"],
    "selected_source_template_tags_mode": "any",
    "selected_connection_template_tags": ["standard-sync"],
    "selected_connection_template_tags_mode": "all",
    "region_id": "b9e48d61-f082-4a14-a8d0-799a907938cb"
  }'
```

#### Response Example

```json
{
  "token": "eyJ0b2tlbiI6ImV5SmhiR2NpT2lKSVV6STFOaUlzSW5SNWNDSTZJa3BYVkNKOS4uLiIsIndpZGdldFVybCI6Imh0dHBzOi8vYXBwLmFpcmJ5dGUuYWkvcXVpY2stc3RhcnQvd2lkZ2V0P3dvcmtzcGFjZUlkPWExYjJjM2Q0LWU1ZjYtNzg5MC1hYjEyLWNkMzRlZjU2Nzg5MCZhbGxvd2VkT3JpZ2luPWh0dHBzOi8veW91cmFwcC5jb20ifQ=="
}
```

### Using Widget Tokens

The widget token is a base64-encoded JSON object containing:

1. **Scoped token** - For API authentication
2. **Widget URL** - Pre-configured URL with workspace ID, origin, and template filters

#### Decode Widget Token

```javascript
// Example: Decode widget token in JavaScript
const decodedToken = JSON.parse(atob(widgetToken));

console.log(decodedToken.token);      // Scoped token for API calls
console.log(decodedToken.widgetUrl);  // URL to load the widget
```

#### Embed Widget

```html
<!-- Embed the Airbyte widget in an iframe -->
<iframe
  id="airbyte-widget"
  src=""
  width="100%"
  height="600px"
  frameborder="0">
</iframe>

<script>
  // Decode the widget token received from your backend
  const widgetToken = "eyJ0b2tlbiI6..."; // From API response
  const decoded = JSON.parse(atob(widgetToken));

  // Set the iframe src to the pre-configured widget URL
  document.getElementById('airbyte-widget').src = decoded.widgetUrl;
</script>
```

### Template Filtering with Tags

Widget tokens support filtering both source templates and connection templates using tags. This allows you to customize which connectors and sync configurations are available to specific users or customer tiers.

#### Use Cases

**Tier-based access:**
```json
{
  "workspace_name": "free_tier_customer",
  "allowed_origin": "https://yourapp.com",
  "selected_source_template_tags": ["free-tier"],
  "selected_source_template_tags_mode": "any"
}
```

**Industry-specific connectors:**
```json
{
  "workspace_name": "healthcare_customer",
  "allowed_origin": "https://yourapp.com",
  "selected_source_template_tags": ["healthcare", "hipaa-compliant"],
  "selected_source_template_tags_mode": "all"
}
```

**Feature gating:**
```json
{
  "workspace_name": "beta_customer",
  "allowed_origin": "https://yourapp.com",
  "selected_source_template_tags": ["stable", "beta"],
  "selected_source_template_tags_mode": "any",
  "selected_connection_template_tags": ["premium-features"],
  "selected_connection_template_tags_mode": "any"
}
```

## Authentication Flow Patterns

### Pattern 1: Direct API Integration

For backend services or API integrations:

1. Store **Operator Bearer Token** securely in your backend
2. Generate **Scoped Token** for each customer workspace
3. Use scoped token for all workspace-specific API calls
4. Cache scoped tokens (they don't expire frequently)

```bash
# 1. Generate scoped token (once per workspace)
SCOPED_TOKEN=$(curl -X POST https://api.airbyte.ai/api/v1/embedded/scoped-token \
  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"workspace_name": "customer_123"}' | jq -r '.token')

# 2. Use scoped token for operations
curl https://api.airbyte.ai/api/v1/embedded/sources \
  -H "Authorization: Bearer $SCOPED_TOKEN"
```

### Pattern 2: Embedded Widget Integration

For embedding the Airbyte UI in your application:

1. Store **Operator Bearer Token** in your backend
2. Create API endpoint in your backend to generate widget tokens
3. Generate **Widget Token** with appropriate tags and origin
4. Return widget token to frontend
5. Frontend decodes token and loads widget

```javascript
// Backend endpoint (Node.js example)
app.post('/api/airbyte/widget-token', async (req, res) => {
  const { customerId, tier } = req.body;

  // Determine tags based on customer tier
  const tags = tier === 'premium' ? ['all'] : ['free-tier'];

  const response = await fetch('https://api.airbyte.ai/api/v1/embedded/widget-token', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.AIRBYTE_OPERATOR_TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      workspace_name: `customer_${customerId}`,
      allowed_origin: 'https://yourapp.com',
      selected_source_template_tags: tags,
      selected_source_template_tags_mode: 'any'
    })
  });

  const data = await response.json();
  res.json({ widgetToken: data.token });
});

// Frontend code
async function loadAirbyteWidget(customerId, tier) {
  // Get widget token from your backend
  const response = await fetch('/api/airbyte/widget-token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ customerId, tier })
  });

  const { widgetToken } = await response.json();

  // Decode and load widget
  const decoded = JSON.parse(atob(widgetToken));
  document.getElementById('airbyte-widget').src = decoded.widgetUrl;
}
```

### Pattern 3: Multi-Region Support

For applications serving users in different regions:

```bash
# Determine region based on customer location
REGION_ID="645a183f-b12b-4c6e-8ad3-99e165603450"  # US
# REGION_ID="b9e48d61-f082-4a14-a8d0-799a907938cb"  # EU

curl -X POST https://api.airbyte.ai/api/v1/embedded/scoped-token \
  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"workspace_name\": \"customer_workspace\",
    \"region_id\": \"$REGION_ID\"
  }"
```

## Token Lifecycle Management

### Token Expiration

- **Operator Bearer Tokens**: Long-lived, managed by Airbyte
- **Scoped Tokens**: Long-lived, remain valid unless explicitly revoked
- **Widget Tokens**: Contain scoped tokens, same lifetime

### Token Refresh

For long-running applications, implement token refresh logic:

```javascript
class AirbyteTokenManager {
  constructor(operatorToken) {
    this.operatorToken = operatorToken;
    this.scopedTokens = new Map();
  }

  async getScopedToken(workspaceName) {
    // Check cache
    if (this.scopedTokens.has(workspaceName)) {
      return this.scopedTokens.get(workspaceName);
    }

    // Generate new scoped token
    const response = await fetch('https://api.airbyte.ai/api/v1/embedded/scoped-token', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.operatorToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ workspace_name: workspaceName })
    });

    const { token } = await response.json();
    this.scopedTokens.set(workspaceName, token);

    return token;
  }

  // Clear cache to force token refresh
  refreshToken(workspaceName) {
    this.scopedTokens.delete(workspaceName);
  }
}
```

## Security Considerations

### Operator Bearer Token

- **Never commit to version control**
- Store in environment variables or secure secrets management
- Rotate periodically (every 90 days recommended)
- Limit access to administrators only
- Use separate tokens for development and production

### Scoped Token

- **Safe to store** on client-side applications (mobile apps, CLIs)
- Automatically scoped to specific workspace
- Cannot access other workspaces
- Can be safely distributed to end-users
- Consider user-specific token generation for audit trails

### Widget Token

- **Origin validation** prevents unauthorized embedding
- Ensure `allowed_origin` exactly matches your application's origin
- Use HTTPS origins in production
- Decode token only in trusted frontend code
- Monitor for unauthorized widget usage

### CORS and Origin Validation

The `allowed_origin` parameter in widget tokens enforces CORS policies:

```javascript
// Correct origin format
allowed_origin: "https://yourapp.com"       // ✓ Correct
allowed_origin: "https://yourapp.com:443"   // ✓ Correct with port
allowed_origin: "http://localhost:3000"     // ✓ For development

// Incorrect formats
allowed_origin: "https://yourapp.com/"      // ✗ No trailing slash
allowed_origin: "yourapp.com"               // ✗ Missing protocol
allowed_origin: "*.yourapp.com"             // ✗ No wildcards
```

## Error Responses

### 401 Unauthorized

```json
{
  "detail": "Invalid authentication credentials"
}
```

**Causes:**
- Missing Authorization header
- Invalid or expired token
- Wrong token type for endpoint

**Solutions:**
- Verify token is included in Authorization header
- Ensure using correct token type (operator vs scoped)
- Generate new token if expired

### 403 Forbidden

```json
{
  "detail": "Access denied to this resource"
}
```

**Causes:**
- Scoped token trying to access resources in different workspace
- Insufficient permissions for operation

**Solutions:**
- Verify token scope matches target workspace
- Use operator token for organization-level operations

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "allowed_origin"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Cause:** Missing or invalid request parameters

**Solution:** Verify all required fields are included and properly formatted

## Common Patterns and Examples

### Example: Multi-Tenant SaaS Application

```javascript
// Backend service managing customer workspaces
class CustomerWorkspaceManager {
  constructor(airbyteOperatorToken) {
    this.operatorToken = airbyteOperatorToken;
  }

  async provisionCustomerWorkspace(customerId, customerTier, region = 'US') {
    const regionMap = {
      'US': '645a183f-b12b-4c6e-8ad3-99e165603450',
      'EU': 'b9e48d61-f082-4a14-a8d0-799a907938cb'
    };

    // Generate scoped token for customer workspace
    const response = await fetch('https://api.airbyte.ai/api/v1/embedded/scoped-token', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.operatorToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        workspace_name: `customer_${customerId}`,
        region_id: regionMap[region]
      })
    });

    const { token } = await response.json();

    // Store token in your database associated with customer
    await db.customers.update(customerId, {
      airbyte_token: token,
      airbyte_workspace: `customer_${customerId}`
    });

    return token;
  }

  async getWidgetToken(customerId, allowedOrigin) {
    const customer = await db.customers.get(customerId);

    // Determine template tags based on customer tier
    const tierTags = {
      'free': ['free-tier'],
      'pro': ['free-tier', 'pro-tier'],
      'enterprise': ['free-tier', 'pro-tier', 'enterprise']
    };

    const response = await fetch('https://api.airbyte.ai/api/v1/embedded/widget-token', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.operatorToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        workspace_name: customer.airbyte_workspace,
        allowed_origin: allowedOrigin,
        selected_source_template_tags: tierTags[customer.tier],
        selected_source_template_tags_mode: 'any'
      })
    });

    return await response.json();
  }
}
```

## Next Steps

- Learn about [Workspace Management](./workspaces.md)
- Create [Source Templates](./source-templates.md)
- Create [Connection Templates](./connection-templates.md)
- Explore [Tag Management](./tags.md) for template organization
