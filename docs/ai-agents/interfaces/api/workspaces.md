---
sidebar_position: 4
---

# Manage workspaces

:::note API-only operations
Listing every workspace, updating a workspace's status, deleting a workspace, and reading workspace metadata are exposed through the API only. The [SDK's workspace class](../sdk/workspaces) covers everything an end-user-scoped app needs; come here for the administrative operations on top.
:::

In Airbyte Agents, a **workspace** represents an end-user of your service who connects their own data sources. Each workspace gets an isolated environment that stores their credentials, connectors, and data separately from other workspaces.

The `workspace_name` you provide when creating scoped tokens serves as the unique workspace identifier within your organization. Use any string that makes sense for your service, like an internal user ID or company name.

## Why workspaces exist

Airbyte Agents uses the workspace concept to provide data isolation in multi-tenant applications.

Airbyte isolates each workspace's data, credentials, and configurations. A [scoped token](./authentication#scoped-token) can only access a single workspace. Workspace data never crosses the workspace boundary. This architecture means you can safely serve multiple end-users from a single Airbyte Agents organization without worrying about data leakage between workspaces.

## Workspaces and authentication

Airbyte Agents uses a hierarchical token system where each token type has a different scope. For complete details on token types and how to generate them, see [Token types](./authentication#token-types).

## Create a new workspace

You create a new workspace when you generate a scoped token with a new `workspace_name`. If the workspace doesn't exist, Airbyte creates it automatically.

```bash title="Request"
curl -X POST https://api.airbyte.ai/api/v1/account/applications/scoped-token \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_name": "acme_corp"
  }'
```

The response contains a scoped token you can use for all operations on behalf of this workspace:

```json title="Response"
{
  "token": "eyJhbGci..."
}
```

## Manage workspaces

Use these endpoints to manage workspaces programmatically. All workspace management endpoints require an application token.

### List workspaces

Retrieve all workspaces in your organization.

```bash
curl https://api.airbyte.ai/api/v1/workspaces \
  -H 'Authorization: Bearer <your_operator_token>'
```

You can filter workspaces by name and status.

```bash
curl 'https://api.airbyte.ai/api/v1/workspaces?name_contains=acme&status=active' \
  -H 'Authorization: Bearer <your_operator_token>'
```

### Get workspace details

Retrieve details for a specific workspace:

```bash
curl https://api.airbyte.ai/api/v1/workspaces/<workspace_id> \
  -H 'Authorization: Bearer <your_operator_token>'
```

### Get workspace info from a scoped token

If you have a scoped token and need to retrieve the associated workspace information:

```bash
curl https://api.airbyte.ai/api/v1/account/applications/scoped-token/info \
  -H 'Authorization: Bearer <scoped_token>'
```

### Update a workspace

Update a workspace's name or status.

```bash
curl -X PUT https://api.airbyte.ai/api/v1/workspaces/<workspace_id> \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Acme Corp - Enterprise",
    "status": "active"
  }'
```

Setting status to `inactive` automatically disables all connections in that workspace.

### Delete a workspace

Delete a workspace and all associated resources:

```bash
curl -X DELETE https://api.airbyte.ai/api/v1/workspaces/<workspace_id> \
  -H 'Authorization: Bearer <your_operator_token>'
```

## Best practices

- Use meaningful, consistent naming for `workspace_name`. Your internal user ID or company name works well, and makes it easy to correlate Airbyte Agents workspaces with your own records.

- Handle token expiration appropriately. Application tokens expire after 15 minutes and scoped tokens expire after 20 minutes.

- Use the workspace status to manage the workspace lifecycle. Setting a workspace to `inactive` is a clean way to suspend access without deleting data.
