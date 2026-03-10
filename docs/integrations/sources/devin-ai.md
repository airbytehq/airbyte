# Devin AI

This page contains the setup guide and reference information for the [Devin AI](https://devin.ai/) source connector.

## Overview

The Devin AI source connector syncs data from the Devin AI v3 API into Airbyte. Devin AI is an autonomous AI software engineer that can plan, code, test, and deploy software. This connector allows you to extract session data, conversation history, playbooks, secrets metadata, and knowledge notes from your Devin AI organization.

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
| [Session Messages](https://docs.devin.ai/api-reference/v3/sessions/get-session-messages) | Full Refresh | Conversation messages for each session |
| [Playbooks](https://docs.devin.ai/api-reference/v3/playbooks/list-playbooks) | Full Refresh | Team playbooks for the organization |
| [Secrets](https://docs.devin.ai/api-reference/v3/secrets/list-secrets) | Full Refresh | Secret metadata (no secret values are synced) |
| [Knowledge Notes](https://docs.devin.ai/api-reference/v3/notes/enterprise-knowledge-notes) | Full Refresh | Knowledge notes for the organization |

## Configuration reference

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_token` | string | Yes | | Devin API key for authentication. Service user tokens use the `cog_*` prefix. |
| `org_id` | string | Yes | | Your Devin organization ID. Uses the `org_*` prefix. |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.1.0 | 2026-03-10 | | Initial release with sessions, session messages, playbooks, secrets, and knowledge notes streams |

</details>
