---
plan: all
---

# API keys

API keys authenticate clients that use the [Airbyte model](../interfaces/model/readme.md), the natural language interface. Create and manage them on the **API Keys** page in the web app.

:::note Public alpha

The Airbyte model is in public alpha. Its behavior, limits, and setup steps can change.

:::

Other interfaces don't use these keys. The [MCP server](../interfaces/mcp/readme.md) authenticates in your browser, and the [API](../interfaces/api/readme.md), [SDK](../interfaces/sdk/readme.md), and [CLI](../interfaces/cli/readme.md) use your organization's client ID and secret. See [Profile](./profile.md#api-credentials).

## Keys are scoped to a workspace

Each key belongs to one workspace, and clients using it can only query the connectors authenticated in that workspace. To query connectors in two workspaces, create a key for each. If you have more than one workspace, verify you're creating the key in the one that holds the data you want. See [Workspaces](../concepts/architecture/workspaces.md).

You can only create keys for workspaces you have access to, and you can have up to 10 active keys in each workspace. Two active keys in the same workspace can't share a name, but a name is free to reuse once you revoke the key that held it.

## Create a key

1. Click **Settings**, then click **API Keys**.

2. Click **Create API key**.

3. Enter a **Name** that identifies where you'll use the key, like `codex-laptop`.

4. Select the **Workspace** the key can query.

5. Select an **Expiration**: 1, 7, 30, 60, or 90 days, measured from the moment you create the key. Airbyte emails you 14 days and 3 days before a key expires.

6. Click **Create key**.

7. Copy the key and store it somewhere safe. Airbyte shows the full key once. After you close the dialog, you can't retrieve it.

The same dialog includes setup snippets for Codex, Claude Code, and pydantic-AI with your new key already in place. To see those snippets again later with a placeholder in place of the key, click **Setup instructions**.

## Review keys

The **API Keys** page lists your keys with their workspace, creator, creation date, expiration, last use, and status. Only the key's prefix and last four characters are shown. If you're an organization administrator, you see every key in the organization. Otherwise, you see the keys you created.

A key's status is one of the following.

| Status | Meaning |
| --- | --- |
| **Active** | The key works. |
| **Expiring soon** | The key expires within 14 days. Create a replacement. |
| **Expired** | The key passed its expiration and no longer authenticates. |
| **Revoked** | Someone revoked the key. |

## Revoke a key

Revoke a key when it's no longer needed, or immediately if it might be exposed.

1. Click **Settings**, then click **API Keys**.

2. Find the key and click the revoke icon.

3. Click **Revoke key**.

Clients using that key lose access right away, and you can't undo this. If you're unsure whether a key is still in use, check its last-used date first.

You can revoke keys you created. Organization administrators can revoke any key in the organization.

## Keep keys safe

- Treat a key like a password. Anyone with it can read data from the connectors in its workspace.
- Store keys in environment variables or a secret manager. Don't commit them to source control or paste them into configuration files you share.
- Create one key per client or machine so you can revoke a single key without disrupting anything else.
- Pick the shortest expiration you can work with.
