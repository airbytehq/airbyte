---
sidebar_position: 4
---

# Manage workspaces

:::note API-only operations
Listing every workspace, updating a workspace's status, deleting a workspace, and reading workspace metadata are exposed through the API only. The [SDK's workspace class](../sdk/workspaces) covers what most apps need day-to-day; come here for the administrative operations on top.
:::

A **workspace** is a container inside your Airbyte Agents organization that holds a set of connectors and credentials. Every organization starts with a `default` workspace, and most apps stay there. Create additional workspaces only when you need to isolate credentials across distinct tenants, teams, or environments.

Every request that touches a connector carries the workspace it belongs to. In the REST body that's `customer_name`; in a scoped or widget token request it's `workspace_name`. Airbyte uses the value as the workspace identifier and creates the workspace on first use.

## Create a new workspace

You don't create workspaces directly. Airbyte creates one automatically the first time you reference a new `workspace_name` when generating a [scoped token](./authentication#scoped-token), or a new `customer_name` when creating a connector. Use any stable string that makes sense in your app.

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

- Pick a naming convention for `workspace_name` up front and stick with it. Airbyte uses whatever string you first pass, so picking a stable identifier now avoids orphaned workspaces later.

- Handle token expiration appropriately. Application tokens expire after 15 minutes and scoped tokens expire after 20 minutes.

- Use the workspace status to manage the workspace lifecycle. Setting a workspace to `inactive` is a clean way to suspend access without deleting data.
