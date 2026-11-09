# Pylon

<HideInUI>

This page contains the setup guide and reference information for the [Pylon](https://usepylon.com) source connector.

</HideInUI>

## Prerequisites

- A Pylon API token created by an Admin under **Settings > Integrations & dev > API tokens**. Choose a role that can read the data you plan to sync. If the token acts as a user or bot, it inherits that identity's current role and permissions. Pylon tokens have no separate scopes. For creation steps, see [Pylon's authentication guide](https://docs.usepylon.com/pylon-docs/developer/api/authentication).
- Access to Tags for the source connection check, plus access to each selected stream and its parent stream. A successful connection check does not verify access to every stream.

## Setup guide

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

The Pylon source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- Full Refresh | Overwrite
- Full Refresh | Append
- Incremental Sync | Append (Issues stream only)
- Incremental Sync | Append + Deduped (Issues stream only; recommended)

Issue time filters are inclusive. Each incremental sync can re-emit issues at the saved cursor, and adjacent query windows can replay records at their shared edges. **Incremental | Append** retains these replays as duplicate rows, including another copy each sync of an issue at the saved cursor. Use **Incremental | Append + Deduped**, with `id` as the primary key, to keep one row per issue.

An issue updated exactly at a shared window edge also generates two child partitions. **Issue Messages** and **Issue Threads** can therefore emit the same child rows twice within one sync. **Full Refresh | Overwrite** does not deduplicate rows within that sync. With a fixed Start Date, this rare edge case can recur on every sync until the issue is updated. It does not lose data; deduplicate child rows downstream by `id` if needed.

## Supported streams

The Pylon source connector supports the following streams:

- [Accounts](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/accounts)
- [Activity Types](https://docs.usepylon.com/pylon-docs/developer/api/api-reference)
- [Contacts](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/contacts)
- [Custom Fields](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/custom-fields)
- [Issues](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/issues) (Incremental)
  - [Issue Messages](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/messages)
  - [Issue Threads](https://docs.usepylon.com/pylon-docs/developer/api/api-reference)
- [Issue Statuses](https://docs.usepylon.com/pylon-docs/developer/api/api-reference)
- [Knowledge Bases](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/knowledge-base)
  - [Knowledge Base Articles](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/knowledge-base)
- [Tags](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/tags)
- [Teams](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/teams)
- [Ticket Forms](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/ticket-forms)
- [User Roles](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/user-roles)
- [Users](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/users)

### Stream notes

- **Issues** is the only incremental stream. It uses `updated_at` as its cursor field and the `POST /issues/search` endpoint, so incremental syncs capture all issue modifications, not just newly created issues. The connector chooses 30-day query windows; this is not a documented Pylon search API limit. Inclusive bounds overlap at window edges to avoid subsecond gaps. The final query can extend up to one second beyond the cursor interval's end, and its bounds remain fixed across pages.
- **Issue Messages** and **Issue Threads** are full-refresh child streams of Issues. On every sync, they re-read all messages or threads for each issue updated since **Start Date**, independently of the Issues stream's saved incremental cursor. They do not filter on the message or thread timestamp, so child records can predate **Start Date**. Both streams include `issue_id`, which you can join to Issues on `id`.
- **Knowledge Base Articles** is a full-refresh child stream of Knowledge Bases. It includes `knowledge_base_id`, which you can join to Knowledge Bases on `id`.
- **Custom Fields** retrieves field definitions for three object types: account, issue, and contact. It does not retrieve definitions for other Pylon object types.
- **Users** includes both active and deactivated users.
- All streams other than Issues support full refresh only and do not save an incremental cursor. **Start Date** does not limit streams other than Issues, Issue Messages, and Issue Threads.

### Upgrading to 0.0.8

Connector version 0.0.8 switches the Issues stream from `GET /issues` (cursored on `created_at`) to `POST /issues/search` (cursored on `updated_at`) so that incremental syncs capture updates to existing issues, not just newly created ones. Connections upgrading from any earlier version automatically run a one-time state migration that rewinds the issues cursor and re-pulls history starting from:

- the **Start Date** you configured, if it is set, or
- **30 days before the first sync**, if Start Date is unset.

If you need a longer backfill, set Start Date to the desired date before the first sync on 0.0.8. Subsequent syncs use the new `updated_at` cursor incrementally and do not re-pull history.

## Limitations & Troubleshooting

### Authentication and permissions

- For `wrong_region_token` (HTTP 401), change **Region** to match your Pylon tenant and token.
- For `invalid_api_token` (HTTP 401), check that the token is correct and has not been rotated or revoked. If the token has an IP allowlist, allow the public egress IP addresses used by Airbyte. Pylon returns the same error when an IP address is blocked.
- For HTTP 403, give the token's role read access to the affected data, or deselect the stream. Child streams also require access to their parent data. The connector fails on permission errors rather than silently skipping inaccessible streams.

For other error codes, see [Pylon's error reference](https://docs.usepylon.com/pylon-docs/developer/api/errors).

### Rate limiting

The [Pylon API rate limits](https://docs.usepylon.com/pylon-docs/developer/api/rate-limits) apply per endpoint and are shared by all API tokens in your organization:

- `GET /activity-types` and `GET /issue-statuses`: 30 requests per minute each.
- `POST /issues/search`, `GET /issues/{id}/messages`, `GET /issues/{id}/threads`, and `GET /knowledge-bases/{id}/articles`: 120 requests per minute each.
- Other endpoints used by this connector: 300 requests per minute each.

The connector budgets requests separately for each endpoint. For rate-limited responses (HTTP 429), it uses `Retry-After`, then `X-Retry-After` if the first header is absent, then exponential backoff if neither is present, with up to five retries. A selected retry-header wait of 120 seconds or more stops the stream rather than waiting. By default, the connector uses three workers, with a minimum of two and a maximum of ten. Lower **Number of Workers** if other integrations also use your organization's API allowance.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                        |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------- |
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
