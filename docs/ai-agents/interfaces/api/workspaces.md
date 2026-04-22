---
sidebar_position: 4
---

# Manage workspaces

:::note API-only operations
Listing every workspace, updating a workspace's status, deleting a workspace, and reading workspace metadata are exposed through the API only. The [SDK's workspace class](../sdk/workspaces) covers what most apps need day-to-day; come here for the administrative operations on top.
:::

A **workspace** is a container inside your Airbyte Agents organization that holds a set of connectors and credentials. Every organization starts with a `default` workspace, and most apps stay there. Create additional workspaces only when you need to isolate credentials across distinct tenants, teams, or environments.

Every request that touches a connector carries the workspace it belongs to in a `workspace_name` field. Airbyte treats that string as a stable identifier for the workspace — once a workspace exists under a given name, later requests against the same name always resolve to the same workspace. Renaming a workspace (see [Update a workspace](#update-a-workspace)) changes its display name in list responses but does not change the identifier your backend sends in request bodies; keep using the original `workspace_name`.

## Create a new workspace

You don't create workspaces directly. Airbyte creates one automatically the first time you mint a [scoped token](./authentication#scoped-token) or [widget token](./authentication#widget-token) against a new `workspace_name`. Use any stable string that makes sense in your app — for example, an internal tenant ID or team slug.

:::warning Create-connector does not autocreate
The [create-connector](./add-connector) endpoint does not autocreate workspaces. Calling it with a `workspace_name` Airbyte hasn't seen before fails with `404 "Workspace not found for workspace_name '...'"`. Mint a scoped token (or open the workspace in the Airbyte Agents UI) first.
:::

## Manage workspaces

Use these endpoints to manage workspaces programmatically. All workspace management endpoints require an application token.

### List workspaces

Retrieve all workspaces in your organization.

```bash
curl https://api.airbyte.ai/api/v1/workspaces \
  -H 'Authorization: Bearer <application_token>'
```

You can filter workspaces by name and status.

```bash
curl 'https://api.airbyte.ai/api/v1/workspaces?name_contains=acme&status=active' \
  -H 'Authorization: Bearer <application_token>'
```

```json title="Response"
{
  "next": null,
  "data": [
    {
      "id": "<workspace_id>",
      "name": "default",
      "organization_id": "<organization_id>",
      "status": "active",
      "cache_enabled": null,
      "tombstone": false,
      "created_at": "2026-04-20T21:57:20.991787Z",
      "updated_at": "2026-04-20T21:57:20.991787Z"
    }
  ]
}
```

- `next` is a cursor. Pass its value as a query parameter to page forward; a `null` value means this is the last page.
- `status` is `"active"` or `"inactive"`.
- `tombstone: true` indicates a soft-deleted workspace. Workspaces are filtered to `tombstone: false` by default.
- `cache_enabled` may be `null` if the workspace predates that feature.

### Get workspace details

Retrieve details for a specific workspace:

```bash
curl https://api.airbyte.ai/api/v1/workspaces/<workspace_id> \
  -H 'Authorization: Bearer <application_token>'
```

The response has the same per-workspace shape as each entry in the [List workspaces](#list-workspaces) response.

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
  -H 'Authorization: Bearer <application_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Acme Corp - Enterprise",
    "status": "active"
  }'
```

Setting status to `inactive` automatically disables all connectors in that workspace.

### Delete a workspace

Delete a workspace and all associated resources:

```bash
curl -X DELETE https://api.airbyte.ai/api/v1/workspaces/<workspace_id> \
  -H 'Authorization: Bearer <application_token>'
```

Deleting a workspace with many connectors and long-lived credentials can take a few seconds. If the server times out with a `504`, retry once — the first call typically finishes in the background.

## Best practices

- Pick a naming convention for `workspace_name` up front and stick with it. Airbyte uses whatever string you first pass, so picking a stable identifier now avoids orphaned workspaces later.

- Handle token expiration appropriately. Application tokens expire after 15 minutes and scoped tokens expire after 20 minutes.

- Use the workspace status to manage the workspace lifecycle. Setting a workspace to `inactive` is a clean way to suspend access without deleting data.
