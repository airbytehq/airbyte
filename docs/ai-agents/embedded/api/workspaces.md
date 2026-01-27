# Workspace Management

Workspaces in Airbyte represent logical containers for your data integration pipelines. Each workspace can contain multiple sources, destinations, and connections. The Workspace Management API allows you to programmatically list, retrieve, update, and manage workspaces within your organization.

## Overview

The Workspace API provides comprehensive management capabilities:

- **List workspaces** with filtering and pagination
- **Get workspace details** by ID
- **Update workspace** name and status
- **Delete workspaces** (soft delete)
- **View workspace statistics** (active/inactive counts)
- **Sync workspaces** from Airbyte Cloud to your local database

All workspace endpoints require **Operator Bearer Token** authentication.

## Workspace status

Each workspace has a status that controls its availability:

- `active` - Workspace is active and all connections can run normally
- `inactive` - Workspace is inactive; setting this status automatically disables all active connections

## List workspaces

Retrieve a paginated list of workspaces for your organization.

### Endpoint

```bash
GET https://api.airbyte.ai/api/v1/workspaces

```

### Query parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name_contains` | string | No | - | Filter workspaces by name (case-insensitive partial match) |
| `status` | string | No | - | Filter by status: `active` or `inactive`. Returns all if not specified |
| `limit` | integer | No | 20 | Maximum number of workspaces to return (max: 100) |
| `cursor` | string | No | - | Opaque pagination cursor from previous response |

### Request example

```bash
curl https://api.airbyte.ai/api/v1/workspaces?limit=50&status=active \

  -H 'Authorization: Bearer <your_operator_token>'

```

### Response example

```json
{
  "data": [
    {
      "id": "a1b2c3d4-e5f6-7890-ab12-cd34ef567890",
      "name": "Production Workspace",
      "organization_id": "12345678-1234-1234-1234-123456789012",
      "status": "active",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    },
    {
      "id": "b2c3d4e5-f6g7-8901-bc23-de45fg678901",
      "name": "Development Workspace",
      "organization_id": "12345678-1234-1234-1234-123456789012",
      "status": "active",
      "created_at": "2025-01-10T14:20:00Z",
      "updated_at": "2025-01-12T09:15:00Z"
    }
  ],
  "next": "https://api.airbyte.ai/api/v1/workspaces?limit=50&cursor=eyJvZmZzZXQiOjUwfQ=="
}

```

### Response fields

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | List of workspace objects |
| `next` | string | URL for the next page of results (null if no more pages) |

#### Workspace object

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier for the workspace |
| `name` | string | Workspace name |
| `organization_id` | UUID | Organization that owns this workspace |
| `status` | string | Workspace status: `active` or `inactive` |
| `created_at` | datetime | Timestamp when the workspace was created |
| `updated_at` | datetime | Timestamp when the workspace was last updated |

### Pagination

The API uses cursor-based pagination. To retrieve the next page:

1. Check the `next` field in the response
2. If `next` is not null, make a GET request to that URL
3. Continue until `next` is null

**Example pagination workflow:**

```bash
# First page
curl https://api.airbyte.ai/api/v1/workspaces?limit=20 \

  -H 'Authorization: Bearer <your_token>'

# Use the 'next' URL from the response for the second page
curl https://api.airbyte.ai/api/v1/workspaces?limit=20&cursor=eyJvZmZzZXQiOjIwfQ== \

  -H 'Authorization: Bearer <your_token>'

```

### Filtering examples

**Filter by name:**

```bash
curl https://api.airbyte.ai/api/v1/workspaces?name_contains=prod \

  -H 'Authorization: Bearer <your_token>'

```

**Filter by status:**

```bash
curl https://api.airbyte.ai/api/v1/workspaces?status=active \

  -H 'Authorization: Bearer <your_token>'

```

**Combined filters:**

```bash
curl https://api.airbyte.ai/api/v1/workspaces?status=active&name_contains=dev&limit=10 \

  -H 'Authorization: Bearer <your_token>'

```

## Get workspace

Retrieve details for a specific workspace.

### Endpoint

```bash
GET https://api.airbyte.ai/api/v1/workspaces/{workspace ID}

```

### Path parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspace ID` | UUID | Yes | Unique identifier of the workspace |

### Request example

```bash
curl https://api.airbyte.ai/api/v1/workspaces/a1b2c3d4-e5f6-7890-ab12-cd34ef567890 \

  -H 'Authorization: Bearer <your_operator_token>'

```

### Response example

```json
{
  "id": "a1b2c3d4-e5f6-7890-ab12-cd34ef567890",
  "name": "Production Workspace",
  "organization_id": "12345678-1234-1234-1234-123456789012",
  "status": "active",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}

```

## Update workspace

Update a workspace's name and/or status.

### Endpoint

```bash
PUT https://api.airbyte.ai/api/v1/workspaces/{workspace ID}

```

### Path parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspace ID` | UUID | Yes | Unique identifier of the workspace |

### Request body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | No | New name for the workspace |
| `status` | string | No | New status: `active` or `inactive` |

### Important behavior

When setting status to `inactive`, **all active connections in the workspace will be automatically disabled**. This ensures that no data syncs occur while the workspace is inactive.

### Request example

**Update workspace name:**

```bash
curl -X PUT https://api.airbyte.ai/api/v1/workspaces/a1b2c3d4-e5f6-7890-ab12-cd34ef567890 \

  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{

    "name": "Production Workspace - Updated"
  }'

```

**Change workspace status to inactive:**

```bash
curl -X PUT https://api.airbyte.ai/api/v1/workspaces/a1b2c3d4-e5f6-7890-ab12-cd34ef567890 \

  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{

    "status": "inactive"
  }'

```

**Update both name and status:**

```bash
curl -X PUT https://api.airbyte.ai/api/v1/workspaces/a1b2c3d4-e5f6-7890-ab12-cd34ef567890 \

  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{

    "name": "Archived Production",
    "status": "inactive"
  }'

```

### Response example

```json
{
  "id": "a1b2c3d4-e5f6-7890-ab12-cd34ef567890",
  "name": "Production Workspace - Updated",
  "organization_id": "12345678-1234-1234-1234-123456789012",
  "status": "active",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-10-08T15:45:00Z"
}

```

## Delete workspace

Delete a workspace from both Airbyte Cloud and mark it as deleted locally (soft delete).

### Endpoint

```bash
DELETE https://api.airbyte.ai/api/v1/workspaces/{workspace ID}

```

### Path parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspace ID` | UUID | Yes | Unique identifier of the workspace |

### Request example

```bash
curl -X DELETE https://api.airbyte.ai/api/v1/workspaces/a1b2c3d4-e5f6-7890-ab12-cd34ef567890 \

  -H 'Authorization: Bearer <your_operator_token>'

```

### Response example

```json
{
  "id": "a1b2c3d4-e5f6-7890-ab12-cd34ef567890",
  "deleted_at": "2025-10-08T16:00:00Z"
}

```

### Important notes

- This performs a soft delete in the local database
- The workspace is deleted from Airbyte Cloud
- All associated resources (sources, destinations, connections) will also be deleted

## Get workspace statistics

Retrieve statistics about workspaces in your organization.

### Endpoint

```bash
GET https://api.airbyte.ai/api/v1/workspaces/stats

```

### Request example

```bash
curl https://api.airbyte.ai/api/v1/workspaces/stats \

  -H 'Authorization: Bearer <your_operator_token>'

```

### Response example

```json
{
  "active_count": 12,
  "inactive_count": 3,
  "total_count": 15
}

```

### Response fields

| Field | Type | Description |
|-------|------|-------------|
| `active_count` | integer | Number of workspaces with status `active` |
| `inactive_count` | integer | Number of workspaces with status `inactive` |
| `total_count` | integer | Total number of workspaces |

### Response fields

| Field | Type | Description |
|-------|------|-------------|
| `total_count` | integer | Total number of workspaces found in Airbyte Cloud |
| `created_count` | integer | Number of new workspaces created locally |
| `created_workspace IDs` | array of UUIDs | IDs of the newly created workspaces |

## Common use cases

### Monitor workspace health

Combine workspace stats and listing to monitor your organization:

```bash
# Get overview statistics
curl https://api.airbyte.ai/api/v1/workspaces/stats \

  -H 'Authorization: Bearer <your_token>'

# List inactive workspaces for review
curl https://api.airbyte.ai/api/v1/workspaces?status=inactive \

  -H 'Authorization: Bearer <your_token>'

```

### Deactivate workspace and connections

When you need to pause all activity in a workspace:

```bash
curl -X PUT https://api.airbyte.ai/api/v1/workspaces/a1b2c3d4-e5f6-7890-ab12-cd34ef567890 \

  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json' \
  -d '{

    "status": "inactive"
  }'

```

This automatically disables all connections, preventing any data syncs.

### Search for workspaces

Find workspaces by name pattern:

```bash
# Find all production workspaces
curl https://api.airbyte.ai/api/v1/workspaces?name_contains=production \

  -H 'Authorization: Bearer <your_token>'

```

## Error responses

### 401 unauthorized

```json
{
  "detail": "Invalid authentication credentials"
}

```

**Cause:** Missing or invalid Operator Bearer Token

**Solution:** Ensure you're using a valid operator token in the Authorization header

### 404 not found

```json
{
  "detail": "Workspace not found"
}

```

**Cause:** The specified workspace ID does not exist

**Solution:** Verify the workspace ID and ensure it belongs to your organization

### 422 validation error

```json
{
  "detail": [
    {
      "loc": ["body", "status"],
      "msg": "value is not a valid enumeration member; permitted: 'active', 'inactive'",
      "type": "type_error.enum"
    }
  ]
}

```

**Cause:** Invalid request parameters

**Solution:** Check that all parameters match the expected format and values
