# Linear

<HideInUI>

This page contains the setup guide and reference information for the [Linear](https://linear.app/) source connector.

</HideInUI>

[Linear](https://linear.app/) is a project management and issue tracking tool designed for software teams. It provides a streamlined interface for managing issues, sprints, and product roadmaps with a focus on speed and simplicity.

## Prerequisites

- A Linear account
- One of the following authentication methods:
  - **API Key**: A Linear personal API key.
  - **OAuth 2.0**: A Linear OAuth app with a client ID, client secret, and refresh token. A Linear workspace admin has to authorize the app, because the connector installs it at the workspace level.

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

1. Create a [Linear OAuth application](https://linear.app/settings/api/applications/new).
2. Add the redirect callback URL for your Airbyte deployment to the app's redirect URLs. Linear rejects authorization requests whose `redirect_uri` isn't registered on the app.
3. Copy the app's client ID and client secret.

The connector requests the `read` and `customer:read` scopes and authorizes with Linear's [actor authorization](https://linear.app/developers/oauth-actor-authorization) (`actor=app`), so the authorization installs the app in the workspace instead of acting as the individual who approved it. Linear treats `customer:read` as an app-only scope and requires admin permissions to install an app, so a workspace admin has to complete the authorization.

If your Airbyte deployment doesn't provide a browser-based OAuth flow, complete Linear's [authorization code flow](https://linear.app/developers/oauth-2-0-authentication) yourself and use the resulting refresh token:

1. Open `https://linear.app/oauth/authorize?client_id=<CLIENT_ID>&redirect_uri=<REDIRECT_URI>&response_type=code&state=<STATE>&scope=read,customer:read&actor=app&prompt=consent` in a browser and approve the app. Generate a random `state` value and verify it on the callback to protect against CSRF. The `prompt=consent` parameter forces Linear to show the consent screen. Linear redirects to your redirect URI with a `code` parameter.
2. Exchange the code for tokens by sending a form-encoded `POST` request to `https://api.linear.app/oauth/token` with `code`, `redirect_uri`, `client_id`, `client_secret`, and `grant_type=authorization_code`.
3. Copy the `refresh_token` from the response. The connector uses it to mint access tokens, which Linear expires after 24 hours.

### Step 2: Configure the Linear connector in Airbyte

1. In the Airbyte UI, navigate to **Sources** and click **+ New source**.
2. Select **Linear** from the list of available sources.
3. Enter a **Source name** of your choosing.
4. For **Authentication**, choose **API Key** or **OAuth 2.0**.
5. Enter the required credentials for your authentication method.
6. Optionally, enter a **Start Date** in ISO 8601 format (for example, `2024-01-01T00:00:00.000Z`). Only records updated on or after this date are replicated for streams that support incremental sync. If you leave this field empty, the connector defaults to two years before the time of the first sync.
7. Optionally, adjust the **Number of concurrent workers** (default 4, range 1–10). Higher values speed up syncs but increase the risk of hitting Linear's rate limits. Users on API key authentication (2,500 requests/hour) should generally stay at or below the default. Users on OAuth authentication (5,000 requests/hour) may increase this value if they have observed headroom in their rate-limit usage.
8. Click **Set up source** and wait for the connection test to complete.

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
| `issues` | Yes | Issues in every team, including archived issues. Archived issues have a non-null `archivedAt` value. |
| `project_milestones` | Yes | Milestones defined inside projects. |
| `project_statuses` | No | Status definitions for projects. |
| `projects` | Yes | Projects across all teams. |
| `teams` | Yes | Teams in your Linear workspace. |
| `users` | Yes | Users in your Linear workspace. |
| `workflow_states` | Yes | Workflow states (for example, Todo, In Progress, Done) defined by each team. |

Starting with connector version `0.2.16`, new connections pre-select `issues`, `projects`, `teams`, `users`, `comments`, `cycles`, `issue_labels`, and `workflow_states`. Enable the other streams yourself if you need them. Existing connections keep the streams you already selected.

### Customer Requests streams

The `customers`, `customer_needs`, `customer_statuses`, and `customer_tiers` streams read Linear's Customer Requests data. An admin has to enable Customer Requests in [Workspace Settings > Customer requests](https://linear.app/settings/customers) before your workspace has any of this data to sync, so these streams return no records in workspaces where the feature is off. Customer tiers are also defined in those settings, so the `customer_tiers` stream stays empty until someone configures tiers. See Linear's [Customer Requests documentation](https://linear.app/docs/customer-requests) for details.

## Limitations and troubleshooting

### Rate limiting

The Linear API uses a leaky bucket algorithm for rate limiting. The connector detects rate-limit errors returned by the API and automatically backs off until the rate-limit window resets. Syncs may slow down during backoff periods but will resume without manual intervention.

Linear enforces three types of rate limits:

- **Request limits**: 2,500 requests per user per hour for API key authentication, 5,000 for OAuth app authentication. All requests by the same user share the same quota.
- **Endpoint-specific limits**: Certain queries have lower per-endpoint limits. The connector respects the `X-RateLimit-Endpoint-Requests-Reset` header when these are hit.
- **Complexity limits**: Each query's complexity is calculated based on the number of requested fields and pagination depth. The maximum single-query complexity is 10,000 points. The hourly complexity budget is 3,000,000 points for API key authentication and 2,000,000 for OAuth.

Workspace-level OAuth applications receive dynamically increased limits based on the number of paid seats. For more information, see the [Linear rate limiting documentation](https://linear.app/developers/rate-limiting).

### Data availability

The connector retrieves only the data its credentials can see. With API key authentication, that's everything the key's owner can see in Linear. With OAuth, it's what the installed app can see in the workspace. If teams, projects, or issues are missing from your synced data, check those permissions in Linear first.

### Archived and deleted records

Archived records are returned with a non-null `archivedAt` value, which the connector uses as the deletion signal. Linear also supports permanent hard deletion (for example, `issueDelete` with `permanently`), which leaves no signal; hard-deleted records cannot be detected. The first sync after upgrading to version 0.3.0 backfills previously invisible archived records and may transfer a large one-time volume.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

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
| `num_workers` | No | Number of worker threads used to read streams in parallel (default 4, range 1–10). Higher values speed up syncs but increase the risk of hitting rate limits. |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------- | ---- | ------------ | ------- |
| 0.3.0 | 2026-08-21 | [84950](https://github.com/airbytehq/airbyte/pull/84950) | Include archived records in all streams (`includeArchived: true`) and declare `archivedAt` (and `trashed` on issues/projects) in stream schemas; the first sync after upgrade backfills previously invisible archived records and may transfer a large one-time volume |
| 0.2.18 | 2026-08-21 | [84948](https://github.com/airbytehq/airbyte/pull/84948) | Clarify authentication field titles and descriptions in the connector setup form. |
| 0.2.17 | 2026-08-21 | [84951](https://github.com/airbytehq/airbyte/pull/84951) | Enable acceptance test suites with GSM test secrets for API key and OAuth |
| 0.2.16 | 2026-08-21 | [84944](https://github.com/airbytehq/airbyte/pull/84944) | Add suggested streams so new connections pre-select core streams and exclude Customer Requests streams |
| 0.2.15 | 2026-08-21 | [84946](https://github.com/airbytehq/airbyte/pull/84946) | Update base image and declare a heartbeat timeout |
| 0.2.14 | 2026-08-18 | [84676](https://github.com/airbytehq/airbyte/pull/84676) | Update dependencies |
| 0.2.13 | 2026-08-11 | [84025](https://github.com/airbytehq/airbyte/pull/84025) | Update dependencies |
| 0.2.12 | 2026-08-04 | [83528](https://github.com/airbytehq/airbyte/pull/83528) | Update dependencies |
| 0.2.11 | 2026-07-28 | [82981](https://github.com/airbytehq/airbyte/pull/82981) | Update dependencies |
| 0.2.10 | 2026-07-21 | [82509](https://github.com/airbytehq/airbyte/pull/82509) | Update dependencies |
| 0.2.9 | 2026-07-14 | [81930](https://github.com/airbytehq/airbyte/pull/81930) | Update dependencies |
| 0.2.8 | 2026-06-30 | [81147](https://github.com/airbytehq/airbyte/pull/81147) | Update dependencies |
| 0.2.7 | 2026-06-23 | [80554](https://github.com/airbytehq/airbyte/pull/80554) | Update dependencies |
| 0.2.6 | 2026-06-16 | [79947](https://github.com/airbytehq/airbyte/pull/79947) | Update dependencies |
| 0.2.5 | 2026-06-10 | [78237](https://github.com/airbytehq/airbyte/pull/78237) | fix(source-linear): Handle GraphQL rate-limit errors |
| 0.2.4 | 2026-06-09 | [79388](https://github.com/airbytehq/airbyte/pull/79388) | Update dependencies |
| 0.2.3 | 2026-06-02 | [78816](https://github.com/airbytehq/airbyte/pull/78816) | Update dependencies |
| 0.2.2 | 2026-05-18 | [78160](https://github.com/airbytehq/airbyte/pull/78160) | Promote release candidate to GA |
| 0.2.1 | 2026-05-12 | [78013](https://github.com/airbytehq/airbyte/pull/78013) | Fix API key config migration for existing connections |
| 0.2.0 | 2026-05-11 | [77578](https://github.com/airbytehq/airbyte/pull/77578) | Add OAuth 2.0 authentication |
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
| 0.0.10 | 2025-06-26 | [61417](https://github.com/airbytehq/airbyte/pull/61417) | Update connector configuration |
| 0.0.9 | 2025-06-21 | [61843](https://github.com/airbytehq/airbyte/pull/61843) | Update dependencies |
| 0.0.8 | 2025-06-14 | [61117](https://github.com/airbytehq/airbyte/pull/61117) | Update dependencies |
| 0.0.7 | 2025-05-24 | [60728](https://github.com/airbytehq/airbyte/pull/60728) | Update dependencies |
| 0.0.6 | 2025-05-10 | [59893](https://github.com/airbytehq/airbyte/pull/59893) | Update dependencies |
| 0.0.5 | 2025-05-03 | [59299](https://github.com/airbytehq/airbyte/pull/59299) | Update dependencies |
| 0.0.4 | 2025-04-26 | [58781](https://github.com/airbytehq/airbyte/pull/58781) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58215](https://github.com/airbytehq/airbyte/pull/58215) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57669](https://github.com/airbytehq/airbyte/pull/57669) | Update dependencies |
| 0.0.1 | 2025-04-11 | [57586](https://github.com/airbytehq/airbyte/pull/57586) | Initial release by [@natikgadzhi](https://github.com/natikgadzhi) |

</details>
