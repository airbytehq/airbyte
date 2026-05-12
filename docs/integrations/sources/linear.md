# Linear

<HideInUI>

This page contains the setup guide and reference information for the [Linear](https://linear.app/) source connector.

</HideInUI>

[Linear](https://linear.app/) is a project management and issue tracking tool designed for software teams. It provides a streamlined interface for managing issues, sprints, and product roadmaps with a focus on speed and simplicity.

## Prerequisites

- A Linear account
- One of the following authentication methods:
  - **API Key**: A Linear personal API key.
  - **OAuth 2.0**: A Linear OAuth app with a client ID, client secret, and refresh token.

## Setup guide

### Step 1: Choose an authentication method

The Linear source connector supports API key and OAuth 2.0 authentication.

#### API key

1. Log in to your [Linear](https://linear.app/) account.
2. Navigate to **Settings** by clicking your workspace name in the sidebar.
3. Select **Security & access** from the settings menu.
4. Scroll to the **Personal API keys** section.
5. Click **Create key**, give the key a descriptive label (for example, `airbyte`), and click **Create**.
6. Copy the API key and store it securely. Linear only displays the key once.

The API key inherits your user's permissions in the workspace. The connector can only sync data you can see in Linear.

For more information, see the [Linear GraphQL API documentation](https://linear.app/developers/graphql).

#### OAuth 2.0

Create a Linear OAuth app and configure the redirect callback URL for your Airbyte deployment. The connector requests the `read` and `customer:read` scopes. Linear returns an access token and refresh token after the OAuth flow, and the connector uses the refresh token to refresh access tokens when they expire.

For more information, see the [Linear OAuth 2.0 authentication documentation](https://linear.app/developers/oauth-2-0-authentication).

### Step 2: Configure the Linear connector in Airbyte

1. In the Airbyte UI, navigate to **Sources** and click **+ New source**.
2. Select **Linear** from the list of available sources.
3. Enter a **Source name** of your choosing.
4. For **Authentication**, choose **API Key** or **OAuth 2.0**.
5. Enter the required credentials for your authentication method.
6. Optionally, enter a **Start Date** in ISO 8601 format (for example, `2024-01-01T00:00:00.000Z`). Only records updated on or after this date are replicated for streams that support incremental sync. If you leave this field empty, the connector defaults to two years before the time of the first sync.
7. Click **Set up source** and wait for the connection test to complete.

Existing connections that authenticated with a Linear API key continue to use API key authentication after upgrading to connector version `0.2.1` or later. If you upgraded an API key connection to `0.2.0` and it no longer passes connection checks, upgrade to `0.2.1` or later.

## Supported sync modes

The Linear source connector supports the following sync modes:

- [Full Refresh - Overwrite](https://docs.airbyte.com/cloud/core-concepts/#full-refresh---overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/cloud/core-concepts/#full-refresh---append)
- [Incremental - Append](https://docs.airbyte.com/cloud/core-concepts/#incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/cloud/core-concepts/#incremental-append--deduped)

Streams that support incremental sync use the `updatedAt` field as the cursor. The Start Date you set when configuring the connector is the lower bound for the first incremental sync. Subsequent syncs use the most recent `updatedAt` value from the previous sync as the new lower bound.

The following streams are full-refresh only because the Linear GraphQL API doesn't expose a filter argument that the connector can use to request only updated records: `project_statuses`, `issue_relations`, `customer_statuses`, and `customer_tiers`.

## Supported streams

The Linear source connector supports the following streams. Streams marked as incremental use `updatedAt` as the cursor field.

| Stream | Incremental | Description |
| ------ | :---------: | ----------- |
| `attachments` | Yes | File and link attachments on issues. |
| `comments` | Yes | Comments posted on issues. |
| `customer_needs` | Yes | Customer needs associated with issues. |
| `customers` | Yes | Customer records tracked in Linear's customer requests feature. |
| `customer_statuses` | No | Status definitions for customer records. |
| `customer_tiers` | No | Tier definitions for customer records. |
| `cycles` | Yes | Cycles (sprints) for each team. |
| `issue_labels` | Yes | Labels that can be applied to issues. |
| `issue_relations` | No | Relationships between issues (for example, blocks and duplicates). |
| `issues` | Yes | Issues in every team, including archived issues. |
| `project_milestones` | Yes | Milestones defined inside projects. |
| `project_statuses` | No | Status definitions for projects. |
| `projects` | Yes | Projects across all teams. |
| `teams` | Yes | Teams in your Linear workspace. |
| `users` | Yes | Users in your Linear workspace. |
| `workflow_states` | Yes | Workflow states (for example, Todo, In Progress, Done) defined by each team. |

## Limitations and troubleshooting

### Rate limiting

The Linear API uses a leaky bucket algorithm for rate limiting. The connector handles rate limiting automatically, but syncs may slow down if you are making many concurrent requests to the Linear API.

Linear currently allows up to 2,500 API key requests per user per hour and 5,000 OAuth app requests per user or app user per hour. Linear also applies query complexity limits, including a maximum complexity of 10,000 points for a single query. For more information, see the [Linear rate limiting documentation](https://linear.app/developers/rate-limiting).

### Data availability

The connector retrieves data that the authenticated user has access to. If you cannot see certain teams, projects, or issues in your synced data, verify that your Linear account has the appropriate permissions.

## Reference

This connector uses the [Linear GraphQL API](https://linear.app/developers/graphql). All API requests use the `https://api.linear.app/graphql` endpoint.

For programmatic configuration, use these parameter names:

| Field | Required | Description |
| ----- | :------: | ----------- |
| `credentials.auth_type` | Yes | Authentication method. Valid values are `API Key` and `OAuth2.0`. |
| `credentials.api_key` | Required for API key authentication | Linear personal API key. |
| `credentials.client_id` | Required for OAuth 2.0 authentication | Client ID of your Linear OAuth app. |
| `credentials.client_secret` | Required for OAuth 2.0 authentication | Client secret of your Linear OAuth app. |
| `credentials.refresh_token` | Required for OAuth 2.0 authentication | Refresh token returned by the Linear OAuth flow. |
| `start_date` | No | UTC date and time in ISO 8601 format. Records updated before this date aren't replicated for streams that support incremental sync. If unset, defaults to two years before the first sync. |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------- | ---- | ------------ | ------- |
| 0.2.1 | 2026-05-12 | [78013](https://github.com/airbytehq/airbyte/pull/78013) | Fix API key config migration for existing connections |
| 0.2.0 | 2026-05-11 | [77578](https://github.com/airbytehq/airbyte/pull/77578) | Add OAuth 2.0 authentication support and migrate existing API key configurations to nested credentials |
| 0.1.2 | 2026-04-28 | [77318](https://github.com/airbytehq/airbyte/pull/77318) | Update dependencies |
| 0.1.1 | 2026-04-21 | [76654](https://github.com/airbytehq/airbyte/pull/76654) | Update dependencies |
| 0.1.0 | 2026-04-17 | [76429](https://github.com/airbytehq/airbyte/pull/76429) | Add incremental sync support for 12 streams using the `updatedAt` cursor field |
| 0.0.36 | 2026-03-31 | [75720](https://github.com/airbytehq/airbyte/pull/75720) | Update dependencies |
| 0.0.35 | 2026-03-17 | [75023](https://github.com/airbytehq/airbyte/pull/75023) | Update dependencies |
| 0.0.34 | 2026-03-03 | [74239](https://github.com/airbytehq/airbyte/pull/74239) | Update dependencies |
| 0.0.33 | 2026-02-10 | [73035](https://github.com/airbytehq/airbyte/pull/73035) | Update dependencies |
| 0.0.32 | 2026-02-03 | [72748](https://github.com/airbytehq/airbyte/pull/72748) | Update dependencies |
| 0.0.31 | 2026-01-21 | [72240](https://github.com/airbytehq/airbyte/pull/72240) | fix(linear): icon |
| 0.0.30 | 2026-01-20 | [72027](https://github.com/airbytehq/airbyte/pull/72027) | Update dependencies |
| 0.0.29 | 2026-01-14 | [71489](https://github.com/airbytehq/airbyte/pull/71489) | Update dependencies |
| 0.0.28 | 2025-12-18 | [70775](https://github.com/airbytehq/airbyte/pull/70775) | Update dependencies |
| 0.0.27 | 2025-11-25 | [70007](https://github.com/airbytehq/airbyte/pull/70007) | Update dependencies |
| 0.0.26 | 2025-11-18 | [69442](https://github.com/airbytehq/airbyte/pull/69442) | Update dependencies |
| 0.0.25 | 2025-10-29 | [68966](https://github.com/airbytehq/airbyte/pull/68966) | Update dependencies |
| 0.0.24 | 2025-10-21 | [68296](https://github.com/airbytehq/airbyte/pull/68296) | Update dependencies |
| 0.0.23 | 2025-10-14 | [68027](https://github.com/airbytehq/airbyte/pull/68027) | Update dependencies |
| 0.0.22 | 2025-10-07 | [67519](https://github.com/airbytehq/airbyte/pull/67519) | Update dependencies |
| 0.0.21 | 2025-09-30 | [66807](https://github.com/airbytehq/airbyte/pull/66807) | Update dependencies |
| 0.0.20 | 2025-09-24 | [66655](https://github.com/airbytehq/airbyte/pull/66655) | Update dependencies |
| 0.0.19 | 2025-09-09 | [65897](https://github.com/airbytehq/airbyte/pull/65897) | Update dependencies |
| 0.0.18 | 2025-08-23 | [65391](https://github.com/airbytehq/airbyte/pull/65391) | Update dependencies |
| 0.0.17 | 2025-08-09 | [64629](https://github.com/airbytehq/airbyte/pull/64629) | Update dependencies |
| 0.0.16 | 2025-08-02 | [64275](https://github.com/airbytehq/airbyte/pull/64275) | Update dependencies |
| 0.0.15 | 2025-07-26 | [63892](https://github.com/airbytehq/airbyte/pull/63892) | Update dependencies |
| 0.0.14 | 2025-07-19 | [63518](https://github.com/airbytehq/airbyte/pull/63518) | Update dependencies |
| 0.0.13 | 2025-07-12 | [63095](https://github.com/airbytehq/airbyte/pull/63095) | Update dependencies |
| 0.0.12 | 2025-07-05 | [62601](https://github.com/airbytehq/airbyte/pull/62601) | Update dependencies |
| 0.0.11 | 2025-06-28 | [62178](https://github.com/airbytehq/airbyte/pull/62178) | Update dependencies |
| 0.0.10 | 2025-06-26 | [61417](https://github.com/airbytehq/airbyte/pull/61417) | source-linear contribution from zckymc |
| 0.0.9 | 2025-06-21 | [61843](https://github.com/airbytehq/airbyte/pull/61843) | Update dependencies |
| 0.0.8 | 2025-06-14 | [61117](https://github.com/airbytehq/airbyte/pull/61117) | Update dependencies |
| 0.0.7 | 2025-05-24 | [60728](https://github.com/airbytehq/airbyte/pull/60728) | Update dependencies |
| 0.0.6 | 2025-05-10 | [59893](https://github.com/airbytehq/airbyte/pull/59893) | Update dependencies |
| 0.0.5 | 2025-05-03 | [59299](https://github.com/airbytehq/airbyte/pull/59299) | Update dependencies |
| 0.0.4 | 2025-04-26 | [58781](https://github.com/airbytehq/airbyte/pull/58781) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58215](https://github.com/airbytehq/airbyte/pull/58215) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57669](https://github.com/airbytehq/airbyte/pull/57669) | Update dependencies |
| 0.0.1 | 2025-04-11 | [#57586](https://github.com/airbytehq/airbyte/pull/57586) | Initial release by [@natikgadzhi](https://github.com/natikgadzhi) |

</details>
