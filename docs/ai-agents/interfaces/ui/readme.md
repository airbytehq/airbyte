---
plan: all
sidebar_position: 1
---

# Web app

The Airbyte Agents web app at [app.airbyte.ai](https://app.airbyte.ai) is the fastest way to use Airbyte Agents without writing code. Describe what you want in natural language, and Airbyte picks the right connectors, makes the necessary tool calls, and replies with an answer grounded in your data.

Use the web app when you want Airbyte itself to be your agent. For Python agents you build yourself, use the [SDK](../sdk). For agents in any other language, use the [API](../api). For a shell-first workflow, use the [CLI](../cli). For agents that already speak Model Context Protocol, use the [MCP server](../mcp).

## Chats

[**Chats**](./chats) are interactive conversations with an Airbyte agent. Ask a question, iterate on the answer, and explore your data in natural language. Chats are the fastest way to get a one-off answer or prototype an idea.

Every Chat runs against the connectors you've authenticated in your workspace. Manage connectors from the **Connectors** page in the sidebar. For the catalog of available connectors, see [Agent connectors](../../connectors).

## Set up connectors

Administrators can add connectors from the web app.

- [**Add a connector**](./add-connector): Authenticate data sources so agents in Chats and every other interface can use them.
- [**Context Store**](../../concepts/context-store): The searchable replica of select entities from your connected data sources that powers grounded answers and large-scale analytics. The Context Store is always on and requires no configuration.

## Workspaces

On the [Team and Custom plans](../../admin/billing.md#team), a workspace picker appears at the top of the sidebar. Each workspace has a name and a color swatch, and the picker shows which workspace is currently active. Chats and connectors are scoped to the active workspace.

- **Switch workspaces**: Open the picker and select another workspace. Airbyte navigates to that workspace and shows a confirmation toast.
- **Create a workspace** (administrators only): Click **New workspace**, enter a name, and pick a color. The Context Store region is fixed to the United States. Airbyte switches you to the new workspace and adds you as a member.
- **Edit a workspace** (administrators only): Hover a workspace and click the edit icon to rename it, change its color, manage members, or copy its ID.
- **Delete a workspace** (administrators only): Hover a workspace and click the delete icon, then type the name to confirm.

The `default` workspace can't be renamed, recolored, or deleted, and everyone in the organization can access it. See [Workspaces](../../concepts/architecture/workspaces) for details.

## Related administration

Other parts of the web app are covered in [Account and administration](../../admin):

- [Profile](../../admin/profile) for account settings.
- [Users](../../admin/users) for inviting members, assigning roles, and managing workspace access (Team and Custom plans).
- [SSO](../../admin/sso) for single sign-on configuration (Team and Custom plans).
- [Sessions](../../admin/sessions) for the run history of every Chat in your organization.
- [Review tool calls](../../admin/tool-calls) for inspecting and approving deferred tool calls.
- [Billing](../../admin/billing) for plans, usage, and invoices.

import DocCardList from '@theme/DocCardList';

<DocCardList />
