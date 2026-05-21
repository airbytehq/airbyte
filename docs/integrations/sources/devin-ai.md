# Devin AI

This page contains the setup guide and reference information for the [Devin AI](https://devin.ai/) source connector.

## Overview

Syncs data from the [Devin AI](https://devin.ai) platform API (v3), providing visibility into your organization's AI engineering agent activity, conversations, and configuration.

- **Sessions** — All Devin sessions in your organization
  - Session status, title, tags, and timestamps
  - ACU consumption and billing-relevant metrics
  - Associated pull requests with PR state
  - User and service user attribution
  - Parent/child session relationships
- **Sessions Insights** — Sessions augmented with aggregate insights
  - All fields from the Sessions stream
  - Per-session message counts (`num_user_messages`, `num_devin_messages`)
  - Session size classification (`session_size`)
  - AI-generated analysis: category, programming languages, tools and frameworks, issues, note usage, suggested prompts, timeline
  - Analysis fields may be null for sessions where insights have not been generated
- **Session Messages** — Full conversation history for each session
  - Every message exchanged between users and Devin
  - Message source attribution (user vs. devin)
  - Chronological ordering via timestamps
- **Playbooks** — Reusable playbook definitions
  - Playbook title, body content, and macro triggers
  - Access controls (team vs. personal)
  - Authorship and modification tracking
- **Secrets** — Secret metadata (values are never exposed)
  - Secret keys, types, and sensitivity flags
  - Access type and organizational scope
  - Creation and update audit trail
- **Knowledge Notes** — Organization knowledge base entries
  - Note content, folder organization, and trigger rules
  - Enabled/disabled state for automated knowledge injection
  - Pinned repo associations and macro triggers

## Prerequisites

- A Devin account with access to an organization.
- A Devin API key. All Devin API credentials use the `cog_` prefix. A [service user API key](https://docs.devin.ai/api-reference/authentication) is recommended for automation; a personal access token also works if your account has the closed beta enabled.
- Your Devin organization ID (uses the `org_` prefix).
- The principal behind your API key must have the Devin permissions required to read the streams you want to sync. Grant these permissions to the service user's role in **Enterprise settings → Roles**:
  - `ViewOrgSessions` — required for `sessions`, `sessions_insights`, and `session_messages`.
  - `ManageOrgPlaybooks` — required for `playbooks`.
  - `ManageOrgSecrets` — required for `secrets` (only metadata is returned; secret values are never exposed).
  - `ManageOrgKnowledge` — required for `knowledge_notes`.

For a full permission reference, see the [Devin Permissions & RBAC documentation](https://docs.devin.ai/api-reference/v3/overview).

## Setup guide

### Step 1: Create a service user and API key

1. Sign in to [app.devin.ai](https://app.devin.ai/) as an organization admin.
2. Open **Settings → Service users** (organization) or **Enterprise settings → Service users** (enterprise).
3. Create a service user and assign a role that grants the permissions listed under [Prerequisites](#prerequisites).
4. Generate an API key for the service user. The key is shown only once at creation — copy and store it securely. All keys start with `cog_`.

### Step 2: Find your organization ID

Your organization ID is shown on the **Settings → Service users** page in [app.devin.ai](https://app.devin.ai/). It starts with `org_`.

### Step 3: Configure the connector in Airbyte

1. In Airbyte, create a new Devin AI source.
2. Enter your **API Token** (the `cog_...` key from Step 1).
3. Enter your **Organization ID** (the `org_...` value from Step 2).
4. Optionally, set a **Start Date** (UTC, ISO 8601 format, for example `2026-01-01T00:00:00Z`) to limit the `sessions`, `sessions_insights`, and `session_messages` streams to sessions created on or after that instant. Leave empty to sync full history.
5. Click **Test Connection** to verify your credentials.

## Supported streams

| Stream | Sync Mode | Description |
|--------|-----------|-------------|
| [Sessions](https://docs.devin.ai/api-reference/v3/sessions/organizations-sessions) | Full Refresh | All Devin sessions in your organization |
| [Sessions Insights](https://docs.devin.ai/api-reference/v3/sessions/organizations-sessions-insights) | Full Refresh | Sessions enriched with message counts, size classification, and AI-generated analysis |
| [Session Messages](https://docs.devin.ai/api-reference/v3/sessions/get-session-messages) | Full Refresh | Conversation messages for each session |
| [Playbooks](https://docs.devin.ai/api-reference/v3/playbooks/list-playbooks) | Full Refresh | Team playbooks for the organization |
| [Secrets](https://docs.devin.ai/api-reference/v3/secrets/list-secrets) | Full Refresh | Secret metadata (no secret values are synced) |
| [Knowledge Notes](https://docs.devin.ai/api-reference/v3/notes/enterprise-knowledge-notes) | Full Refresh | Knowledge notes for the organization |

The `session_messages` stream is a substream of `sessions`: for each session returned by `sessions`, Airbyte issues one additional request to fetch that session's messages. Conversation history may contain PII, so only enable this stream when you need message-level data. For aggregate message counts and Devin-generated classification without raw message bodies, use `sessions_insights` instead.

## Configuration reference

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_token` | string | Yes | | Devin API key for authentication. All Devin API credentials use the `cog_` prefix. |
| `org_id` | string | Yes | | Your Devin organization ID. Uses the `org_` prefix. |
| `start_date` | string (ISO 8601, UTC) | No | (no filter) | Optional lower bound on `created_at` for the `sessions`, `sessions_insights`, and `session_messages` streams. Sessions created before this instant are excluded. Format: `YYYY-MM-DDTHH:MM:SSZ`. Example: `2026-01-01T00:00:00Z`. |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.2.1 | 2026-04-28 | [77201](https://github.com/airbytehq/airbyte/pull/77201) | Update dependencies |
| 0.2.0 | 2026-04-22 | [76475](https://github.com/airbytehq/airbyte/pull/76475) | Add `sessions_insights` stream for analytics (message counts, session size, AI-generated classification); add optional `start_date` config to filter `sessions`, `sessions_insights`, and `session_messages` by creation time |
| 0.1.1 | 2026-04-21 | [76504](https://github.com/airbytehq/airbyte/pull/76504) | Update dependencies |
| 0.1.0 | 2026-04-15 | [74417](https://github.com/airbytehq/airbyte/pull/74417) | Initial release with sessions, session messages, playbooks, secrets, and knowledge notes streams |

</details>
