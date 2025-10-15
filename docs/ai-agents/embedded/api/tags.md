# Template Tags

Template tags provide a flexible way to organize, categorize, and filter both source templates and connection templates. Tags enable you to control which templates are available to different users, implement tier-based access, and organize templates by use case, industry, or any custom criteria.

## Overview

The Template Tags API allows you to:

- **Create and manage tags** centrally for your organization
- **Tag source templates** to control which data sources are available
- **Tag connection templates** to control sync configurations
- **Filter templates by tags** when generating widget tokens or listing templates
- **Implement access control** using tag-based filtering

## Use cases

### Tier-based access control

Implement different feature tiers by tagging templates:

```bash
Tags: "free-tier", "pro-tier", "enterprise"

Example:

- Basic connectors: tagged with "free-tier"
- Advanced connectors: tagged with "pro-tier"
- Premium connectors: tagged with "enterprise"

```

### Industry-specific organization

Organize templates by industry or compliance requirements:

```bash
Tags: "healthcare", "hipaa-compliant", "finance", "retail"

Example:

- HIPAA-compliant connectors: tagged with "healthcare", "hipaa-compliant"
- Financial connectors: tagged with "finance", "pci-compliant"

```

### Feature staging

Manage connector rollout with stability tags:

```bash
Tags: "stable", "beta", "experimental"

Example:

- Production-ready: tagged with "stable"
- Beta features: tagged with "beta"
- Experimental features: tagged with "experimental"

```

### Use-case categorization

Group templates by business function:

```bash
Tags: "crm", "analytics", "marketing", "sales", "support"

Example:

- Salesforce, HubSpot: tagged with "crm", "sales"
- Google Analytics, Mixpanel: tagged with "analytics"

```

## Tag selection modes

When filtering templates by tags, you can control matching behavior with **Tag Selection Modes**:

| Mode | Behavior | Example |
|------|----------|---------|
| `any` | Template must have **at least one** of the specified tags | Tags: `["crm", "sales"]` matches templates with "crm" OR "sales" |
| `all` | Template must have **all** of the specified tags | Tags: `["crm", "sales"]` matches only templates with both "crm" AND "sales" |

## Tag management API

### Create tag

Create a new tag for your organization.

#### Endpoint

```bash
POST https://api.airbyte.ai/api/v1/integrations/templates/tags

```

#### Authentication

Requires **Operator Bearer Token** or **Scoped Token**

#### Request body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Tag name (max 255 characters) |

#### Request example

```bash
curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/tags \

  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{

    "name": "pro-tier"
  }'

```

#### Response example

```json
{
  "id": "a1b2c3d4-e5f6-7890-ab12-cd34ef567890",
  "name": "pro-tier",
  "organization_id": "12345678-1234-1234-1234-123456789012",
  "created_at": "2025-10-08T10:30:00Z",
  "updated_at": "2025-10-08T10:30:00Z"
}

```

### List tags

Retrieve all tags for your organization.

#### Endpoint

```bash
GET https://api.airbyte.ai/api/v1/integrations/templates/tags

```

#### Authentication

Requires **Operator Bearer Token** or **Scoped Token**

#### Request example

```bash
curl https://api.airbyte.ai/api/v1/integrations/templates/tags \

  -H 'Authorization: Bearer <your_operator_token>'

```

#### Response example

```json
{
  "data": [
    {
      "id": "a1b2c3d4-e5f6-7890-ab12-cd34ef567890",
      "name": "free-tier",
      "organization_id": "12345678-1234-1234-1234-123456789012",
      "created_at": "2025-10-01T10:00:00Z",
      "updated_at": "2025-10-01T10:00:00Z"
    },
    {
      "id": "b2c3d4e5-f6g7-8901-bc23-de45fg678901",
      "name": "pro-tier",
      "organization_id": "12345678-1234-1234-1234-123456789012",
      "created_at": "2025-10-05T14:20:00Z",
      "updated_at": "2025-10-05T14:20:00Z"
    },
    {
      "id": "c3d4e5f6-g7h8-9012-cd34-ef56gh789012",
      "name": "healthcare",
      "organization_id": "12345678-1234-1234-1234-123456789012",
      "created_at": "2025-10-07T09:15:00Z",
      "updated_at": "2025-10-07T09:15:00Z"
    }
  ]
}

```

### Update tag

Update an existing tag's name.

#### Endpoint

```bash
PUT https://api.airbyte.ai/api/v1/integrations/templates/tags/{name}

```

#### Authentication

Requires **Operator Bearer Token** or **Scoped Token**

#### Path parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Current name of the tag |

#### Request body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | New name for the tag (max 255 characters) |

#### Request example

```bash
curl -X PUT https://api.airbyte.ai/api/v1/integrations/templates/tags/pro-tier \

  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{

    "name": "professional-tier"
  }'

```

#### Response example

```json
{
  "id": "a1b2c3d4-e5f6-7890-ab12-cd34ef567890",
  "name": "professional-tier",
  "organization_id": "12345678-1234-1234-1234-123456789012",
  "created_at": "2025-10-08T10:30:00Z",
  "updated_at": "2025-10-08T16:45:00Z"
}

```

#### Important notes

- Updating a tag name automatically updates all associations with source and connection templates
- The tag name is used as the identifier in the URL path parameter

### Delete tag

Delete a tag from your organization.

#### Endpoint

```bash
DELETE https://api.airbyte.ai/api/v1/integrations/templates/tags/{name}

```

#### Authentication

Requires **Operator Bearer Token** or **Scoped Token**

#### Path parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Name of the tag to delete |

#### Request example

```bash
curl -X DELETE https://api.airbyte.ai/api/v1/integrations/templates/tags/experimental \

  -H 'Authorization: Bearer <your_operator_token>'

```

#### Response example

```json
{
  "id": "a1b2c3d4-e5f6-7890-ab12-cd34ef567890",
  "deleted_at": "2025-10-08T17:00:00Z"
}

```

#### Important notes

- Deleting a tag removes all associations with source and connection templates
- This operation cannot be undone
- Templates will remain but will no longer have this tag

## Tagging source templates

### Add tag to source template

Add a tag to a specific source template.

#### Endpoint

```bash
POST https://api.airbyte.ai/api/v1/integrations/templates/sources/{id}/tags

```

#### Authentication

Requires **Operator Bearer Token** or **Scoped Token**

#### Path parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | Source template ID |

#### Request body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tag` | string | Yes | Name of the tag to add |

#### Request example

```bash
curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/sources/a1b2c3d4-e5f6-7890-ab12-cd34ef567890/tags \

  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{

    "tag": "pro-tier"
  }'

```

#### Response example

```json
{
  "id": "a1b2c3d4-e5f6-7890-ab12-cd34ef567890",
  "name": "Salesforce Source",
  "actor_definition_id": "def123-...",
  "organization_id": "12345678-1234-1234-1234-123456789012",
  "tags": ["crm", "sales", "pro-tier"],
  "created_at": "2025-10-01T10:00:00Z",
  "updated_at": "2025-10-08T17:15:00Z"
}

```

### Remove tag from source template

Remove a tag from a specific source template.

#### Endpoint

```bash
DELETE https://api.airbyte.ai/api/v1/integrations/templates/sources/{id}/tags/{tag_name}

```

#### Authentication

Requires **Operator Bearer Token** or **Scoped Token**

#### Path parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | Source template ID |
| `tag_name` | string | Yes | Name of the tag to remove |

#### Request example

```bash
curl -X DELETE https://api.airbyte.ai/api/v1/integrations/templates/sources/a1b2c3d4-e5f6-7890-ab12-cd34ef567890/tags/beta \

  -H 'Authorization: Bearer <your_operator_token>'

```

#### Response example

```json
{
  "id": "a1b2c3d4-e5f6-7890-ab12-cd34ef567890",
  "name": "Salesforce Source",
  "actor_definition_id": "def123-...",
  "organization_id": "12345678-1234-1234-1234-123456789012",
  "tags": ["crm", "sales", "pro-tier"],
  "created_at": "2025-10-01T10:00:00Z",
  "updated_at": "2025-10-08T17:20:00Z"
}

```

## Tagging connection templates

### Add tag to connection template

Add a tag to a specific connection template.

#### Endpoint

```bash
POST https://api.airbyte.ai/api/v1/integrations/templates/connections/{id}/tags

```

#### Authentication

Requires **Operator Bearer Token**

#### Path parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | Connection template ID |

#### Request body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tag` | string | Yes | Name of the tag to add |

#### Request example

```bash
curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/connections/b2c3d4e5-f6g7-8901-bc23-de45fg678901/tags \

  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{

    "tag": "standard-sync"
  }'

```

#### Response example

```json
{
  "id": "b2c3d4e5-f6g7-8901-bc23-de45fg678901",
  "name": "Standard BigQuery Sync",
  "destination_actor_definition_id": "dest456-...",
  "organization_id": "12345678-1234-1234-1234-123456789012",
  "tags": ["analytics", "standard-sync"],
  "created_at": "2025-10-02T11:00:00Z",
  "updated_at": "2025-10-08T17:25:00Z"
}

```

### Remove tag from connection template

Remove a tag from a specific connection template.

#### Endpoint

```bash
DELETE https://api.airbyte.ai/api/v1/integrations/templates/connections/{id}/tags/{tag_name}

```

#### Authentication

Requires **Operator Bearer Token**

#### Path parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | Connection template ID |
| `tag_name` | string | Yes | Name of the tag to remove |

#### Request example

```bash
curl -X DELETE https://api.airbyte.ai/api/v1/integrations/templates/connections/b2c3d4e5-f6g7-8901-bc23-de45fg678901/tags/beta \

  -H 'Authorization: Bearer <your_operator_token>'

```

#### Response example

```json
{
  "id": "b2c3d4e5-f6g7-8901-bc23-de45fg678901",
  "name": "Standard BigQuery Sync",
  "destination_actor_definition_id": "dest456-...",
  "organization_id": "12345678-1234-1234-1234-123456789012",
  "tags": ["analytics", "standard-sync"],
  "created_at": "2025-10-02T11:00:00Z",
  "updated_at": "2025-10-08T17:30:00Z"
}

```

## Filtering templates by tags

### Widget token with tag filtering

When generating a widget token, you can filter which templates are available by specifying tags:

```bash
curl -X POST https://api.airbyte.ai/api/v1/embedded/widget-token \

  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{

    "workspace_name": "customer_workspace",
    "allowed_origin": "https://yourapp.com",
    "selected_source_template_tags": ["pro-tier", "enterprise"],
    "selected_source_template_tags_mode": "any",
    "selected_connection_template_tags": ["standard-sync"],
    "selected_connection_template_tags_mode": "all"
  }'

```

In this example:

- **Source templates**: Must have "pro-tier" OR "enterprise" tag (`any` mode)
- **Connection templates**: Must have "standard-sync" tag (`all` mode with single tag)

### List templates with tag filtering

Both source and connection template list endpoints support tag filtering:

**Source templates:**

```bash
curl https://api.airbyte.ai/api/v1/integrations/templates/sources?tags=crm&tags=sales&tags_mode=any \

  -H 'Authorization: Bearer <your_operator_token>'

```

**Connection templates:**

```bash
curl https://api.airbyte.ai/api/v1/integrations/templates/connections?tags=analytics&tags=standard-sync&tags_mode=all \

  -H 'Authorization: Bearer <your_operator_token>'

```

## Common workflows

### Workflow 1: set up tier-based access

```bash
# 1. Create tier tags
curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/tags \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "free-tier"}'

curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/tags \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "pro-tier"}'

curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/tags \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "enterprise"}'

# 2. Tag source templates
curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/sources/$BASIC_SOURCE_ID/tags \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tag": "free-tier"}'

curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/sources/$PREMIUM_SOURCE_ID/tags \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tag": "enterprise"}'

# 3. Generate widget tokens with tier filtering
# Free tier customer
curl -X POST https://api.airbyte.ai/api/v1/embedded/widget-token \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{

    "workspace_name": "free_customer",
    "allowed_origin": "https://yourapp.com",
    "selected_source_template_tags": ["free-tier"],
    "selected_source_template_tags_mode": "any"
  }'

# Enterprise tier customer
curl -X POST https://api.airbyte.ai/api/v1/embedded/widget-token \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{

    "workspace_name": "enterprise_customer",
    "allowed_origin": "https://yourapp.com",
    "selected_source_template_tags": ["free-tier", "pro-tier", "enterprise"],
    "selected_source_template_tags_mode": "any"
  }'

```

### Workflow 2: organize by industry

```bash
# 1. Create industry tags
for industry in "healthcare" "finance" "retail" "technology"; do
  curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/tags \

    -H "Authorization: Bearer $OPERATOR_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$industry\"}"

done

# 2. Tag healthcare-specific templates
curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/sources/$EMR_SOURCE_ID/tags \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tag": "healthcare"}'

# 3. Also tag with compliance tags
curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/tags \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "hipaa-compliant"}'

curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/sources/$EMR_SOURCE_ID/tags \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tag": "hipaa-compliant"}'

# 4. Filter for healthcare customer with compliance requirements
curl -X POST https://api.airbyte.ai/api/v1/embedded/widget-token \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{

    "workspace_name": "healthcare_customer",
    "allowed_origin": "https://yourapp.com",
    "selected_source_template_tags": ["healthcare", "hipaa-compliant"],
    "selected_source_template_tags_mode": "all"
  }'

```

### Workflow 3: feature staging

```bash
# 1. Create stability tags
curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/tags \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "stable"}'

curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/tags \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "beta"}'

# 2. Tag production-ready templates
curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/sources/$PROD_SOURCE_ID/tags \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tag": "stable"}'

# 3. Tag beta features
curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/sources/$BETA_SOURCE_ID/tags \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tag": "beta"}'

# 4. Prod customers see only stable
curl -X POST https://api.airbyte.ai/api/v1/embedded/widget-token \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{

    "workspace_name": "prod_customer",
    "allowed_origin": "https://yourapp.com",
    "selected_source_template_tags": ["stable"],
    "selected_source_template_tags_mode": "any"
  }'

# 5. Beta testers see both
curl -X POST https://api.airbyte.ai/api/v1/embedded/widget-token \

  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{

    "workspace_name": "beta_tester",
    "allowed_origin": "https://yourapp.com",
    "selected_source_template_tags": ["stable", "beta"],
    "selected_source_template_tags_mode": "any"
  }'

```

## Error responses

### 404 tag not found

```json
{
  "detail": "Template tag with name 'invalid-tag' not found."
}

```

**Cause:** Attempting to update or delete a tag that doesn't exist

**Solution:** Verify the tag name and ensure it exists in your organization

### 404 tag not found on template

```json
{
  "detail": "Tag 'pro-tier' not found on this template."
}

```

**Cause:** Attempting to remove a tag that isn't associated with the template

**Solution:** List the template's tags to verify which tags are attached

### 422 validation error

```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "ensure this value has at most 255 characters",
      "type": "value_error.any_str.max_length"
    }
  ]
}

```

**Cause:** Tag name exceeds maximum length

**Solution:** Use a tag name with 255 characters or fewer

## Integration examples

### Multi-tenant SaaS with tiered access

```javascript
// Backend: Generate widget token based on customer tier
async function generateCustomerWidgetToken(customerId) {
  const customer = await db.customers.get(customerId);

  // Map customer tier to tags
  const tierTagsMap = {
    'free': ['free-tier'],
    'pro': ['free-tier', 'pro-tier'],
    'enterprise': ['free-tier', 'pro-tier', 'enterprise']
  };

  const response = await fetch('https://api.airbyte.ai/api/v1/embedded/widget-token', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.AIRBYTE_OPERATOR_TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      workspace_name: `customer_${customerId}`,
      allowed_origin: 'https://yourapp.com',
      selected_source_template_tags: tierTagsMap[customer.tier],
      selected_source_template_tags_mode: 'any'
    })
  });

  return await response.json();
}

```

### Industry-specific applications

```python
# Backend: Healthcare application with compliance filtering
def get_compliant_widget_token(customer_id, compliance_requirements):
    customer = db.customers.get(customer_id)

    # Build tags based on compliance needs
    tags = ['healthcare']

    if 'HIPAA' in compliance_requirements:
        tags.append('hipaa-compliant')

    if 'GDPR' in compliance_requirements:
        tags.append('gdpr-compliant')

    response = requests.post(
        'https://api.airbyte.ai/api/v1/embedded/widget-token',
        headers={
            'Authorization': f'Bearer {OPERATOR_TOKEN}',
            'Content-Type': 'application/json'
        },
        json={
            'workspace_name': f'customer_{customer_id}',
            'allowed_origin': 'https://healthcare-app.com',
            'selected_source_template_tags': tags,
            'selected_source_template_tags_mode': 'all'  # Must have all compliance tags
        }
    )

    return response.json()

```

## Related documentation

- [Authentication](./authentication.md) - Learn about widget tokens and tag filtering
- [Source Templates](./source-templates.md) - Create and manage source templates
- [Connection Templates](./connection-templates.md) - Create and manage connection templates
- [Widget Integration](../widget/README.md) - Embed the Airbyte widget with tag filtering
