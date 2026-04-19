# Devin AI

<HideInUI>

This page contains the setup guide and reference information for the [Devin AI](https://devin.ai/) source connector.

</HideInUI>

[Devin AI](https://devin.ai/) is an AI software engineering agent built by Cognition. The Devin AI source connector syncs data from the [Devin API (v3)](https://docs.devin.ai/api-reference/overview), providing visibility into your organization's sessions, conversations, playbooks, secrets metadata, and knowledge base.

## Prerequisites

- A Devin AI account with a [service user](https://docs.devin.ai/api-reference/authentication) configured for API access
- A Devin AI API token (starts with `cog_`)
- Your Devin AI Organization ID (starts with `org_`)

### Required permissions

The service user's role must include the following permissions:

| Permission | Required for |
|---|---|
| `ViewOrgSessions` | Sessions, Session Messages |
| `ViewOrgPlaybooks` | Playbooks |
| `ViewOrgSecrets` | Secrets |
| `ViewOrgKnowledge` | Knowledge Notes |

## Setup guide

### Step 1: Create a service user and generate an API token

1. Log in to your [Devin AI dashboard](https://app.devin.ai/).
2. Navigate to **Settings** > **Service Users**.
3. Click **Create Service User** and assign a role that includes the permissions listed in [Required permissions](#required-permissions).
4. Copy the generated API token. It starts with `cog_` and is displayed only once.

For more information, see the [Devin AI authentication documentation](https://docs.devin.ai/api-reference/authentication).

### Step 2: Find your Organization ID

Your Organization ID is displayed on the **Settings** > **Service Users** page. It uses the `org_` prefix format.

### Step 3: Configure the connector in Airbyte

1. In the Airbyte UI, navigate to **Sources** and click **+ New source**.
2. Select **Devin AI** from the list of available sources.
3. Enter a **Source name** of your choosing.
4. Enter your **API Token** from Step 1.
5. Enter your **Organization ID** from Step 2.
6. Click **Set up source** and wait for the connection test to complete.

<HideInUI>

## Supported sync modes

The Devin AI source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

## Supported streams

| Stream | Description |
|---|---|
| [Sessions](https://docs.devin.ai/api-reference/v3/sessions/list-sessions) | All Devin sessions in your organization, including status, tags, timestamps, ACU consumption, associated pull requests, and parent/child session relationships. |
| Session Messages | Conversation messages for each session, including message source attribution and timestamps. This is a child stream of Sessions. |
| [Playbooks](https://docs.devin.ai/api-reference/v3/playbooks/list-playbooks) | Reusable playbook definitions, including title, body content, macro triggers, and access controls. |
| [Secrets](https://docs.devin.ai/api-reference/v3/secrets/list-secrets) | Secret metadata only. Secret values are never synced. Includes secret keys, types, sensitivity flags, and access scope. |
| [Knowledge Notes](https://docs.devin.ai/api-reference/v3/notes/enterprise-knowledge-notes) | Organization knowledge base entries, including note content, folder organization, trigger rules, and pinned repository associations. |

## Limitations and troubleshooting

### Session messages volume

The Session Messages stream fetches messages for every session in your organization. Organizations with a large number of sessions may experience long sync times because each session requires a separate API request.

### Rate limiting

The Devin API enforces rate limits. The connector retries rate-limited requests and server errors with exponential back-off, up to 5 times. If you encounter persistent rate limit errors, reduce sync frequency or limit the number of streams you sync.

### Secret values are not synced

The Secrets stream syncs metadata only, such as secret names, types, and access scope. Secret values aren't exposed through the API or synced by this connector.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.1.0 | 2026-04-15 | [74417](https://github.com/airbytehq/airbyte/pull/74417) | Initial release with Sessions, Session Messages, Playbooks, Secrets, and Knowledge Notes streams |

</details>

</HideInUI>
