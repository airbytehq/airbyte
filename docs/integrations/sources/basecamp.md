# Basecamp

<HideInUI>

This page contains the setup guide and reference information for the [Basecamp](https://basecamp.com/) source connector.

</HideInUI>

## Prerequisites

- A Basecamp account with access to at least one project
- A registered OAuth application on the [37signals Launchpad](https://launchpad.37signals.com/integrations)
- Your Basecamp Account ID

## Setup guide

### Step 1: Register an OAuth application

1. Go to [37signals Launchpad](https://launchpad.37signals.com/integrations) and sign in with your Basecamp credentials.
2. Register a new application. You will receive a **Client ID** and **Client Secret**.
3. Provide a **Redirect URI** during registration. If you don't have one ready, you can use a placeholder like `http://localhost`.

### Step 2: Obtain a refresh token

This connector authenticates using OAuth 2.0 with a refresh token. To obtain one, you must complete the OAuth authorization flow:

1. Direct a browser to the following URL, replacing the placeholders with your Client ID and Redirect URI:

   ```text
   https://launchpad.37signals.com/authorization/new?type=web_server&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI
   ```

2. Authorize the application when prompted. Basecamp redirects you to your Redirect URI with a `code` parameter.
3. Exchange the authorization code for tokens by making a POST request:

   ```text
   POST https://launchpad.37signals.com/authorization/token
   ```

   Include `type=web_server`, your `client_id`, `redirect_uri`, `client_secret`, and the `code` from the previous step.

4. The response contains an `access_token` and a `refresh_token`. Copy the **refresh_token** for use in the connector configuration.

Alternatively, the [`basecampy3`](https://github.com/phistrom/basecampy3) Python library provides a CLI tool that automates this flow.

### Step 3: Find your Account ID

1. After obtaining your access token, make a GET request to `https://launchpad.37signals.com/authorization.json` with the `Authorization: Bearer YOUR_ACCESS_TOKEN` header.
2. In the response, find the account with `"product": "bc3"`. The `id` field is your **Account ID**.

Alternatively, your Account ID is the number in your Basecamp URL: `https://3.basecamp.com/YOUR_ACCOUNT_ID/...`.

### Step 4: Configure the connector in Airbyte

1. Enter your **Account ID**.
2. Set a **Start date** for incremental streams. Records updated before this date are not synced.
3. Enter the **Client ID** and **Client Secret** from your OAuth application.
4. Enter the **Refresh token** obtained in Step 2.

## Supported sync modes

The Basecamp source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- Full Refresh
- Incremental

## Supported streams

| Stream | Primary Key | Sync Modes | Description |
|---|---|---|---|
| [projects](https://github.com/basecamp/bc3-api/blob/master/sections/projects.md) | `id` | Full Refresh | Lists all active projects in the account. |
| [schedules](https://github.com/basecamp/bc3-api/blob/master/sections/schedules.md) | `id` | Full Refresh | Schedule tools attached to each project. Child of `projects`. |
| [schedule_entries](https://github.com/basecamp/bc3-api/blob/master/sections/schedule_entries.md) | `id` | Full Refresh | Individual entries within each schedule. Child of `schedules`. |
| [todos](https://github.com/basecamp/bc3-api/blob/master/sections/todos.md) | `id` | Full Refresh, Incremental | To-do items across all projects. Uses `updated_at` as the cursor field. |
| [messages](https://github.com/basecamp/bc3-api/blob/master/sections/messages.md) | `id` | Full Refresh, Incremental | Message board posts across all projects. Uses `updated_at` as the cursor field. |

### Stream relationships

The `schedules` stream is a child of `projects`, and `schedule_entries` is a child of `schedules`. During a sync, the connector first fetches all projects, then retrieves schedules for each project, and finally fetches entries for each schedule.

## Limitations and troubleshooting

### Rate limiting

The Basecamp API enforces a rate limit of 50 requests per 10-second window per IP address. The API returns a `429 Too Many Requests` response with a `Retry-After` header when this limit is exceeded.

### Token expiration

Basecamp access tokens expire after two weeks. The connector uses the refresh token to obtain new access tokens automatically. If the refresh token itself becomes invalid, you need to re-authorize the application by repeating the OAuth flow.

### Connector maturity

This connector is in **Alpha** status and has **Community** support. It is a manifest-only (low-code) connector built with the Connector Builder.

<HideInUI>

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `account_id` | `number` | Your Basecamp Account ID. Find it in your Basecamp URL or via the authorization endpoint. | |
| `start_date` | `string` | Start date for incremental syncs in `YYYY-MM-DDTHH:MM:SSZ` format. Records updated before this date are not synced. | |
| `client_id` | `string` | OAuth Client ID from your [37signals Launchpad](https://launchpad.37signals.com/integrations) application. | |
| `client_secret` | `string` | OAuth Client Secret from your 37signals Launchpad application. | |
| `client_refresh_token_2` | `string` | OAuth refresh token obtained through the authorization flow. | |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.35 | 2026-04-01 | [75947](https://github.com/airbytehq/airbyte/pull/75947) | Bump SDM base image for memory monitor (CDK PR #962) |
| 0.0.34 | 2026-03-31 | [75892](https://github.com/airbytehq/airbyte/pull/75892) | Update dependencies |
| 0.0.33 | 2026-03-17 | [75000](https://github.com/airbytehq/airbyte/pull/75000) | Update dependencies |
| 0.0.32 | 2026-02-24 | [73800](https://github.com/airbytehq/airbyte/pull/73800) | Update dependencies |
| 0.0.31 | 2026-02-03 | [72685](https://github.com/airbytehq/airbyte/pull/72685) | Update dependencies |
| 0.0.30 | 2026-01-20 | [71898](https://github.com/airbytehq/airbyte/pull/71898) | Update dependencies |
| 0.0.29 | 2026-01-14 | [71405](https://github.com/airbytehq/airbyte/pull/71405) | Update dependencies |
| 0.0.28 | 2025-12-18 | [70811](https://github.com/airbytehq/airbyte/pull/70811) | Update dependencies |
| 0.0.27 | 2025-11-25 | [69901](https://github.com/airbytehq/airbyte/pull/69901) | Update dependencies |
| 0.0.26 | 2025-11-18 | [69521](https://github.com/airbytehq/airbyte/pull/69521) | Update dependencies |
| 0.0.25 | 2025-10-29 | [68904](https://github.com/airbytehq/airbyte/pull/68904) | Update dependencies |
| 0.0.24 | 2025-10-21 | [68382](https://github.com/airbytehq/airbyte/pull/68382) | Update dependencies |
| 0.0.23 | 2025-10-14 | [67965](https://github.com/airbytehq/airbyte/pull/67965) | Update dependencies |
| 0.0.22 | 2025-10-07 | [67162](https://github.com/airbytehq/airbyte/pull/67162) | Update dependencies |
| 0.0.21 | 2025-09-30 | [66275](https://github.com/airbytehq/airbyte/pull/66275) | Update dependencies |
| 0.0.20 | 2025-09-09 | [65643](https://github.com/airbytehq/airbyte/pull/65643) | Update dependencies |
| 0.0.19 | 2025-08-02 | [64408](https://github.com/airbytehq/airbyte/pull/64408) | Update dependencies |
| 0.0.18 | 2025-07-26 | [63806](https://github.com/airbytehq/airbyte/pull/63806) | Update dependencies |
| 0.0.17 | 2025-07-12 | [63042](https://github.com/airbytehq/airbyte/pull/63042) | Update dependencies |
| 0.0.16 | 2025-06-28 | [62136](https://github.com/airbytehq/airbyte/pull/62136) | Update dependencies |
| 0.0.15 | 2025-06-15 | [61088](https://github.com/airbytehq/airbyte/pull/61088) | Update dependencies |
| 0.0.14 | 2025-05-24 | [60678](https://github.com/airbytehq/airbyte/pull/60678) | Update dependencies |
| 0.0.13 | 2025-05-10 | [59871](https://github.com/airbytehq/airbyte/pull/59871) | Update dependencies |
| 0.0.12 | 2025-05-03 | [59362](https://github.com/airbytehq/airbyte/pull/59362) | Update dependencies |
| 0.0.11 | 2025-04-26 | [58726](https://github.com/airbytehq/airbyte/pull/58726) | Update dependencies |
| 0.0.10 | 2025-04-19 | [58254](https://github.com/airbytehq/airbyte/pull/58254) | Update dependencies |
| 0.0.9 | 2025-04-12 | [57606](https://github.com/airbytehq/airbyte/pull/57606) | Update dependencies |
| 0.0.8 | 2025-04-05 | [57157](https://github.com/airbytehq/airbyte/pull/57157) | Update dependencies |
| 0.0.7 | 2025-03-29 | [56608](https://github.com/airbytehq/airbyte/pull/56608) | Update dependencies |
| 0.0.6 | 2025-03-22 | [56114](https://github.com/airbytehq/airbyte/pull/56114) | Update dependencies |
| 0.0.5 | 2025-03-08 | [54863](https://github.com/airbytehq/airbyte/pull/54863) | Update dependencies |
| 0.0.4 | 2025-02-22 | [54222](https://github.com/airbytehq/airbyte/pull/54222) | Update dependencies |
| 0.0.3 | 2025-02-15 | [47905](https://github.com/airbytehq/airbyte/pull/47905) | Update dependencies |
| 0.0.2 | 2024-10-09 | [46660](https://github.com/airbytehq/airbyte/pull/46660) | Update dependencies |
| 0.0.1 | 2024-08-12 | | Initial release by natikgadzhi via Connector Builder |

</details>

</HideInUI>
