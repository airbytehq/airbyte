---
products: embedded
---

# Workspace Management

Workspaces in Airbyte Embedded represent isolated environments for each of your end users. Each workspace contains its own sources, connections, and configurations, ensuring complete data isolation between your customers.

## Overview

A workspace is automatically created when you generate a [scoped token](./authentication.md#scoped-token) or [widget token](./authentication.md#widget-token) for a user. However, you may need to manage workspaces directly for operations like:

- Listing all end-user workspaces
- Updating workspace names or status
- Deactivating workspaces for churned customers
- Synchronizing workspace data from Airbyte Cloud
- Getting workspace statistics

## Authentication

All workspace management endpoints require an [Access Token](./authentication.md#access-token-operator-token) with organization admin permissions.

```
Authorization: Bearer {access-token}
```

## List Workspaces

Retrieve a paginated list of workspaces in your organization.

### Endpoint

```
GET /api/v1/workspaces
```

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 20 | Number of workspaces per page (1-100) |
| `cursor` | string | No | - | Pagination cursor from previous response |
| `name_contains` | string | No | - | Filter by workspace name (case-insensitive partial match) |
| `status` | enum | No | - | Filter by status: `active` or `inactive` |

### Request Example

```bash
curl -X GET "https://api.airbyte.ai/api/v1/workspaces?limit=50&name_contains=demo&status=active" \
  -H "Authorization: Bearer your-access-token" \
  -H "X-Organization-Id: your-org-id"
```

### Response

```json
{
  "data": [
    {
      "workspace_id": "789e0123-e45b-67c8-d901-234567890abc",
      "name": "demo-user-workspace",
      "organization_id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "active",
      "created_at": "2025-09-15T10:30:00Z",
      "updated_at": "2025-10-01T14:22:00Z"
    },
    {
      "workspace_id": "456e0789-e01b-23c4-d567-890123456def",
      "name": "demo-user-2-workspace",
      "organization_id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "active",
      "created_at": "2025-09-20T08:15:00Z",
      "updated_at": "2025-09-20T08:15:00Z"
    }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6IjQ1NmUwNzg5LWUwMWItMjNjNC1kNTY3LTg5MDEyMzQ1NmRlZiJ9",
    "has_more": true
  }
}
```

### Pagination

Use cursor-based pagination to iterate through all workspaces:

```bash
# First request
curl -X GET "https://api.airbyte.ai/api/v1/workspaces?limit=20" \
  -H "Authorization: Bearer your-access-token"

# Subsequent request using cursor from previous response
curl -X GET "https://api.airbyte.ai/api/v1/workspaces?limit=20&cursor=eyJpZCI6IjQ1NmUwNzg5..." \
  -H "Authorization: Bearer your-access-token"
```

Continue fetching pages while `pagination.has_more` is `true`.

## Get Workspace

Retrieve details for a single workspace.

### Endpoint

```
GET /api/v1/workspaces/{workspace_id}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspace_id` | UUID | Yes | The workspace ID to retrieve |

### Request Example

```bash
curl -X GET "https://api.airbyte.ai/api/v1/workspaces/789e0123-e45b-67c8-d901-234567890abc" \
  -H "Authorization: Bearer your-access-token" \
  -H "X-Organization-Id: your-org-id"
```

### Response

```json
{
  "workspace_id": "789e0123-e45b-67c8-d901-234567890abc",
  "name": "demo-user-workspace",
  "organization_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "active",
  "created_at": "2025-09-15T10:30:00Z",
  "updated_at": "2025-10-01T14:22:00Z"
}
```

## Update Workspace

Update a workspace's name or status.

### Endpoint

```
PUT /api/v1/workspaces/{workspace_id}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspace_id` | UUID | Yes | The workspace ID to update |

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | No | New workspace name |
| `status` | enum | No | New status: `active` or `inactive` |

### Request Example: Rename Workspace

```bash
curl -X PUT "https://api.airbyte.ai/api/v1/workspaces/789e0123-e45b-67c8-d901-234567890abc" \
  -H "Authorization: Bearer your-access-token" \
  -H "X-Organization-Id: your-org-id" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "new-workspace-name"
  }'
```

### Request Example: Deactivate Workspace

```bash
curl -X PUT "https://api.airbyte.ai/api/v1/workspaces/789e0123-e45b-67c8-d901-234567890abc" \
  -H "Authorization: Bearer your-access-token" \
  -H "X-Organization-Id: your-org-id" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "inactive"
  }'
```

### Response

```json
{
  "workspace_id": "789e0123-e45b-67c8-d901-234567890abc",
  "name": "new-workspace-name",
  "organization_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "active",
  "created_at": "2025-09-15T10:30:00Z",
  "updated_at": "2025-10-08T16:45:00Z"
}
```

### Workspace Status

**Active Workspaces:**
- Sources can be configured and connections can run
- Scoped tokens can access workspace resources
- Normal operation

**Inactive Workspaces:**
- All connections are automatically disabled
- Sources remain but cannot sync
- Scoped tokens still authenticate but operations may be restricted
- Useful for pausing service for non-paying customers

## Delete Workspace

Delete a workspace. This is a soft delete - the workspace is marked as deleted but data is retained for recovery.

### Endpoint

```
DELETE /api/v1/workspaces/{workspace_id}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspace_id` | UUID | Yes | The workspace ID to delete |

### Request Example

```bash
curl -X DELETE "https://api.airbyte.ai/api/v1/workspaces/789e0123-e45b-67c8-d901-234567890abc" \
  -H "Authorization: Bearer your-access-token" \
  -H "X-Organization-Id: your-org-id"
```

### Response

```json
{
  "workspace_id": "789e0123-e45b-67c8-d901-234567890abc",
  "deleted": true
}
```

### Important Notes

- This is a **soft delete** - workspace data is retained for recovery
- All connections in the workspace are disabled
- Sources remain but cannot sync
- Contact Airbyte support for hard deletion or recovery

## Get Workspace Statistics

Get aggregate statistics about workspaces in your organization.

### Endpoint

```
GET /api/v1/workspaces/stats
```

### Request Example

```bash
curl -X GET "https://api.airbyte.ai/api/v1/workspaces/stats" \
  -H "Authorization: Bearer your-access-token" \
  -H "X-Organization-Id: your-org-id"
```

### Response

```json
{
  "total_workspaces": 150,
  "active_workspaces": 142,
  "inactive_workspaces": 8,
  "workspaces_with_sources": 138,
  "workspaces_with_active_connections": 125
}
```

### Use Cases

- Dashboard metrics for your admin panel
- Monitoring workspace growth
- Identifying inactive workspaces for cleanup
- Usage analytics

## Sync Workspaces

Synchronize workspace data from Airbyte Cloud to your local Sonar database. This is useful if workspaces were created outside of Sonar (e.g., directly in Airbyte Cloud).

### Endpoint

```
POST /api/v1/workspaces/sync
```

### Request Example

```bash
curl -X POST "https://api.airbyte.ai/api/v1/workspaces/sync" \
  -H "Authorization: Bearer your-access-token" \
  -H "X-Organization-Id: your-org-id"
```

### Response

```json
{
  "total_found": 150,
  "created_locally": 8,
  "already_existed": 142
}
```

### When to Use

- After creating workspaces directly in Airbyte Cloud
- Periodic synchronization to ensure data consistency
- Migration or data recovery scenarios

### Notes

- Only workspaces belonging to your organization are synced
- Existing workspace data is not overwritten
- This operation is idempotent - safe to run multiple times

## Common Use Cases

### 1. List All Workspaces for Admin Dashboard

```javascript
const response = await fetch('https://api.airbyte.ai/api/v1/workspaces?limit=100', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'X-Organization-Id': organizationId
  }
});

const { data: workspaces } = await response.json();

// Display in admin dashboard
workspaces.forEach(workspace => {
  console.log(`${workspace.name}: ${workspace.status}`);
});
```

### 2. Search for a User's Workspace

```bash
curl -X GET "https://api.airbyte.ai/api/v1/workspaces?name_contains=user-12345" \
  -H "Authorization: Bearer your-access-token"
```

### 3. Deactivate Workspace for Churned Customer

```javascript
// When a customer cancels their subscription
async function deactivateCustomerWorkspace(workspaceId) {
  const response = await fetch(
    `https://api.airbyte.ai/api/v1/workspaces/${workspaceId}`,
    {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'X-Organization-Id': organizationId,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: 'inactive' })
    }
  );

  return response.json();
}
```

### 4. Bulk Status Update

```javascript
// Deactivate all workspaces for non-paying customers
async function deactivateInactiveCustomers(workspaceIds) {
  const promises = workspaceIds.map(id =>
    fetch(`https://api.airbyte.ai/api/v1/workspaces/${id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'X-Organization-Id': organizationId,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: 'inactive' })
    })
  );

  return Promise.all(promises);
}
```

### 5. Pagination Through All Workspaces

```javascript
async function getAllWorkspaces() {
  const allWorkspaces = [];
  let cursor = null;
  let hasMore = true;

  while (hasMore) {
    const url = cursor
      ? `https://api.airbyte.ai/api/v1/workspaces?limit=100&cursor=${cursor}`
      : 'https://api.airbyte.ai/api/v1/workspaces?limit=100';

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'X-Organization-Id': organizationId
      }
    });

    const result = await response.json();
    allWorkspaces.push(...result.data);

    cursor = result.pagination?.next_cursor;
    hasMore = result.pagination?.has_more || false;
  }

  return allWorkspaces;
}
```

## Error Responses

### 404 Not Found

Workspace does not exist or doesn't belong to your organization:

```json
{
  "error": "Not Found",
  "message": "Workspace not found"
}
```

### 400 Bad Request

Invalid request parameters:

```json
{
  "error": "Bad Request",
  "message": "Invalid limit value: must be between 1 and 100"
}
```

### 401 Unauthorized

Missing or invalid access token:

```json
{
  "error": "Unauthorized",
  "message": "Invalid bearer token"
}
```

### 403 Forbidden

User lacks organization admin permissions:

```json
{
  "error": "Forbidden",
  "message": "User must be an organization admin"
}
```

## Best Practices

### Workspace Naming Convention

Use a consistent naming scheme for workspace names:

```
{environment}-{customer-id}-workspace
```

Examples:
- `prod-customer-123-workspace`
- `staging-customer-456-workspace`

This makes it easy to:
- Search for workspaces by customer ID
- Identify environment (prod vs. staging)
- Maintain consistent organization

### Workspace Lifecycle Management

1. **Creation:** Automatically created via token generation
2. **Active Use:** Monitor with workspace statistics endpoint
3. **Deactivation:** Set status to `inactive` for churned customers
4. **Deletion:** Soft delete after grace period, contact support for hard delete

### Monitoring

Regularly check workspace statistics to:
- Track growth in customer count
- Identify workspaces without sources (onboarding incomplete)
- Find inactive workspaces for cleanup
- Monitor workspace creation trends

### Performance Tips

- Use pagination with reasonable limits (20-50) for optimal performance
- Cache workspace lists on your backend to reduce API calls
- Use `name_contains` filter instead of fetching all workspaces when searching
- Filter by status to focus on active workspaces only

## Related Resources

- [Authentication](./authentication.md) - Learn about access tokens and scoped tokens
- [Configuring Sources](./configuring-sources.md) - Manage sources within workspaces
- [API Reference](https://api.airbyte.ai/api/v1/docs) - Complete API documentation
