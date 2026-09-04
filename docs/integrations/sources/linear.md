# Linear

<HideInUI>

This page contains the setup guide and reference information for the [Linear](https://linear.app/) source connector.

</HideInUI>

[Linear](https://linear.app/) is a project management and issue tracking tool designed for software teams. It provides a streamlined interface for managing issues, sprints, and product roadmaps with a focus on speed and simplicity.

## Prerequisites

- A Linear account
- One of the following authentication methods:
  - **OAuth 2.0 (Airbyte Cloud)**: A Linear workspace administrator account with permission to authorize the required workspace data. Airbyte supplies the OAuth application.
  - **OAuth 2.0 (Self-managed)**: A Linear OAuth application and its client ID and client secret. You also need a Linear workspace administrator account with permission to authorize the required workspace data, because the connector installs the app at the workspace level.
  - **API Key**: A Linear personal API key.
- To sync the `customers`, `customer_needs`, `customer_statuses`, and `customer_tiers` streams: Linear's Customer Requests feature enabled in your workspace. OAuth connections also need the `customer:read` scope; API keys don't use scopes. See [Customer Requests streams](#customer-requests-streams).

## Setup guide

## Set up Linear

The Linear source connector supports OAuth 2.0 and API key authentication. Starting with connector version `0.2.19`, the setup form selects OAuth 2.0 by default.

### OAuth 2.0

1. If you use Airbyte Cloud, Airbyte supplies the OAuth application. If you use a self-managed deployment, create a [Linear OAuth application](https://linear.app/settings/api/applications/new).
2. For a self-managed deployment, add the redirect callback URL shown during the Airbyte OAuth setup to the application's redirect URLs. Linear rejects authorization requests whose `redirect_uri` isn't registered on the app. Copy the application's client ID and client secret.
3. In Airbyte, choose **OAuth 2.0**. For self-managed deployments, enter the client ID and client secret from your Linear application, then complete the authorization flow.
4. Linear access tokens last 24 hours, and the connector refreshes them automatically. Each refresh returns a new refresh token, and the connector stores it in the source configuration. Linear rotates the refresh token on every exchange, so the previous token stops working apart from a short replay window that lets the connector retry an interrupted refresh.

The connector requests the `read`, `customer:read`, and `initiative:read` scopes and authorizes with Linear's [actor authorization](https://linear.app/developers/oauth-actor-authorization) (`actor=app`), so the authorization installs the app in the workspace instead of acting as the individual who approved it. Linear treats `customer:read` as an app-only scope and requires admin permissions to install an app, so a workspace admin has to complete the authorization.

If your Airbyte deployment doesn't provide a browser-based OAuth flow, complete Linear's [authorization code flow](https://linear.app/developers/oauth-2-0-authentication) yourself and use the resulting refresh token:

1. Open `https://linear.app/oauth/authorize?client_id=<CLIENT_ID>&redirect_uri=<REDIRECT_URI>&response_type=code&state=<STATE>&scope=read,customer:read,initiative:read&actor=app&prompt=consent` in a browser and approve the app. Generate a random `state` value and verify it on the callback to protect against CSRF. The `prompt=consent` parameter forces Linear to show the consent screen. Linear redirects to your redirect URI with a `code` parameter.
2. Exchange the code for tokens by sending a form-encoded `POST` request to `https://api.linear.app/oauth/token` with `code`, `redirect_uri`, `client_id`, `client_secret`, and `grant_type=authorization_code`.
3. Copy the `refresh_token` from the response into the connector configuration. The connector uses it to mint access tokens, which Linear expires after 24 hours. The first refresh replaces this token, so don't reuse the same value in another source or keep a copy to paste in later.

### API key

1. Log in to your [Linear](https://linear.app/) account.
2. Navigate to **Settings** by clicking your workspace name in the sidebar.
3. Select **Security & access** from the settings menu.
4. Scroll to the **Personal API keys** section.
5. Click **Create key**, give the key a descriptive label (for example, `airbyte`), and click **Create**.
6. Copy the API key and store it securely. Linear only displays the key once.

The API key inherits your user's permissions in the workspace. The connector can only sync data you can see in Linear.

For more information, see the [Linear GraphQL API documentation](https://linear.app/developers/graphql).

## Set up the Linear connector in Airbyte

1. In the Airbyte UI, navigate to **Sources** and click **+ New source**.
2. Select **Linear** from the list of available sources.
3. Enter a **Source name** of your choosing.
4. For **Authentication**, choose **OAuth 2.0** (the default) or **API Key**.
5. Enter the required credentials for your authentication method.
6. Optionally, enter a **Start Date** in ISO 8601 format (for example, `2024-01-01T00:00:00.000Z`). Only records updated on or after this date are replicated for streams that support incremental sync. If you leave this field empty, the connector defaults to two years before the time of the first sync.
7. Optionally, adjust the **Number of concurrent workers** (default 4, range 1–10). Higher values speed up syncs but increase the risk of hitting Linear's rate limits. OAuth provides more requests per hour (5,000 versus 2,500 for API keys), but a lower hourly complexity budget (2,000,000 versus 3,000,000). Because this connector uses GraphQL, complexity is usually the binding limit, so increase this value only after you have observed headroom.
8. Click **Set up source** and wait for the connection test to complete.

Existing connections that authenticated with a Linear API key continue to use API key authentication after upgrading to connector version `0.2.1` or later. If you upgraded an API key connection to `0.2.0` and it no longer passes connection checks, upgrade to `0.2.1` or later.

## Supported sync modes

The Linear source connector supports the following sync modes:

- [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped)

Streams that support incremental sync use the `updatedAt` field as the cursor. The Start Date you set when configuring the connector is the lower bound for the first incremental sync. Subsequent syncs use the most recent `updatedAt` value from the previous sync as the new lower bound.

That lower bound is inclusive, so a record whose `updatedAt` matches the stored cursor exactly is read again on the next sync. Overlap is also wider after a failed sync. Each stream gets its own cursor, and the connector advances a stream's cursor only once that stream finishes, so a stream interrupted by a failure re-reads everything updated since its own last successful run. Streams that finished before the failure keep their new cursor and aren't affected. In **Incremental - Append + Deduped** mode the destination collapses these repeats. In **Incremental - Append** mode they land as extra rows, so deduplicate on the primary key downstream if that matters to you.

The following streams are full-refresh only because the Linear GraphQL API doesn't expose a filter argument that the connector can use to request only updated records: `project_statuses`, `issue_relations`, `customer_statuses`, `customer_tiers`, and `initiative_to_projects`. `issue_history` is full-refresh only for a different reason: Linear exposes an issue's history only through that issue, so the connector reads it issue by issue. See [Issue history](#issue-history).

## Supported Streams

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
| `initiatives` | Yes | Strategic initiatives tracked across projects. |
| `initiative_to_projects` | No | Relationships between initiatives and projects. |
| `issue_history` | No | Changes made to issues over time. |
| `issue_labels` | Yes | Labels that can be applied to issues. |
| `issue_relations` | No | Relationships between issues (for example, blocks and duplicates). |
| `issues` | Yes | Issues in every team. |
| `project_milestones` | Yes | Milestones defined inside projects. |
| `project_statuses` | No | Status definitions for projects. |
| `project_updates` | Yes | Updates posted for projects. |
| `projects` | Yes | Projects across all teams. |
| `teams` | Yes | Teams in your Linear workspace. |
| `users` | Yes | Users in your Linear workspace. |
| `workflow_states` | Yes | Workflow states (for example, Todo, In Progress, Done) defined by each team. |

Starting with connector version `0.2.16`, new connections pre-select `issues`, `projects`, `teams`, `users`, `comments`, `cycles`, `issue_labels`, and `workflow_states`. Enable the other streams yourself if you need them. Existing connections keep the streams you already selected.

### Customer Requests streams

The `customers`, `customer_needs`, `customer_statuses`, and `customer_tiers` streams read Linear's Customer Requests data. An admin has to enable Customer Requests in [Workspace Settings > Customer requests](https://linear.app/settings/customers), and OAuth connections need the `customer:read` scope, before your workspace has any of this data to sync. Customer tiers are also defined in those settings, so the `customer_tiers` stream stays empty until someone configures tiers.

:::caution Behavior change in `0.2.23`
Before `0.2.23`, if Linear refused a Customer Requests query, the connector reported those streams as successful with zero records. Starting with `0.2.23`, the sync fails and repeats Linear's explanation of the refusal. If your workspace doesn't have Customer Requests enabled, deselect `customers`, `customer_needs`, `customer_statuses`, and `customer_tiers` in the connection's schema tab. See [Syncs fail on errors Linear returns in the response body](#syncs-fail-on-errors-linear-returns-in-the-response-body).
:::

See Linear's [Customer Requests documentation](https://linear.app/docs/customer-requests) for details.

### Initiative streams

The `initiatives` and `initiative_to_projects` streams need Linear's `initiative:read` scope. Connector version `0.4.0` requests it, but Linear grants scopes when you authorize, so OAuth sources created before `0.4.0` hold tokens without it. If either stream fails with `Invalid scope: initiative:read ... required for app user to read initiative data`, a workspace admin must re-authenticate the source in Sources > your source > Settings. API key sources are unaffected.

### Issue history

`issue_history` is the only stream the connector reads through a parent stream. On every sync it pages through all your issues, then sends a separate query for each issue to collect that issue's history entries, 50 entries per page. Two consequences:

- Request volume and sync time scale with your issue count, not with how much changed since the last sync, and the queries count against the same hourly request and complexity budgets as every other stream. On a workspace with many issues, selecting this stream can slow every other stream in the connection. See [Rate limiting](#rate-limiting).
- The stream has no cursor, so each sync returns the complete history again. Sync it in **Full Refresh - Overwrite** mode unless you have a reason to keep the repeats. In **Full Refresh - Append** mode, every sync appends another full copy.

The connector reads the parent issues itself, so you don't need to select the `issues` stream to sync `issue_history`. Each history record carries an `issueId` field that the connector adds from the parent issue; Linear's own response doesn't include it. The primary key is `issueId` and `id` together.

### Archived records

Linear hides archived records from API responses by default rather than deleting them, and it archives some records for you: completed issues, cycles, and projects are auto-archived over time. Deletion is a separate action, described below in [Limitations & Troubleshooting](#limitations--troubleshooting). Starting with connector version `0.3.0`, every stream asks Linear for archived records, so they sync alongside active ones. Each record's `archivedAt` field holds the time Linear archived it, and is `null` while the record is active.

Before `0.3.0` the connector didn't request archived records, so Linear left them out of every response and `archivedAt` was always `null`. Upgrading changes what your syncs return:

- Streams you sync in full refresh mode return all archived records on the next sync. In an established workspace this can be a large one-time increase in volume.
- Streams you sync incrementally return an archived record only when its `updatedAt` value is later than the stream's cursor. Records Linear archives from now on qualify; records archived before the upgrade usually don't, because their `updatedAt` predates the cursor. To pick those up, [refresh the stream](https://docs.airbyte.com/platform/operator-guides/refreshes).

### Date and timestamp columns

Starting with connector version `1.0.0`, the connector declares `date` and `date-time` formats on Linear's temporal fields, so destinations create date and timestamp columns for them instead of strings. `issues.dueDate`, `projects.startDate`, `projects.targetDate`, `project_milestones.targetDate`, `initiatives.targetDate`, `issue_history.fromDueDate`, and `issue_history.toDueDate` become date columns, because Linear stores them as calendar dates with no time. Every other temporal field, including `createdAt`, `updatedAt`, and `archivedAt`, becomes a timestamp column.

This changes existing column types in your destination. Refresh the source schema and clear the affected streams after upgrading, and update downstream models that cast these columns from strings. See the [Linear migration guide](/integrations/sources/linear-migrations#upgrading-to-100).

### Fields Linear deprecated

Version `1.0.0` stops requesting fields Linear has deprecated: `users.inviteHash`, `users.calendarHash`, `teams.inviteHash`, `teams.private`, `teams.markedAsDuplicateWorkflowState` (and the derived `teams.markedAsDuplicateWorkflowStateId`), and `customer_statuses.type`. Those columns stop receiving values after you upgrade.

The `teams` stream carries `visibility` in place of `private`. It's a string rather than a boolean, with three values: `public` for teams every workspace member can see, `private` for teams only their own members can see, and `restricted` for a non-private team inside a private team's boundary. A `restricted` team isn't private, so write downstream logic as `visibility = 'private'` rather than treating anything that isn't `public` as private.

## Limitations & Troubleshooting

### Rate limiting

The Linear API uses a leaky bucket algorithm for rate limiting. Starting with connector version `0.2.22`, the connector paces its own requests to stay below Linear's hourly request ceiling for your authentication method, spreading requests across the hour instead of sending them in bursts. The connector also detects rate-limit errors returned by the API and automatically backs off until the rate-limit window resets. This reactive backoff still matters because the connector can't see quota consumed by other applications using the same credentials, and it doesn't track query complexity. Syncs may slow down during pacing or backoff periods but resume without manual intervention.

Linear enforces three types of rate limits:

- **Request limits**: 2,500 requests per user per hour for API key authentication, 5,000 for OAuth app authentication. All requests by the same user share the same quota.
- **Endpoint-specific limits**: Certain queries have lower per-endpoint limits. The connector respects the `X-RateLimit-Endpoint-Requests-Reset` header when these are hit.
- **Complexity limits**: Each query's complexity is calculated based on the number of requested fields and pagination depth. The maximum single-query complexity is 10,000 points. The hourly complexity budget is 3,000,000 points for API key authentication and 2,000,000 for OAuth. Because this connector uses GraphQL, the complexity budget is usually the binding limit before the request limit.

Workspace-level OAuth applications receive dynamically increased limits based on the number of paid seats. For more information, see the [Linear rate limiting documentation](https://linear.app/developers/rate-limiting).

### OAuth authorization stops working

If an OAuth source starts failing with an authorization error, re-authenticate the source from its settings page to issue a fresh refresh token. Linear rotates the refresh token every time the connector exchanges it, so a source breaks permanently once its stored token is replaced with an older value. Don't restore an earlier copy of a source's configuration, and don't paste the same refresh token into more than one source.

### The connection test only reads the issues stream

The connection test queries the `issues` stream. It confirms that Linear accepts your credentials, but it doesn't check any other stream. Credentials that can't reach Customer Requests data still pass the test, and the problem only surfaces when a sync reads those streams.

### Data availability

The connector retrieves only the data its credentials can see. With API key authentication, that's everything the key's owner can see in Linear. With OAuth, it's what the installed app can see in the workspace. If teams, projects, or issues are missing from your synced data, check those permissions in Linear first.

### Deleted records aren't removed from your destination

When you delete an issue or project in Linear, it moves to the team's **Recently deleted** tab for 30 days before Linear removes it permanently. The `issues`, `projects`, `initiatives`, and `issue_history` streams carry a `trashed` field for this state, so you can filter these records out downstream. No other stream exposes `trashed`.

Once Linear removes a record permanently, nothing in the API reports it, and Airbyte doesn't delete rows it has already written, so the row stays in your destination. If you need to find rows that no longer exist in Linear, compare a full refresh of the stream against your destination table.

### Syncs fail on errors Linear returns in the response body

Linear's GraphQL API often reports a problem in the response body instead of in the HTTP status code. Starting with version `0.2.23`, a sync fails when Linear returns errors this way and the response contains no usable data, unless the response is one the connector retries. Before `0.2.23` the connector discarded those errors and treated the response as an empty but successful stream, so a connection that had been completing can start failing on this version even though nothing changed in Linear.

Every one of these failures repeats Linear's own explanation of the problem. Use that text to decide what to do:

- **Rejected credentials**: confirm your API key still exists under **Settings** > **Security & access** > **Personal API keys** in Linear, or re-authenticate an OAuth source to issue a fresh refresh token.
- **Denied access to data or to a feature your workspace doesn't have**: grant your credentials access to that data in Linear, or deselect the stream. Customer Requests streams are the most common cause. See [Customer Requests streams](#customer-requests-streams).
- **An invalid query**: this is a connector defect rather than a configuration problem. Report it to Airbyte support.

Responses that contain both errors and usable records still sync. If Linear returns partial results, the connector keeps the records it received.

Request timeouts and Linear's 5xx responses are retried, so they only fail a sync if they persist. A rejected credential, denied access, or an invalid query fails immediately no matter which status code accompanies it.

### Programmatic configuration

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

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------- | ---- | ------------ | ------- |
| 1.0.0 | 2026-08-28 | [85095](https://github.com/airbytehq/airbyte/pull/85095) | Breaking: declare `date` and `date-time` formats on every temporal field, and drop the fields Linear deprecated in the `users`, `teams`, and `customer_statuses` queries (`teams.visibility` replaces `teams.private`). See the [migration guide](/integrations/sources/linear-migrations#upgrading-to-100). |
| 0.4.0 | 2026-08-27 | [85056](https://github.com/airbytehq/airbyte/pull/85056) | Add initiatives, initiative-to-project relationships, project updates, and issue history streams |
| 0.3.1 | 2026-08-26 | [85053](https://github.com/airbytehq/airbyte/pull/85053) | Add regression tests covering incremental cursor boundary behavior |
| 0.3.0 | 2026-08-26 | [84950](https://github.com/airbytehq/airbyte/pull/84950) | Sync archived records in every stream and declare `archivedAt` (plus `trashed` on `issues` and `projects`) in the stream schemas |
| 0.2.23 | 2026-08-25 | [84949](https://github.com/airbytehq/airbyte/pull/84949) | Classify Linear GraphQL errors: surface actionable config errors for invalid credentials, fail fast on invalid queries, and fail any response carrying a GraphQL `errors` array instead of reporting it as a successful empty stream |
| 0.2.22 | 2026-08-25 | [84954](https://github.com/airbytehq/airbyte/pull/84954) | Add proactive rate-limit pacing for Linear API requests |
| 0.2.21 | 2026-08-24 | [84947](https://github.com/airbytehq/airbyte/pull/84947) | Fix OAuth consent scope encoding and persist the access token issued during authorization. |
| 0.2.20 | 2026-08-24 | [84947](https://github.com/airbytehq/airbyte/pull/84947) | Persist rotated OAuth refresh tokens so OAuth connections keep working after the first token refresh. |
| 0.2.19 | 2026-08-24 | [84947](https://github.com/airbytehq/airbyte/pull/84947) | Make OAuth 2.0 the default authentication method in the connector setup form |
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
