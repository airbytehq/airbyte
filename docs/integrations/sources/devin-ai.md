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

- A Devin AI account with API access
- A Devin AI API token (service user tokens use the `cog_*` prefix)
- Your Devin AI Organization ID (uses the `org_*` prefix)

## Setup guide

### Step 1: Obtain your API token

1. Log in to your Devin AI dashboard.
2. Navigate to the API settings or service user management section.
3. Create or retrieve your API token.

### Step 2: Find your Organization ID

1. Your Organization ID is available in your Devin AI dashboard settings.
2. It uses the `org_*` prefix format.

### Step 3: Configure the connector in Airbyte

1. Enter your **API Token**.
2. Enter your **Organization ID**.
3. Click **Test Connection** to verify your credentials.

## Supported streams

| Stream | Sync Mode | Description |
|--------|-----------|-------------|
| [Sessions](https://docs.devin.ai/api-reference/v3/sessions/list-sessions) | Full Refresh | All Devin sessions in your organization |
| [Sessions Insights](https://docs.devin.ai/api-reference/v3/sessions/organizations-sessions-insights) | Full Refresh | Sessions enriched with message counts, size classification, and AI-generated analysis |
| [Session Messages](https://docs.devin.ai/api-reference/v3/sessions/get-session-messages) | Full Refresh | Conversation messages for each session |
| [Playbooks](https://docs.devin.ai/api-reference/v3/playbooks/list-playbooks) | Full Refresh | Team playbooks for the organization |
| [Secrets](https://docs.devin.ai/api-reference/v3/secrets/list-secrets) | Full Refresh | Secret metadata (no secret values are synced) |
| [Knowledge Notes](https://docs.devin.ai/api-reference/v3/notes/enterprise-knowledge-notes) | Full Refresh | Knowledge notes for the organization |

## Configuration reference

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_token` | string | Yes | | Devin API key for authentication. Service user tokens use the `cog_*` prefix. |
| `org_id` | string | Yes | | Your Devin organization ID. Uses the `org_*` prefix. |
| `start_date` | string (ISO 8601, UTC) | No | (epoch 0, i.e. no filter) | Optional lower bound on `created_at` for the `sessions`, `sessions_insights`, and `session_messages` streams. Sessions created before this instant are excluded. Format: `YYYY-MM-DDTHH:MM:SSZ`. Example: `2026-01-01T00:00:00Z`. |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.2.0 | 2026-04-20 | [76475](https://github.com/airbytehq/airbyte/pull/76475) | Add `sessions_insights` stream for analytics (message counts, session size, AI-generated classification); add optional `start_date` config to filter `sessions`, `sessions_insights`, and `session_messages` by creation time |
| 0.1.1 | 2026-04-21 | [76504](https://github.com/airbytehq/airbyte/pull/76504) | Update dependencies |
| 0.1.0 | 2026-03-10 | | Initial release with sessions, session messages, playbooks, secrets, and knowledge notes streams |

</details>
