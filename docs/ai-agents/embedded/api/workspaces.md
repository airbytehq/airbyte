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

## Workspace Status

Each workspace has a status that controls its availability:

- `active` - Workspace is active and all connections can run normally
- `inactive` - Workspace is inactive; setting this status automatically disables all active connections

## List Workspaces

Retrieve a paginated list of workspaces for your organization.

### Endpoint

```
GET https://api.airbyte.ai/api/v1/workspaces
```

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name_contains` | string | No | - | Filter workspaces by name (case-insensitive partial match) |
| `status` | string | No | - | Filter by status: `active` or `inactive`. Returns all if not specified |
| `limit` | integer | No | 20 | Maximum number of workspaces to return (max: 100) |
| `cursor` | string | No | - | Opaque pagination cursor from previous response |

### Request Example

```bash
curl https://api.airbyte.ai/api/v1/workspaces?limit=50&status=active \
  -H 'Authorization: Bearer <your_operator_token>'
```

### Response Example

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

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | List of workspace objects |
| `next` | string | URL for the next page of results (null if no more pages) |

#### Workspace Object

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

### Filtering Examples

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

## Get Workspace

Retrieve details for a specific workspace.

### Endpoint

```
GET https://api.airbyte.ai/api/v1/workspaces/{workspace_id}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspace_id` | UUID | Yes | Unique identifier of the workspace |

### Request Example

```bash
curl https://api.airbyte.ai/api/v1/workspaces/a1b2c3d4-e5f6-7890-ab12-cd34ef567890 \
  -H 'Authorization: Bearer <your_operator_token>'
```

### Response Example

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

## Update Workspace

Update a workspace's name and/or status.

### Endpoint

```
PUT https://api.airbyte.ai/api/v1/workspaces/{workspace_id}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspace_id` | UUID | Yes | Unique identifier of the workspace |

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | No | New name for the workspace |
| `status` | string | No | New status: `active` or `inactive` |

### Important Behavior

When setting status to `inactive`, **all active connections in the workspace will be automatically disabled**. This ensures that no data syncs occur while the workspace is inactive.

### Request Example

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

### Response Example

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

## Delete Workspace

Delete a workspace from both Airbyte Cloud and mark it as deleted locally (soft delete).

### Endpoint

```
DELETE https://api.airbyte.ai/api/v1/workspaces/{workspace_id}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspace_id` | UUID | Yes | Unique identifier of the workspace |

### Request Example

```bash
curl -X DELETE https://api.airbyte.ai/api/v1/workspaces/a1b2c3d4-e5f6-7890-ab12-cd34ef567890 \
  -H 'Authorization: Bearer <your_operator_token>'
```

### Response Example

```json
{
  "id": "a1b2c3d4-e5f6-7890-ab12-cd34ef567890",
  "deleted_at": "2025-10-08T16:00:00Z"
}
```

### Important Notes

- This performs a soft delete in the local database
- The workspace is deleted from Airbyte Cloud
- All associated resources (sources, destinations, connections) will also be deleted

## Get Workspace Statistics

Retrieve statistics about workspaces in your organization.

### Endpoint

```
GET https://api.airbyte.ai/api/v1/workspaces/stats
```

### Request Example

```bash
curl https://api.airbyte.ai/api/v1/workspaces/stats \
  -H 'Authorization: Bearer <your_operator_token>'
```

### Response Example

```json
{
  "active_count": 12,
  "inactive_count": 3,
  "total_count": 15
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `active_count` | integer | Number of workspaces with status `active` |
| `inactive_count` | integer | Number of workspaces with status `inactive` |
| `total_count` | integer | Total number of workspaces |

## Sync Workspaces

Synchronize workspaces from Airbyte Cloud to your local database. This operation fetches all workspaces for your organization and creates any that don't exist locally.

### Endpoint

```
POST https://api.airbyte.ai/api/v1/workspaces/sync
```

### Use Case

Use this endpoint to:
- Keep your local workspace cache in sync with Airbyte Cloud
- Discover new workspaces created in Airbyte Cloud
- Refresh workspace data after changes in the cloud

### Request Example

```bash
curl -X POST https://api.airbyte.ai/api/v1/workspaces/sync \
  -H 'Authorization: Bearer <your_operator_token>'
```

### Response Example

```json
{
  "total_count": 15,
  "created_count": 2,
  "created_workspace_ids": [
    "c3d4e5f6-g7h8-9012-cd34-ef56gh789012",
    "d4e5f6g7-h8i9-0123-de45-fg67hi890123"
  ]
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `total_count` | integer | Total number of workspaces found in Airbyte Cloud |
| `created_count` | integer | Number of new workspaces created locally |
| `created_workspace_ids` | array of UUIDs | IDs of the newly created workspaces |

## Common Use Cases

### Monitor Workspace Health

Combine workspace stats and listing to monitor your organization:

```bash
# Get overview statistics
curl https://api.airbyte.ai/api/v1/workspaces/stats \
  -H 'Authorization: Bearer <your_token>'

# List inactive workspaces for review
curl https://api.airbyte.ai/api/v1/workspaces?status=inactive \
  -H 'Authorization: Bearer <your_token>'
```

### Deactivate Workspace and Connections

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

### Keep Local Database in Sync

Schedule periodic workspace synchronization:

```bash
# Sync every hour to catch new workspaces
curl -X POST https://api.airbyte.ai/api/v1/workspaces/sync \
  -H 'Authorization: Bearer <your_token>'
```

### Search for Workspaces

Find workspaces by name pattern:

```bash
# Find all production workspaces
curl https://api.airbyte.ai/api/v1/workspaces?name_contains=production \
  -H 'Authorization: Bearer <your_token>'
```

## Error Responses

### 401 Unauthorized

```json
{
  "detail": "Invalid authentication credentials"
}
```

**Cause:** Missing or invalid Operator Bearer Token

**Solution:** Ensure you're using a valid operator token in the Authorization header

### 404 Not Found

```json
{
  "detail": "Workspace not found"
}
```

**Cause:** The specified workspace_id does not exist

**Solution:** Verify the workspace ID and ensure it belongs to your organization

### 422 Validation Error

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
