---
plan: all
sidebar_position: 2
---

# Workspaces

A workspace is an isolation boundary within an [organization](./organizations). Each workspace holds its own set of connectors and credentials. A token scoped to one workspace cannot access connectors in another.

## The default workspace

Every organization starts with a workspace named `default`. Most people use this single workspace and never need to create additional ones. The web app, SDK, API, and MCP server all target the `default` workspace unless you specify otherwise.

## When to create additional workspaces

Create additional workspaces when you need to isolate credentials across distinct boundaries. Common scenarios include:

- **Multi-tenant SaaS** — Give each of your customers their own workspace so their credentials and data stay separate.
- **Team isolation** — Separate engineering, sales, and support connectors into their own workspaces.
- **Environment separation** — Use different workspaces for development, staging, and production.

If none of these apply, the `default` workspace is all you need.

## Workspace identifiers

Every workspace has two identifiers:

- **UUID** (`id`) — An Airbyte-assigned identifier that never changes. Persist this in your backend and use it for any operation that accepts a `workspace_id`.
- **Name** (`workspace_name`) — A human-readable label you choose when the workspace is created. Routing endpoints like scoped-token minting and connector creation accept the name as a lookup key.

The UUID is the durable identifier. The name is a convenience for routing, but it must still be unique within an organization.

## Create a workspace

Workspaces are created programmatically through the API or SDK — they can't be created through the web app. The first time you mint a [scoped token](../../interfaces/api/authentication#scoped-token) against a new `workspace_name`, Airbyte creates the workspace for you. Use any stable string that makes sense in your app — for example, an internal tenant ID or team slug.

## Scoped tokens

A scoped token limits access to a single workspace. If you just use the `default` workspace (most cases), you can skip scoped tokens entirely and authenticate with an [application token](../../interfaces/api/authentication#application-token). Generate a scoped token when you need to hand a token to a component that should only see one workspace's connectors.

For details on generating and using scoped tokens, see [Authentication](../../interfaces/api/authentication#scoped-token).

## Manage workspaces

Workspace management — listing, updating, and deleting workspaces — is available through the API. The SDK `Workspace` class covers day-to-day operations like listing connectors and executing operations.

- [Manage workspaces (API)](../../interfaces/api/workspaces) — List, update, and delete workspaces.
- [Manage workspaces (SDK)](../../interfaces/sdk/workspaces) — Target a workspace, list connectors, and execute operations.

## Related topics

- [Organizations](./organizations) — The parent container for all workspaces.
- [Connectors and credentials](./connectors-and-credentials) — What lives inside a workspace.
- [Authentication](../../interfaces/api/authentication) — Application tokens, scoped tokens, and the token hierarchy.
