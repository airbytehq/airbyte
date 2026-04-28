---
sidebar_position: 4
---

# Manage workspaces

:::note API-only operations
Listing every workspace, updating a workspace's status, deleting a workspace, and reading workspace metadata are exposed through the API only. The [SDK's workspace class](../sdk/workspaces) covers what most apps need day-to-day; come here for the administrative operations on top.
:::

A **workspace** is a container inside your Airbyte Agents organization that holds a set of connectors and credentials. Every organization starts with a `default` workspace, and most apps stay there. Create additional workspaces only when you need to isolate credentials across distinct tenants, teams, or environments.

Every workspace has two identifiers:

- `id`: an Airbyte-assigned UUID that never changes for the lifetime of the workspace. This is the durable identifier. Persist it in your backend.
- `name` (referred to in request bodies as `workspace_name`): a human-readable label you choose. It's also what routing endpoints like [mint a scoped token](./authentication#scoped-token) and [create a connector](./add-connector) accept as a lookup key, so it acts like an identifier in day-to-day use — but it isn't guaranteed to be stable.

:::warning Persist the UUID
Persist each workspace's UUID in your backend when it's created, and reference it — not the name — wherever the API accepts a `workspace_id` (for example, in this page's [Get](#get-workspace-details), [Update](#update-a-workspace), and [Delete](#delete-a-workspace) endpoints). Treat `workspace_name` as a routing convenience, not an identifier.
:::

<!--
AGENTIC-1140: renaming a workspace makes name-keyed reads 404 while
scoped-token mint silently autocreates a brand-new empty workspace
under the old name with a new UUID. The "persist the UUID" guidance
above is the safe path for readers; we don't surface the mint behavior
publicly. Revisit when autocreate is consistent across endpoints and/or
rename rejects reuse of the old name.
-->

## Create a new workspace

You don't create workspaces directly. Airbyte creates one automatically the first time you mint a [scoped token](./authentication#scoped-token) against a new `workspace_name`. Use any stable string that makes sense in your app — for example, an internal tenant ID or team slug.

<!--
AGENTIC-1140: create-connector doesn't autocreate a workspace — it 404s
when the workspace_name is new. Minting a scoped token against that name
is the canonical way to create a workspace, and the paragraph above
already routes readers through that path, so we don't need to call out
the asymmetry publicly. Revisit when autocreate is consistent.
-->

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

```json title="Response"
{
  "id": "<workspace_id>",
  "deleted_at": "2026-04-23T01:32:22.512509Z"
}
```

Deleting a workspace with many connectors and long-lived credentials can take a few seconds. If the server times out with a `504`, retry once — the first call typically finishes in the background.

## Best practices

- Persist each workspace's UUID (`id`) in your backend on creation and reference it wherever the API accepts a `workspace_id`. `workspace_name` is a human-readable label, not a durable identifier — renaming breaks name-keyed requests, as described at the top of this page.

- Handle token expiration appropriately. Application tokens expire after 15 minutes and scoped tokens expire after 20 minutes.

- Use the workspace status to manage the workspace lifecycle. Setting a workspace to `inactive` is a clean way to suspend access without deleting data.
