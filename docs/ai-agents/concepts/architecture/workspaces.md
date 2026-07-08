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

- **Multi-tenant SaaS**: Give each of your customers their own workspace so their credentials and data stay separate.
- **Team isolation**: Separate engineering, sales, and support connectors into their own workspaces.
- **Environment separation**: Use different workspaces for development, staging, and production.

If none of these apply, the `default` workspace is all you need.

## Workspace identifiers

Every workspace has two identifiers:

- **UUID** (`id`): An Airbyte-assigned identifier that never changes. Persist this in your backend and use it for any operation that accepts a `workspace_id`.
- **Name** (`workspace_name`): A human-readable label you choose when the workspace is created. Routing endpoints like scoped-token minting and connector creation accept the name as a lookup key.

The UUID is the durable identifier. The name is a convenience for routing, but it must still be unique within an organization.

## Create a workspace

There are two ways to create a workspace:

- **Web app** ([Team and Custom plans](../../admin/billing.md#team)): Only administrators can create workspaces. Open the workspace picker in the sidebar, click **New workspace**, enter a name, pick a color, and click **Create**. Airbyte switches you to the new workspace and adds you as a member automatically.
- **API**: The first time you mint a [scoped token](../../interfaces/api/authentication#scoped-token) against a new `workspace_name`, Airbyte creates the workspace for you. Use any stable string that makes sense in your app, for example an internal tenant ID or team slug.

## Workspace properties

Each workspace has the following properties:

- **Name**: A human-readable label, unique within the organization. You can rename a workspace later, except the default workspace.
- **Color**: A swatch chosen from a fixed palette. The color appears next to the workspace name in the picker and helps you tell workspaces apart at a glance.
- **Context Store region**: Where the workspace's [Context Store](../context-store) data is stored. This is currently the United States for every workspace and can't be changed.

## Scoped tokens

A scoped token limits access to a single workspace. If you just use the `default` workspace (most cases), you can skip scoped tokens entirely and authenticate with an [application token](../../interfaces/api/authentication#application-token). Generate a scoped token when you need to hand a token to a component that should only see one workspace's connectors.

For details on generating and using scoped tokens, see [Authentication](../../interfaces/api/authentication#scoped-token).

## Workspace membership

On [Team and Custom plans](../../admin/billing.md#team), administrators control which workspaces each member can access.

- **Administrators** can see and manage every workspace in the organization. They always keep access to every workspace and can't be removed as members.
- **Members** can be added to specific workspaces by an administrator. A member sees only the workspaces they belong to.

Everyone in the organization has access to the `default` workspace. This can't be changed.

Chats and connectors are shared within a workspace: any member of a workspace can view, use, and edit the connectors it contains. Workspace membership is what lets administrators control who can access which set of chats and connectors.

## Manage workspaces

Administrators manage workspaces from the workspace picker in the sidebar. Open the picker, hover a workspace, and use the edit or delete controls. Non-administrators don't see these controls, and the `default` workspace can't be edited or deleted.

### Edit a workspace

Click the edit (pencil) icon next to a workspace to open its settings. You can:

- **Rename** the workspace and change its **color**.
- **Manage members**: add any active organization member, or remove a member you added earlier. Administrators always appear as members and can't be removed. Search by name or email to find people.

Click **Save** to apply your changes. The Context Store region is fixed and can't be edited.

To grab a workspace's ID for use in API calls, open the picker and use the **Copy workspace ID** control on the workspace's row. You don't need to open the edit dialog to do this.

### Delete a workspace

Click the delete (trash) icon next to a workspace, then type the workspace name to confirm. Deleting a workspace permanently removes the workspace along with all chats and connectors inside it. This can't be undone.

Historical [session](../../admin/sessions.md) and [tool call](../../admin/tool-calls.md) records that ran in a deleted workspace are preserved, but the workspace no longer appears as a place you can open or add connectors to.

### Programmatic access

Workspace management is also available through the [API](../../interfaces/api/workspaces). The [SDK `Workspace` class](../../interfaces/sdk/workspaces) covers day-to-day operations like listing connectors and executing operations.

- [Manage workspaces (API)](../../interfaces/api/workspaces): List, update, and delete workspaces.
- [Manage workspaces (SDK)](../../interfaces/sdk/workspaces): Target a workspace, list connectors, and execute operations.

## Related topics

- [Organizations](./organizations): The parent container for all workspaces.
- [Connectors and credentials](./connectors-and-credentials): What lives inside a workspace.
- [Authentication](../../interfaces/api/authentication): Application tokens, scoped tokens, and the token hierarchy.
