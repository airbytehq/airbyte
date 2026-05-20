# Basecamp

This page guides you through configuring the Basecamp source connector to sync project, schedule, to-do, and message data from [Basecamp 3](https://basecamp.com/) into your destination. The connector uses the [Basecamp 3 REST API](https://github.com/basecamp/bc3-api) and authenticates with OAuth 2.0 through [37signals Launchpad](https://launchpad.37signals.com/).

## Prerequisites

- A Basecamp account on Basecamp 3 (accounts on Basecamp 2 and Basecamp Classic use a different API and aren't supported).
- Your Basecamp **Account ID**.
- A registered OAuth integration on 37signals Launchpad, which provides a **Client ID** and **Client secret**.
- A long-lived OAuth 2.0 **Refresh token** issued for that integration.

### Find your Account ID

Sign in to Basecamp and open any page in your account. The numeric segment immediately after the host in the URL is your account ID. For example, if the URL is `https://3.basecamp.com/1234567/projects`, your account ID is `1234567`. All API requests to Basecamp are scoped to this ID.

### Register an OAuth integration

1. Go to [37signals Launchpad integrations](https://launchpad.37signals.com/integrations) and click **New integration**.
2. Enter a name, your company, and a website or contact address. 37signals uses this information to contact integration owners, so provide values you can receive mail at.
3. For **Redirect URI**, enter any URL you control. The connector doesn't use this URL, but 37signals requires one. If you don't have one handy, use a placeholder like `https://example.com/oauth`.
4. Save the integration. Launchpad displays a **Client ID** and **Client secret**. Keep both values safe; you need them for the connector and to complete the OAuth flow.

### Obtain a refresh token

The connector refreshes its own access tokens at runtime, but you must supply a refresh token the first time you set up the source. To get one, complete a full OAuth 2.0 authorization code flow against 37signals Launchpad once, using the client ID and secret you just created.

Follow the steps in the [Basecamp authentication guide](https://github.com/basecamp/api/blob/master/sections/authentication.md) to exchange an authorization code for an access token and refresh token. The relevant endpoints are:

- Authorization: `https://launchpad.37signals.com/authorization/new`
- Token exchange: `https://launchpad.37signals.com/authorization/token`

Any OAuth 2.0 client library can perform this flow. If you'd prefer a ready-made tool, the community-maintained [basecampy3](https://github.com/phistrom/basecampy3) CLI walks you through the flow and prints the resulting tokens. Record the `refresh_token` value; that's what Airbyte needs.

Refresh tokens issued by 37signals do not expire unless you revoke the integration, so you can reuse the same value across syncs.

## Setup guide

1. In the Airbyte UI, create a new **Basecamp** source.
2. Enter your **Account ID**.
3. Enter a **Start date** in `YYYY-MM-DDTHH:MM:SSZ` format. Incremental streams only emit records updated on or after this date.
4. Paste the **Client ID**, **Client secret**, and **Refresh token** you obtained above into the matching fields.
5. Click **Set up source**. Airbyte runs a connection check against the `projects` endpoint to validate your credentials.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `account_id` | `number` | Your Basecamp Account ID. |  |
| `start_date` | `string` | Start date used for incremental streams. Records updated before this date aren't synced. |  |
| `client_id` | `string` | OAuth application Client ID from [37signals Launchpad](https://launchpad.37signals.com/integrations). |  |
| `client_secret` | `string` | OAuth application Client secret. |  |
| `client_refresh_token_2` | `string` | OAuth 2.0 refresh token obtained by completing the Launchpad authorization flow once. |  |

## Supported sync modes

The Basecamp source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes):

- Full Refresh | Overwrite
- Full Refresh | Append
- Incremental | Append (for streams that expose an `updated_at` cursor)
- Incremental | Append + Deduped (for streams that expose an `updated_at` cursor)

## Supported streams

| Stream | Primary key | Incremental | Notes |
|--------|-------------|-------------|-------|
| [`projects`](https://github.com/basecamp/bc3-api/blob/master/sections/projects.md) | `id` | ❌ | Active projects (buckets) in the account. Used as the parent stream for schedules. |
| [`schedules`](https://github.com/basecamp/bc3-api/blob/master/sections/schedules.md) | `id` | ❌ | Schedule tools attached to each project. |
| [`schedule_entries`](https://github.com/basecamp/bc3-api/blob/master/sections/schedule_entries.md) | `id` | ❌ | Events listed in each project's schedule. |
| [`todos`](https://github.com/basecamp/bc3-api/blob/master/sections/todos.md) | `id` | ✅ (cursor: `updated_at`) | To-do recordings across all projects. |
| [`messages`](https://github.com/basecamp/bc3-api/blob/master/sections/messages.md) | `id` | ✅ (cursor: `updated_at`) | Message board posts across all projects. |

The `todos` and `messages` streams use Basecamp's `projects/recordings.json` endpoint, which returns records sorted by `updated_at` in descending order. The connector walks the result set until it reaches the configured start date, then stops — Basecamp doesn't offer a server-side `updated_since` filter for this endpoint.

## Performance considerations

- Basecamp applies dynamic, multi-dimensional rate limits. The first limit you typically encounter is around **50 requests per 10-second window per IP**. The connector retries `429 Too Many Requests` responses using the `Retry-After` header.
- All requests are scoped to a single account (the connector's `url_base` is `https://3.basecampapi.com/{account_id}/`).
- To sync multiple Basecamp accounts, create one Airbyte source per account.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.37 | 2026-04-28 | [77177](https://github.com/airbytehq/airbyte/pull/77177) | Update dependencies |
| 0.0.36 | 2026-04-21 | [76843](https://github.com/airbytehq/airbyte/pull/76843) | Bump SDM base image to stable 7.17.2 |
| 0.0.35 | 2026-03-31 | [75947](https://github.com/airbytehq/airbyte/pull/75947) | Bump SDM base image for memory monitor (CDK PR #962) |
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
