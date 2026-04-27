---
sidebar_position: 3
---

# Add a connector

Before an Airbyte agent can read from or write to a data source, someone has to authenticate that source for the workspace. In the web app, that happens on the **Credentials** page. Adding a connector means picking a workspace, picking a data source, and completing an authentication flow once; after that, every interface you use—Chats, Automations, the SDK, the API, and the MCP server—can use the resulting connector.

This page walks through adding connectors end-to-end: where to add them, how to add them from inside a chat or the Automation Builder, how workspaces and multiple connectors fit together, and how to update or remove connectors you've already added.

## What "adding a connector" means

It helps to separate two ideas that both get called "a connector":

- A **connector type**, like GitHub, Salesforce, or Google Drive. These come from the [Airbyte connector catalog](../../connectors) and are the same for every organization.
- A **connector** you've added to a workspace. This is a connector type plus real credentials (an OAuth token, an API key, a service-account file) that Airbyte can use to make calls.

When this doc says "add a connector," it means the second thing: creating an authenticated instance of a connector type inside one of your workspaces. Once it exists, any Chat, Automation, or external client that runs in the same workspace can use it without re-authenticating.

Adding a connector is a one-time setup step per workspace. You don't need to pick a "mode" or opt into specific use cases. The same connector is available to agents in Chats, scheduled Automations, the [SDK](../sdk), the [API](../api), and the [MCP server](../mcp).

## Workspaces and connectors

A **workspace** is the scope that a connector lives in. Every organization starts with a `default` workspace and a `Test Environment` workspace, and you can create more. Use workspaces to separate credentials that shouldn't mix—for example, production data from sandbox data, or one customer's credentials from another customer's.

A workspace can hold as many connectors as you need:

- Connectors of different types. A workspace might have GitHub, Linear, and Salesforce connectors side by side so a single agent can answer cross-system questions.
- Multiple connectors of the same type. For example, two GitHub connectors for different organizations, or one Salesforce connector for a sandbox and one for production. Airbyte keeps them separate and the agent picks among them based on your prompt and [context](./chats#context).

Each Chat or Automation runs in one workspace at a time and sees only the connectors in that workspace. If you can't find a connector you expect, check that you're in the right workspace.

## Add a connector from the Credentials page

The Credentials page is the primary place to add, view, and manage connectors for every workspace in your organization. This is the right flow when you're setting up a new workspace, onboarding a data source before you need it, or adding a second account for a connector type you already use.

1. Click **Credentials** in the left sidebar.

2. Click **Add Credential** in the top right. A slide-out panel opens.

3. Under **Select Workspace**, pick the workspace the connector should belong to. To create a new workspace on the fly, click **+ Add new workspace** and give it a name.

4. Under **Select a connector to add credentials for**, browse or search for the data source you want, then click its tile.

5. Airbyte opens the authentication module for that connector in a dialog. Complete the flow it asks for: typically an OAuth consent screen, or a short form for API keys and endpoint URLs. Refer to the connector's [setup guide](../../connectors) if you're not sure what a field expects.

6. When authentication finishes, the dialog closes and a **Credential Added** confirmation appears in the slide-out. From there you can click **Add Another Credential** to add more, or **Chat with your Agent** to jump straight into a Chat that uses the new connector.

The new connector appears immediately in the Credentials table and in the **Available context** list on the Chat and Automation landing pages. You don't need to reload other tabs.

## OAuth versus access tokens {#oauth-vs-tokens}

### OAuth

In an OAuth flow, the third-party service asks you to authorize Airbyte to act on your behalf. For connectors that publish OAuth scope metadata, the entity picker shows **Read** and **Write** columns, and you can select access per entity. Your selections map to the narrowest set of OAuth scopes that covers what you chose, and the third-party service enforces those scopes on every request the connector makes.

The result is granular, read/write scope control. The connector can only reach the entities and operations the service agreed to, and you can see what you consented to in the authorization dialog.

### Access tokens and personal access tokens (PATs)

When you paste an access token, API key, or PAT into the form, you're handing Airbyte a credential that already carries whatever permissions you assigned to it on the third-party side. Airbyte has no way to narrow that credential. The token grants access to data, but Airbyte can't see what data.

In token mode, selecting entities controls what Airbyte replicates into the [Context Store](../../concepts/context-store), not what the token can reach. The entity picker shows a single **Include** column—there are no read/write modes, because the mode isn't Airbyte's to enforce. If you need to keep the connector away from a piece of data, restrict the token itself on the third-party service before you paste it in.

### Why the entity list can differ

The list of entities the picker shows can differ between the two authentication methods:

- In OAuth mode, the picker shows every entity the connector knows about, including write-only ones, because OAuth scopes can express write-only access.
- In token mode, the picker hides write-only entities, because selecting one wouldn't put anything into the Context Store.

This is by design, not a bug. A different entity list doesn't mean one method gives you less data than the other—the connector can still read the same underlying entities from the third-party service. In token mode the picker just limits itself to the entities you can actually replicate, so the options you see match the outcome you get and the UI doesn't imply a level of access control Airbyte can't enforce.

## Add a connector during a Chat

You don't have to add connectors up front. If you start a Chat and the agent realizes it needs a data source it doesn't have, it can ask you to authenticate one inline without leaving the conversation.

When this happens, the agent's message includes one or more connector tiles next to its reply. Each tile shows the connector's logo, name, and current status. To authenticate:

1. Click the tile for the connector you want to connect. The authentication module opens in a dialog, the same flow the Credentials page uses.

2. Complete the OAuth or API-key flow. When it finishes, the tile flips to a success state.

3. If the agent requested more than one connector, repeat for each tile you want to authenticate. Click **Skip** on any tile you don't want to add right now.

4. Once you've handled the tiles you care about, the agent picks up the new connectors automatically and continues its response.

Anything you add through this inline flow is saved to the workspace the Chat is running in, just like credentials added from the Credentials page. It's visible afterward in the Credentials table and usable by other Chats and Automations in the same workspace.

If you'd rather not add a connector inline—for example, because you want to pick a different workspace, or because you need to finish authentication elsewhere first—you can also open the **Credentials** page in another tab, add the connector there, then come back to the Chat. Send the agent a short message like "try again" and it re-reads the available context and picks up the new connector on its next turn.

## Add a connector from the Automation Builder

Automations run without a person sitting in the loop, so every connector an automation uses must be authenticated ahead of time. The [Automation Builder](./automations#the-automation-builder) makes this part of the setup conversation.

The fastest path is to tell the Automation Builder Agent what you want and let it flag missing connectors. Describe the automation in plain language. If a required data source isn't authenticated yet, the agent says so—often with connector tiles right in the chat—exactly like in a regular Chat. Click a tile, authenticate, and continue iterating on the automation. The agent re-reads the workspace context and adjusts its plan once the new connector is available.

You can also ask the Automation Builder Agent to change which connectors the automation uses. Sending a message like "use the Salesforce connector instead" or "add HubSpot" tells it to update the automation's [**Context**](./automations#properties) to match. Airbyte blocks direct edits to the Context list in the Properties panel on purpose, so that the prompt and the connectors it relies on stay in sync.

If you prefer, you can still pre-authenticate everything from the Credentials page first, then open the Automation Builder with the connectors already in place. That path is often faster when you already know exactly which sources the automation needs.

## Manage existing connectors

The Credentials page also shows every connector that's already been added across every workspace. Use it to audit what's authenticated, see how much each connector is being used, and retire ones you no longer need.

- **Filter the list**. Use the **All workspaces** and **All connectors** filters at the top of the table to narrow the list by workspace or connector type.

- **Inspect a connector's history**. Click the clock icon on a row to see an agent-request history for that connector, including which tool calls hit it, when, and what succeeded.

- **Re-authenticate a connector**. If credentials expire or get revoked on the third-party side, click the pencil icon to re-launch the authentication module and update them. The connector keeps its identity, so Chats and Automations that reference it don't need to be rewired.

- **Remove a connector**. Click the trash icon on a row to delete that connector. The credential is removed from the workspace immediately. Any Chat or Automation that was relying on it needs a replacement connector, or a different approach, the next time it runs.

You don't have to turn off a connector before deleting it, and there's no minimum number of connectors per workspace. An empty workspace is a valid state. It just means no agent running in it can reach external data.

## Doing this without the web app

Everything on this page has programmatic equivalents:

- Use the [API](../api/add-connector) to create, update, and delete connectors from a script or backend service.
- Use the [SDK](../sdk) to manage connectors from Python code, including inside your own agent implementations.
- Use the [MCP server](../mcp) to expose an authenticated connector to any MCP-compatible client.

All three act on the same underlying connectors, so a connector added in the web app is immediately usable from the API, SDK, and MCP server, and vice versa.
