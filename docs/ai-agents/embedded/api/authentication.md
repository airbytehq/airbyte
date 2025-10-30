# Authentication

The Airbyte Embedded API uses a hierarchical authentication system with three types of tokens, each designed for specific use cases and security requirements.

## Token types overview

| Token Type | Use Case | Scope | Access Level |
|------------|----------|-------|--------------|
| **Operator Bearer Token** | Organization management, template creation | Organization-wide | Full access to organization resources |
| **Scoped Token** | API integration, programmatic workspace access | Single workspace | Limited to specific workspace |
| **Widget Token** | Embedded widget integration | Single workspace + origin validation | Limited to specific workspace with CORS protection |

## Operator bearer token

The Operator Bearer Token provides full organization-level access and is used for administrative operations.

### Use cases

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

### Security best practices

- **Never expose operator tokens in client-side code**
- Store securely in secrets management system
- Use scoped tokens for end-user operations
- Rotate tokens periodically
- Limit token distribution to trusted administrators only

## Scoped token

Scoped tokens provide workspace-level access and are designed for allowing end-users to create and edit sources in their workspace.

### Use cases

- API integrations for managing sources within a specific workspace
- Multi-tenant applications with isolated workspaces

### Features

- Workspace-scoped access (cannot access other workspaces)
- Automatically creates workspace from a workspace name if it doesn't exist
- Region selection support
- Embedded in JWT with `io.airbyte.auth.workspace_scope` claim

### Generate scoped token

#### Endpoint

```bash
POST https://api.airbyte.ai/api/v1/embedded/scoped-token

```

#### Authentication

Requires **Operator Bearer Token**

#### Request body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workspace_name` | string | Yes | Name of the workspace to create or use |
| `region_id` | UUID | No | Region where workspace should be created (defaults to US) |

#### Region ids

| Region | Region ID |
|--------|-----------|
| US (Default) | `645a183f-b12b-4c6e-8ad3-99e165603450` |
| EU | `b9e48d61-f082-4a14-a8d0-799a907938cb` |

#### Request example

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

#### Response example

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

```

#### Behavior notes

- If the workspace already exists, returns a token for the existing workspace
- If the workspace doesn't exist:
  - Checks if a workspace with the same name exists in Airbyte Cloud
  - If found in cloud, creates local database record
  - If not found, creates new workspace in both Airbyte Cloud and local database
- The `region_id` is only used when creating a new workspace

### Using scoped tokens

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

### Get scoped token information

Retrieve organization and workspace information from a scoped token.

#### Endpoint

```bash
GET https://api.airbyte.ai/api/v1/embedded/scoped-token/info

```

#### Authentication

Requires **Scoped Token**

#### Request example

```bash
curl https://api.airbyte.ai/api/v1/embedded/scoped-token/info \

  -H 'Authorization: Bearer <scoped_token>'

```

#### Response example

```json
{
  "organization_id": "12345678-1234-1234-1234-123456789012",
  "workspace ID": "a1b2c3d4-e5f6-7890-ab12-cd34ef567890"
}

```

## Widget token

Widget tokens are specialized tokens designed for embedded widget integration with enhanced security features.

### Use cases

- Embedding the Airbyte configuration widget in your application
- Providing end-users with a UI to configure data sources
- Multi-tenant applications with isolated workspaces

### Features

- All features of scoped tokens
- **Origin validation** for CORS protection via `allowed_origin`
- **Template filtering** via tags (both source and connection templates)
- Base64-encoded payload containing token and pre-configured widget URL
- Tag selection modes: `any` (at least one tag) or `all` (all tags required)

### Generate widget token

#### Endpoint

```bash
POST https://api.airbyte.ai/api/v1/embedded/widget-token

```

#### Authentication

Requires **Operator Bearer Token**

#### Request body

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `workspace_name` | string | Yes | - | Name of the workspace to create or use |
| `allowed_origin` | string | Yes | - | The allowed origin for CORS (for example, `https://yourapp.com`) |
| `region_id` | UUID | No | US region | Region where workspace should be created |
| `selected_source_template_tags` | array of strings | No | `[]` | Tags to filter which source templates are available |
| `selected_source_template_tags_mode` | string | No | `any` | Tag selection mode: `any` or `all` |
| `selected_connection_template_tags` | array of strings | No | `[]` | Tags to filter which connection templates are available |
| `selected_connection_template_tags_mode` | string | No | `any` | Tag selection mode: `any` or `all` |

#### Tag selection modes

| Mode | Behavior | Example |
|------|----------|---------|
| `any` | Template must have **at least one** of the specified tags | Tags: `["crm", "sales"]` matches templates with either "crm" OR "sales" |
| `all` | Template must have **all** of the specified tags | Tags: `["crm", "sales"]` matches only templates with both "crm" AND "sales" |

#### Request examples

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

#### Response example

```json
{
  "token": "eyJ0b2tlbiI6ImV5SmhiR2NpT2lKSVV6STFOaUlzSW5SNWNDSTZJa3BYVkNKOS4uLiIsIndpZGdldFVybCI6Imh0dHBzOi8vYXBwLmFpcmJ5dGUuYWkvcXVpY2stc3RhcnQvd2lkZ2V0P3dvcmtzcGFjZUlkPWExYjJjM2Q0LWU1ZjYtNzg5MC1hYjEyLWNkMzRlZjU2Nzg5MCZhbGxvd2VkT3JpZ2luPWh0dHBzOi8veW91cmFwcC5jb20ifQ=="
}

```

### Using widget tokens

The widget token is a base64-encoded JSON object containing:

1. **Scoped token** - For API authentication
2. **Widget URL** - Pre-configured URL with workspace ID, origin, and template filters

#### Decode widget token

```javascript
// Example: Decode widget token in JavaScript
const decodedToken = JSON.parse(atob(widgetToken));

console.log(decodedToken.token);      // Scoped token for API calls
console.log(decodedToken.widgetUrl);  // URL to load the widget

```

#### Embed widget

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

### Template filtering with tags

Widget tokens support filtering both source templates and connection templates using tags. This allows you to customize which connectors and sync configurations are available to specific users or customer tiers.

#### Use cases

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

## Authentication flow patterns

### Pattern 1: direct API integration

For backend services or API integrations:

1. Store **Operator Bearer Token** securely in your backend
2. Generate **Scoped Token** for each customer workspace
3. Use scoped token for all workspace-specific API calls
4. Refresh scoped tokens when they expire (they expire after 20 minutes)

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

### Pattern 2: embedded widget integration

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

### Pattern 3: multi-region support

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

## Token lifecycle management

### Token expiration

- **Operator Bearer Tokens**: Short-lived, expires after 15 minutes
- **Scoped Tokens**: Short-lived, expires after 20 minutes
- **Widget Tokens**: Contain scoped tokens, same lifetime

## Security considerations

### CORS and origin validation

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

## Error responses

### 401 unauthorized

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

### 403 forbidden

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

### 422 validation error

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

## Next steps

- Learn about [Workspace Management](./workspaces.md)
- Create [Source Templates](./source-templates.md)
- Create [Connection Templates](./connection-templates.md)
- Explore [Tag Management](./tags.md) for template organization
