---
plan: all
sidebar_position: 3
---

# Add a connector

Before an Airbyte agent can read from or write to a data source, someone has to authenticate that source for the workspace. In the web app, that happens on the **Connectors** page. Adding a connector means picking a workspace, picking a data source, and completing an authentication flow once; after that, every interface you use (Chats, the SDK, the API, and the MCP server) can use the resulting connector.

This page walks through adding connectors end-to-end: where to add them, how to add them from inside a chat, how workspaces and multiple connectors fit together, and how to update or remove connectors you've already added.

## What "adding a connector" means

It helps to separate two ideas that both get called "a connector":

- A **connector type**, like GitHub, Salesforce, or Google Drive. These come from the [Airbyte connector catalog](../../connectors) and are the same for every organization.
- A **connector** you've added to a workspace. This is a connector type plus real credentials (an OAuth token, an API key, a service-account file) that Airbyte can use to make calls.

When this doc says "add a connector," it means the second thing: creating an authenticated instance of a connector type inside one of your workspaces. Once it exists, any Chat or external client that runs in the same workspace can use it without re-authenticating.

Adding a connector is a one-time setup step per workspace. You don't need to pick a "mode" or opt into specific use cases. The same connector is available to agents in Chats, the [SDK](../sdk), the [API](../api), the [CLI](../cli), and the [MCP server](../mcp).

## Workspaces and connectors

A **workspace** is the scope that a connector lives in. Every organization starts with a `default` workspace, and on the [Team and Custom plans](../../admin/billing.md#team) administrators can create more. Use workspaces to separate credentials that shouldn't mix. For example, separate production data from sandbox data, or one customer's credentials from another customer's.

Connectors are shared within a workspace. Any user with access to the workspace can use a connector in chats, and can edit or delete it. Keep this in mind when you add credentials to a shared workspace.

A workspace can hold as many connectors as you need:

- Connectors of different types. A workspace might have GitHub, Linear, and Salesforce connectors side by side so a single agent can answer cross-system questions.
- Multiple connectors of the same type. For example, two GitHub connectors for different organizations, or one Salesforce connector for a sandbox and one for production. Airbyte keeps them separate and the agent picks among them based on your prompt and [context](./chats#context).

Each Chat runs in one workspace at a time and sees only the connectors in that workspace. If you can't find a connector you expect, check that you're in the right workspace.

## Add a connector from the Connectors page

The Connectors page is the primary place to add, view, and manage connectors for every workspace in your organization. This is the right flow when you're setting up a new workspace, onboarding a data source before you need it, or adding a second account for a connector type you already use.

1. Click **Connectors** in the left sidebar.

2. Click **Add Connector** in the top right. A slide-out panel opens.

3. Under **Select Workspace**, pick the workspace the connector should belong to. To create a new workspace on the fly, click **+ Add new workspace** and give it a name.

4. Under **Select a connector to add credentials for**, browse or search for the data source you want, then click its tile.

5. Airbyte opens the authentication module for that connector in a dialog. Complete the flow it asks for: typically an OAuth consent screen, or a short form for API keys and endpoint URLs. Refer to the connector's [setup guide](../../connectors) if you're not sure what a field expects.

6. When authentication finishes, the dialog closes and a **Credential Added** confirmation appears in the slide-out. From there you can click **Add Another Credential** to add more, or **Chat with your Agent** to jump straight into a Chat that uses the new connector.

The new connector appears immediately in the Connectors list and in the **Available context** list on the Chat landing page. You don't need to reload other tabs.

## OAuth versus access tokens {#oauth-vs-tokens}

### OAuth

In an OAuth flow, the third-party service asks you to authorize Airbyte to act on your behalf. For connectors that publish OAuth scope metadata, the entity picker shows **Read** and **Write** columns, and you can select access per entity. Your selections map to the narrowest set of OAuth scopes that covers what you chose, and the third-party service enforces those scopes on every request the connector makes.

The result is granular, read/write scope control. The connector can only reach the entities and operations the service agreed to, and you can see what you consented to in the authorization dialog.

### Access tokens and personal access tokens (PATs)

When you paste an access token, API key, or PAT into the form, you're handing Airbyte a credential that already carries whatever permissions you assigned to it on the third-party side. Airbyte has no way to narrow that credential. The token grants access to data, but Airbyte can't see what data.

In token mode, selecting entities controls what Airbyte replicates into the [Context Store](../../concepts/context-store), not what the token can reach. The entity picker shows a single **Include** column. There are no read/write modes, because the mode isn't Airbyte's to enforce. If you need to keep the connector away from a piece of data, restrict the token itself on the third-party service before you paste it in.

### Why the entity list can differ

The list of entities the picker shows can differ between the two authentication methods:

- In OAuth mode, the picker shows every entity the connector knows about, including write-only ones, because OAuth scopes can express write-only access.
- In token mode, the picker hides write-only entities, because selecting one wouldn't put anything into the Context Store.

This is by design, not a bug. A different entity list doesn't mean one method gives you less data than the other. The connector can still read the same underlying entities from the third-party service. In token mode the picker just limits itself to the entities you can actually replicate, so the options you see match the outcome you get and the UI doesn't imply a level of access control Airbyte can't enforce.

## Add a connector during a Chat

You don't have to add connectors up front. If you start a Chat and the agent realizes it needs a data source it doesn't have, it can ask you to authenticate one inline without leaving the conversation.

When this happens, the agent's message includes one or more connector tiles next to its reply. Each tile shows the connector's logo, name, and current status. To authenticate:

1. Click the tile for the connector you want to connect. The authentication module opens in a dialog, the same flow the Connectors page uses.

2. Complete the OAuth or API-key flow. When it finishes, the tile flips to a success state.

3. If the agent requested more than one connector, repeat for each tile you want to authenticate. Click **Skip** on any tile you don't want to add right now.

4. Once you've handled the tiles you care about, the agent picks up the new connectors automatically and continues its response.

Anything you add through this inline flow is saved to the workspace the Chat is running in, just like connectors added from the Connectors page. It's visible afterward in the Connectors list and usable by other Chats in the same workspace.

If you'd rather not add a connector inline (for example, because you want to pick a different workspace, or because you need to finish authentication elsewhere first), you can also open the **Connectors** page in another tab, add the connector there, then come back to the Chat. Send the agent a short message like "try again" and it re-reads the available context and picks up the new connector on its next turn.

## Manage existing connectors

The Connectors page also shows every connector that's already been added across every workspace. Use it to audit what's authenticated, see how much each connector is being used, and retire ones you no longer need.

- **Filter the list**. Use the **All workspaces** and **All connectors** filters at the top of the table to narrow the list by workspace or connector type.

- **Open a connector's detail page**. Click **Details** on a row to open the connector's detail page. The page shows the connector's metadata (connector ID, workspace, and when it was created and last used), its [Context Store](../../concepts/context-store) entities, and an **Activity** section with the agent-request history for that connector, including which tool calls hit it, when, and whether they succeeded. Filter the Activity list by request type (**Direct API** or **Search**) and status, and page through older requests.

- **Re-authenticate a connector**. If credentials expire or get revoked on the third-party side, click the pencil icon on a row, or **Edit** on the connector detail page, to re-launch the authentication module and update them. The connector keeps its identity, so Chats that reference it don't need to be rewired.

- **Remove a connector**. Click the trash icon on a row, or **Delete** on the connector detail page, to delete that connector. The credential is removed from the workspace immediately. Any Chat that was relying on it needs a replacement connector, or a different approach, the next time it runs.

You don't have to turn off a connector before deleting it, and there's no minimum number of connectors per workspace. An empty workspace is a valid state. It just means no agent running in it can reach external data.

## Doing this without the web app

Everything on this page has programmatic equivalents:

- Use the [API](../api/add-connector) to create, update, and delete connectors from a script or backend service.
- Use the [SDK](../sdk) to manage connectors from Python code, including inside your own agent implementations.
- Use the [MCP server](../mcp) to expose an authenticated connector to any MCP-compatible client.

All three act on the same underlying connectors, so a connector added in the web app is immediately usable from the API, SDK, and MCP server, and vice versa.
