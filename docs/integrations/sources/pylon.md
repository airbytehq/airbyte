# Pylon

<HideInUI>

This page contains the setup guide and reference information for the [Pylon](https://usepylon.com) source connector.

</HideInUI>

## Prerequisites

- A Pylon API token created by an Admin under **Settings > Integrations & dev > API tokens**. Choose a role that can read the data you plan to sync. If the token acts as a user or bot, it inherits that identity's current role and permissions. Pylon tokens have no separate scopes. For creation steps, see [Pylon's authentication guide](https://docs.usepylon.com/pylon-docs/developer/api/authentication#create-an-api-token).
- Access to Tags for the source connection check, plus access to each selected stream and its parent stream. A successful connection check does not verify access to every stream.

## Setup guide

Before you set up the source, create a Pylon API token with a role that can read the data you plan to sync, as described in [Prerequisites](#prerequisites). For creation steps, see [Pylon's authentication guide](https://docs.usepylon.com/pylon-docs/developer/api/authentication#create-an-api-token).

## Set up Pylon

### For Airbyte Cloud

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources**, then click **+ New source**.
3. Select **Pylon** as the source type.
4. Enter a name for the Pylon connector.
5. Fill in the fields described below.
6. Click **Set up source**.

### For Airbyte Open Source

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources**, then click **+ New source**.
3. Select **Pylon** as the source type.
4. Enter a name for the Pylon connector.
5. Fill in the fields described below.
6. Click **Set up source**.

<FieldAnchor field="api_token">

Enter only your **API Token**, without the word `Bearer` or surrounding spaces. The connector adds the authentication header to all requests to the Pylon API.

</FieldAnchor>

<FieldAnchor field="region">

Select **Region** to match your Pylon tenant and API token. **US** (the default) uses `https://api.usepylon.com` with tokens prefixed `pylon_api_`. **EU** uses `https://api.eu.usepylon.com` with tokens prefixed `pylon_api_eu_`. For older tokens without a prefix, choose the region where your Pylon tenant is hosted. Existing configurations without Region continue to use US.

</FieldAnchor>

<FieldAnchor field="start_date">

Optionally, enter a **Start Date** in UTC format (`YYYY-MM-DDTHH:MM:SSZ`). The connector uses the issue's `updated_at`, not its creation date, to select Issues and the parent issues for Issue Messages and Issue Threads. If omitted, the starting point defaults to 30 days before each sync. Set an explicit date to keep a fixed history window for the child streams. Subsequent incremental Issues syncs resume from the saved cursor.

</FieldAnchor>

<FieldAnchor field="num_workers">

Optionally, set **Number of Workers** from **2** to **10** (default: **3**). At least two workers are required so child streams can read records while generating parent partitions. Lower this value if other integrations share your organization's API allowance.

</FieldAnchor>

## Supported sync modes

The Pylon source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts#sync-mode):

- Full Refresh | Overwrite
- Full Refresh | Append
- Incremental Sync | Append (Issues stream only)
- Incremental Sync | Append + Deduped (Issues stream only; recommended)

Issue time filters are inclusive. Each incremental sync can re-emit issues at the saved cursor, and adjacent query windows can replay records at their shared edges. **Incremental | Append** retains these replays as duplicate rows, including another copy each sync of an issue at the saved cursor. Use **Incremental | Append + Deduped**, with `id` as the primary key, to keep one row per issue.

An issue updated exactly at a shared window edge also generates two child partitions. **Issue Messages** and **Issue Threads** can therefore emit the same child rows twice within one sync. **Full Refresh | Overwrite** does not deduplicate rows within that sync. With a fixed Start Date, this rare edge case can recur on every sync until the issue is updated. It does not lose data; deduplicate child rows downstream by `id` if needed.

## Supported Streams

| Stream | Pylon API endpoint | Sync modes | Primary key | Parent stream (join key) |
| --- | --- | --- | --- | --- |
| Accounts | [`GET /accounts`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/accounts#get-accounts) | Full Refresh | `id` | None |
| Activity Types | [`GET /activity-types`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/accounts/activities#get-activity-types) | Full Refresh | `id` | None |
| Audit Logs | [`GET /audit-logs`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/audit-logs#get-audit-logs) | Full Refresh | `id` | None |
| Contacts | [`GET /contacts`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/contacts#get-contacts) | Full Refresh | `id` | None |
| Custom Fields | [`GET /custom-fields`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/custom-fields#get-custom-fields) | Full Refresh | `id` | None |
| Issues | [`POST /issues/search`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/issues#post-issues-search) | Full Refresh, Incremental (`updated_at`) | `id` | None |
| Issue Messages | [`GET /issues/{id}/messages`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/messages#get-issues-id-messages) | Full Refresh | `id` | Issues (`issue_id` = Issues `id`) |
| Issue Threads | [`GET /issues/{id}/threads`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/messages#get-issues-id-threads) | Full Refresh | `id` | Issues (`issue_id` = Issues `id`) |
| Issue Statuses | [`GET /issue-statuses`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/issues#get-issue-statuses) | Full Refresh | `slug` | None |
| Knowledge Bases | [`GET /knowledge-bases`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/knowledge-base#get-knowledge-bases) | Full Refresh | `id` | None |
| Knowledge Base Articles | [`GET /knowledge-bases/{id}/articles`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/knowledge-base#get-knowledge-bases-id-articles) | Full Refresh | `id` | Knowledge Bases (`knowledge_base_id` = Knowledge Bases `id`) |
| Macro Groups | [`GET /macro-groups`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/macros#get-macro-groups) | Full Refresh | `id` | None |
| Surveys | [`GET /surveys`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/surveys#get-surveys) | Full Refresh | `id` | None |
| Tags | [`GET /tags`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/tags#get-tags) | Full Refresh | `id` | None |
| Teams | [`GET /teams`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/teams#get-teams) | Full Refresh | `id` | None |
| Ticket Forms | [`GET /ticket-forms`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/ticket-forms#get-ticket-forms) | Full Refresh | `id` | None |
| Training Data | [`GET /training-data`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/training-data#get-training-data) | Full Refresh | `id` | None |
| User Roles | [`GET /user-roles`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/user-roles#get-user-roles) | Full Refresh | `id` | None |
| Users | [`GET /users`](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/users#get-users) | Full Refresh | `id` | None |

### Stream notes

- **Audit Logs** requires an Admin-role API token and a Pylon plan that includes audit log access. A 403 on this stream fails the sync; deselect it if the token isn't Admin. Enterprise organizations get the full audit history on every sync; other plans get a rolling window of the last 30 days. **Start Date** does not apply. Use **Full Refresh | Append**, de-duplicating on `id` downstream, to keep history beyond 30 days. Append re-writes the window's events on each sync. Overwrite modes keep only the current window (30 days on non-Enterprise plans).
- **Issues** is the only incremental stream. It uses `updated_at` as its cursor field and the `POST /issues/search` endpoint, so incremental syncs capture all issue modifications, not just newly created issues. The connector chooses 30-day query windows; this is not a documented Pylon search API limit. Inclusive bounds overlap at window edges to avoid subsecond gaps. The final query can extend up to one second beyond the cursor interval's end, and its bounds remain fixed across pages.
- **Issue Messages** and **Issue Threads** are full-refresh child streams of Issues. On every sync, they re-read all messages or threads for each issue updated since **Start Date**, independently of the Issues stream's saved incremental cursor. They do not filter on the message or thread timestamp, so child records can predate **Start Date**. Both streams include `issue_id`, which you can join to Issues on `id`.
- **Knowledge Base Articles** is a full-refresh child stream of Knowledge Bases. It includes `knowledge_base_id`, which you can join to Knowledge Bases on `id`.
- **Custom Fields** retrieves field definitions for three object types: account, issue, and contact. It does not retrieve definitions for other Pylon object types.
- **Users** includes both active and deactivated users.
- **Issue Statuses** uses `slug` as its primary key because issue status records have no `id` field.
- **Macro Groups** returns macro groups only, not the macros in them. **Surveys** returns survey definitions, not survey responses. **Training Data** returns training data configurations. Pylon doesn't paginate these three endpoints, so the connector reads each in a single request.
- **Tags** returns tags for every object type in one stream. Use `object_type` (for example `account`, `article`, or `issue`) to tell them apart.
- **Teams** includes each team's members in a nested `users` array, plus its assignment settings. The connector has no separate team membership stream.
- All streams other than Issues support full refresh only and do not save an incremental cursor. **Start Date** does not limit streams other than Issues, Issue Messages, and Issue Threads.

## Upgrade notes

### Upgrading to 1.0.0

Version 1.0.0 is a breaking change: `tags` on Accounts and Issues is now an array of strings, and eight timestamp fields on Accounts, Issues, Issue Messages, and Custom Fields are now typed as `date-time`. After upgrading, refresh the source schema; some destinations also require you to clear the affected streams. For the changed fields and upgrade steps, see the [Pylon migration guide](/integrations/sources/pylon-migrations#upgrading-to-100).

### Upgrading to 0.0.8

Connector version 0.0.8 switches the Issues stream from `GET /issues` (cursored on `created_at`) to `POST /issues/search` (cursored on `updated_at`) so that incremental syncs capture updates to existing issues, not just newly created ones. Connections upgrading from any earlier version automatically run a one-time state migration that rewinds the issues cursor and re-pulls history starting from:

- the **Start Date** you configured, if it is set, or
- **30 days before the first sync**, if Start Date is unset.

If you need a longer backfill, set Start Date to the desired date before the first sync on 0.0.8. Subsequent syncs use the new `updated_at` cursor incrementally and do not re-pull history.

## Limitations & Troubleshooting

### Authentication and permissions

- For `wrong_region_token` ([HTTP 401](https://docs.usepylon.com/pylon-docs/developer/api/errors#authentication-401)), change **Region** to match your Pylon tenant and token.
- For `invalid_api_token` (HTTP 401), check that the token is correct and has not been rotated or revoked. If the token has an [IP allowlist](https://docs.usepylon.com/pylon-docs/developer/api/authentication#ip-allowlist), allow the public egress IP addresses used by Airbyte. Pylon returns the same error when an IP address is blocked.
- For [HTTP 403](https://docs.usepylon.com/pylon-docs/developer/api/errors#authorization-403), give the token's role read access to the affected data, or deselect the stream. Child streams also require access to their parent data. The connector fails on permission errors rather than silently skipping inaccessible streams.

For other error codes, see [Pylon's error reference](https://docs.usepylon.com/pylon-docs/developer/api/errors#error-codes).

### Rate limiting

The [Pylon API rate limits](https://docs.usepylon.com/pylon-docs/developer/api/rate-limits#how-limits-apply) apply per endpoint and are shared by all API tokens in your organization:

- `GET /activity-types` and `GET /issue-statuses`: 30 requests per minute each.
- `POST /issues/search`, `GET /issues/{id}/messages`, `GET /issues/{id}/threads`, and `GET /knowledge-bases/{id}/articles`: 120 requests per minute each.
- Other endpoints used by this connector: 300 requests per minute each.

The connector budgets requests separately for each endpoint. For rate-limited responses ([HTTP 429](https://docs.usepylon.com/pylon-docs/developer/api/rate-limits#handling-429-responses)), it uses `Retry-After`, then `X-Retry-After` if the first header is absent, then exponential backoff if neither is present, with up to five retries. A selected retry-header wait of 120 seconds or more stops the stream rather than waiting. By default, the connector uses three workers, with a minimum of two and a maximum of ten. Lower **Number of Workers** if other integrations also use your organization's API allowance.

### IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                        |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------- |
| 1.0.0 | 2026-11-12 | [92021](https://github.com/airbytehq/airbyte/pull/92021) | Type `tags` as strings and 8 timestamp fields as `date-time` |
| 0.1.0 | 2026-11-10 | [91827](https://github.com/airbytehq/airbyte/pull/91827) | Add Audit Logs, Macro Groups, Surveys, and Training Data streams, with an Admin-role error message for Audit Logs. |
| 0.0.32 | 2026-11-10 | [91678](https://github.com/airbytehq/airbyte/pull/91678) | Update dependencies |
| 0.0.31 | 2026-11-06 | [91022](https://github.com/airbytehq/airbyte/pull/91022) | Add EU region support, documented fields, deactivated users, inclusive issue windows, parent IDs on child streams, actionable errors, request budgets, and configurable concurrency. |
| 0.0.30 | 2026-11-03 | [90398](https://github.com/airbytehq/airbyte/pull/90398) | Simplify error handling while preserving retry and rate-limit behavior. |
| 0.0.29 | 2026-11-03 | [90704](https://github.com/airbytehq/airbyte/pull/90704) | Update dependencies |
| 0.0.28 | 2026-10-27 | [90041](https://github.com/airbytehq/airbyte/pull/90041) | Update dependencies |
| 0.0.27 | 2026-10-20 | [89362](https://github.com/airbytehq/airbyte/pull/89362) | Update dependencies |
| 0.0.26 | 2026-10-13 | [88765](https://github.com/airbytehq/airbyte/pull/88765) | Update dependencies |
| 0.0.25 | 2026-10-06 | [87996](https://github.com/airbytehq/airbyte/pull/87996) | Update dependencies |
| 0.0.24 | 2026-09-29 | [87314](https://github.com/airbytehq/airbyte/pull/87314) | Update dependencies |
| 0.0.23 | 2026-09-22 | [86771](https://github.com/airbytehq/airbyte/pull/86771) | Update dependencies |
| 0.0.22 | 2026-09-15 | [86190](https://github.com/airbytehq/airbyte/pull/86190) | Update dependencies |
| 0.0.21 | 2026-09-08 | [85622](https://github.com/airbytehq/airbyte/pull/85622) | Update dependencies |
| 0.0.20 | 2026-08-18 | [84722](https://github.com/airbytehq/airbyte/pull/84722) | Update dependencies |
| 0.0.19 | 2026-08-11 | [84079](https://github.com/airbytehq/airbyte/pull/84079) | Update dependencies |
| 0.0.18 | 2026-07-28 | [83194](https://github.com/airbytehq/airbyte/pull/83194) | Update to CDK 7.23.8 (fixes AirbyteCustomCodeNotPermittedError for bundled custom components) and remove the temporary Cloud version override |
| 0.0.17 | 2026-07-28 | [1082](https://github.com/airbytehq/airbyte-python-cdk/issues/1082) | Roll Cloud back to 0.0.15 — 0.0.16 is built on SDM 7.23.7, which breaks bundled custom components |
| 0.0.16 | 2026-07-28 | [83064](https://github.com/airbytehq/airbyte/pull/83064) | Update dependencies |
| 0.0.15 | 2026-07-21 | [82527](https://github.com/airbytehq/airbyte/pull/82527) | Update dependencies |
| 0.0.14 | 2026-07-14 | [81963](https://github.com/airbytehq/airbyte/pull/81963) | Update dependencies |
| 0.0.13 | 2026-06-30 | [81204](https://github.com/airbytehq/airbyte/pull/81204) | Update dependencies |
| 0.0.12 | 2026-06-23 | [80608](https://github.com/airbytehq/airbyte/pull/80608) | Update dependencies |
| 0.0.11 | 2026-06-16 | [80004](https://github.com/airbytehq/airbyte/pull/80004) | Update dependencies |
| 0.0.10 | 2026-06-09 | [79462](https://github.com/airbytehq/airbyte/pull/79462) | Update dependencies |
| 0.0.9 | 2026-06-02 | [78905](https://github.com/airbytehq/airbyte/pull/78905) | Update dependencies |
| 0.0.8 | 2026-05-07 | [76083](https://github.com/airbytehq/airbyte/pull/76083) | Switch the Issues stream to `POST /issues/search` cursored on `updated_at` for true incremental sync. State migration rewinds the issues cursor to the configured Start Date (or 30 days ago if unset) on the first sync after upgrade. |
| 0.0.7 | 2026-04-28 | [77394](https://github.com/airbytehq/airbyte/pull/77394) | Update dependencies |
| 0.0.6 | 2026-04-21 | [76721](https://github.com/airbytehq/airbyte/pull/76721) | Update dependencies |
| 0.0.5 | 2026-03-31 | [75855](https://github.com/airbytehq/airbyte/pull/75855) | Update dependencies |
| 0.0.4 | 2026-03-17 | [74921](https://github.com/airbytehq/airbyte/pull/74921) | Update dependencies |
| 0.0.3 | 2026-02-24 | [73850](https://github.com/airbytehq/airbyte/pull/73850) | Update dependencies |
| 0.0.2 | 2026-02-20 | [73693](https://github.com/airbytehq/airbyte/pull/73693) | Make start_date optional, default to 1 month ago |
| 0.0.1 | 2026-02-20 | [73624](https://github.com/airbytehq/airbyte/pull/73624) | Initial release of Pylon source connector |

</details>
