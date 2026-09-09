# Pipedrive

This page contains the setup guide and reference information for the Pipedrive source connector.

## Prerequisites

- A Pipedrive account with API access enabled for your user
- Your Pipedrive API Token
- A Start Date (in UTC) from which to begin replicating data

## Setup guide

### Step 1: Set up Pipedrive

The connector authenticates with a personal API token. Each token is tied to a Pipedrive user, so the connector can only read data that user is allowed to see.

1. In the Pipedrive web app, click your account name (top right), then **Company settings** > **Personal preferences** > **API**.
2. Copy the API token shown on that page. See [How to find the API token](https://pipedrive.readme.io/docs/how-to-find-the-api-token) for screenshots.

Pipedrive allows one active API token per user. If you regenerate it, update the connector configuration. If you belong to more than one company, each company has its own token.

If the **API** tab isn't visible, your company admin hasn't enabled API access for your permission set. Ask them to follow [Enabling API for company users](https://pipedrive.readme.io/docs/enabling-api-for-company-users).

### Step 2: Set up the Pipedrive connector in Airbyte

1. In the Airbyte UI, go to **Sources** and click **+ New source**.
2. Select **Pipedrive** from the list.
3. Enter a name for the source.
4. Fill in the fields below, then click **Set up source**.

<FieldAnchor field="api_token">

**API Token**: The personal API token you copied in Step 1. Airbyte sends it as the `api_token` query parameter on every request.

</FieldAnchor>

<FieldAnchor field="replication_start_date">

**Start Date**: A UTC date and time in the format `YYYY-MM-DDTHH:MM:SSZ`, for example `2017-01-25T00:00:00Z`. Streams that support incremental sync only replicate records modified on or after this date. Streams that don't support incremental sync ignore it and always return all records, except `deal_products`, which only expands the deals returned by the `deals` stream. A space instead of `T`, as in the example shown in the UI, also works. See [Incremental sync and Start Date](#incremental-sync-and-start-date).

</FieldAnchor>

When you click **Set up source**, Airbyte tests the connection by calling the [Currencies](https://developers.pipedrive.com/docs/api/v1/Currencies#getCurrencies) endpoint. Every API token can read it, so the test passes even on an account that has no deals yet.

## Supported sync modes

The Pipedrive source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

The connector uses the [Pipedrive API v1](https://developers.pipedrive.com/docs/api/v1). Ten streams support incremental sync; the rest are full refresh only. Stream names below match the names shown in Airbyte.

| Stream                | Sync modes                | Notes                                                                                                                                                                                                                                       |
| :-------------------- | :------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `activities`          | Full Refresh, Incremental | Read from [Recents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) with `items=activity`. Cursor: `update_time`.                                                                                                            |
| `activity_fields`     | Full Refresh              | [ActivityFields](https://developers.pipedrive.com/docs/api/v1/ActivityFields#getActivityFields)                                                                                                                                              |
| `activity_types`      | Full Refresh              | [ActivityTypes](https://developers.pipedrive.com/docs/api/v1/ActivityTypes#getActivityTypes)                                                                                                                                                 |
| `currencies`          | Full Refresh              | [Currencies](https://developers.pipedrive.com/docs/api/v1/Currencies#getCurrencies)                                                                                                                                                          |
| `deal_fields`         | Full Refresh              | [DealFields](https://developers.pipedrive.com/docs/api/v1/DealFields#getDealFields)                                                                                                                                                          |
| `deal_products`       | Full Refresh              | Products attached to each deal, fetched with one request per deal ([DealProducts](https://developers.pipedrive.com/docs/api/v1/DealProducts#getDealProducts)). The connector still calls the v1 path `GET /v1/deals/{id}/products`, which Pipedrive stopped supporting on 2026-08-01, and only expands deals returned by the `deals` stream. |
| `deals`               | Full Refresh, Incremental | Read from [Recents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) with `items=deal`. Cursor: `update_time`.                                                                                                                |
| `files`               | Full Refresh, Incremental | Read from [Recents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) with `items=file`. Cursor: `update_time`.                                                                                                                |
| `filters`             | Full Refresh, Incremental | Read from [Recents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) with `items=filter`. Cursor: `update_time`.                                                                                                              |
| `goals`               | Full Refresh              | [Goals](https://developers.pipedrive.com/docs/api/v1/Goals#getGoals)                                                                                                                                                                         |
| `lead_labels`         | Full Refresh              | [LeadLabels](https://developers.pipedrive.com/docs/api/v1/LeadLabels#getLeadLabels)                                                                                                                                                          |
| `leads`               | Full Refresh              | [Leads](https://developers.pipedrive.com/docs/api/v1/Leads#getLeads)                                                                                                                                                                         |
| `mail`                | Full Refresh              | Messages in each mail thread, fetched with one request per thread ([Mailbox getMailThreadMessages](https://developers.pipedrive.com/docs/api/v1/Mailbox#getMailThreadMessages)). See [Mail streams](#mail-streams).                          |
| `mailThreads`         | Full Refresh              | Mail threads from the `inbox`, `drafts`, `sent`, and `archive` folders ([Mailbox getMailThreads](https://developers.pipedrive.com/docs/api/v1/Mailbox#getMailThreads)). See [Mail streams](#mail-streams).                                    |
| `notes`               | Full Refresh, Incremental | Read from [Recents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) with `items=note`. Cursor: `update_time`.                                                                                                                |
| `organization_fields` | Full Refresh              | [OrganizationFields](https://developers.pipedrive.com/docs/api/v1/OrganizationFields#getOrganizationFields)                                                                                                                                  |
| `organizations`       | Full Refresh              | [Organizations](https://developers.pipedrive.com/docs/api/v1/Organizations#getOrganizations). The connector still calls the v1 path `GET /v1/organizations`, which Pipedrive stopped supporting on 2026-08-01. |
| `permission_sets`     | Full Refresh              | [PermissionSets](https://developers.pipedrive.com/docs/api/v1/PermissionSets#getPermissionSets)                                                                                                                                              |
| `person_fields`       | Full Refresh              | [PersonFields](https://developers.pipedrive.com/docs/api/v1/PersonFields#getPersonFields)                                                                                                                                                    |
| `persons`             | Full Refresh, Incremental | Read from [Recents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) with `items=person`. Cursor: `update_time`.                                                                                                              |
| `pipelines`           | Full Refresh, Incremental | Read from [Recents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) with `items=pipeline`. Cursor: `update_time`.                                                                                                            |
| `product_fields`      | Full Refresh              | [ProductFields](https://developers.pipedrive.com/docs/api/v1/ProductFields#getProductFields)                                                                                                                                                 |
| `products`            | Full Refresh, Incremental | Read from [Recents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) with `items=product`. Cursor: `update_time`.                                                                                                             |
| `roles`               | Full Refresh              | [Roles](https://developers.pipedrive.com/docs/api/v1/Roles#getRoles)                                                                                                                                                                         |
| `stages`              | Full Refresh, Incremental | Read from [Recents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) with `items=stage`. Cursor: `update_time`.                                                                                                               |
| `users`               | Full Refresh, Incremental | Read from [Recents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) with `items=user`. Cursor: `modified`.                                                                                                                   |

### Incremental sync and Start Date

The ten incremental streams read from the Pipedrive [Recents](https://developers.pipedrive.com/docs/api/v1/Recents#getRecents) endpoint, which returns items changed since a given timestamp. On the first sync, Airbyte passes your Start Date as `since_timestamp`. On later incremental syncs, it passes the latest cursor value it saw (`update_time`, or `modified` for `users`). Records modified before the Start Date are never replicated by these streams, and the Start Date has no effect on the full refresh streams.

Because these streams use the Recents endpoint, they return records that changed in the window, not only records that were created in it. For example, a deal created years before your Start Date shows up in `deals` as soon as anyone edits it.

Pipedrive's Recents endpoint returns at most one month of history, regardless of the Start Date. Records last modified more than a month before a sync are never backfilled by these streams, and moving the Start Date earlier does not retrieve them. The connector is being moved to Pipedrive API v2 to remove this limitation.

### Custom fields

Pipedrive lets you add custom fields to deals, persons, organizations, products, and activities. The API returns each custom field as a 40-character hash key (for example `dcf558aac1ae4e8c4f849ba5e668430d8df9be12`) rather than a readable name. The `deals`, `persons`, `organizations`, `products`, and `activities` streams pass these keys through as additional top-level properties on each record. To map a hash key to its label and type, sync the matching `*_fields` stream (`deal_fields`, `person_fields`, `organization_fields`, `product_fields`, or `activity_fields`) and join on the `key` column.

### Mail streams

`mailThreads` lists threads from the mailbox of the user who owns the API token. It queries each of the `inbox`, `drafts`, `sent`, and `archive` folders separately, so a thread that appears in more than one folder may be returned more than once. `mail` then requests the messages of every thread returned by `mailThreads`, one request per thread. Both streams are full refresh only, and you only see mail for the user whose token you configured, not for the whole company. If that user has not connected a mailbox to Pipedrive (Mail sync), both streams return no records.

## Performance considerations

Pipedrive enforces per-company, token-based [rate limits](https://pipedrive.readme.io/docs/core-api-concepts-rate-limiting) that depend on your plan and the number of seats. When Pipedrive answers with HTTP 429, the connector waits for the window reported in the `x-ratelimit-reset` header, falls back to exponential backoff when the header is missing, and retries up to ten times before failing the sync. If the header asks for a wait of 300 seconds or more, the connector stops the sync with a retryable error instead of waiting. Two limits apply per API token: a rolling 2-second burst window (20 to 120 requests depending on your plan) that recovers after a short wait, and a daily token budget (30,000 tokens times the plan multiplier and the number of seats) that, once exhausted, rejects every request until midnight in Pipedrive's server timezone. Waiting does not help in the second case; the failure message says so. If your account is close to its limits, run fewer streams per connection or schedule syncs less often.

Two streams make one request per parent record and can be slow on large accounts:

- `deal_products` makes one request per deal.
- `mail` makes one request per mail thread.

Consider leaving these streams disabled unless you need them.

## Limitations & Troubleshooting

<details>
<summary>Expand to see details about Pipedrive connector limitations and troubleshooting.</summary>

### Connector limitations

How the connector treats Pipedrive HTTP errors:

| HTTP status | Behavior |
|:------------|:---------|
| 401, 402, 403 | The sync fails with a configuration error that includes Pipedrive's error text. For `deal_products` and `mail`, a 403 on a single parent record is skipped and the sync continues. If the token can't read any deal products or mail messages at all, those two streams finish empty rather than failing. |
| 404, 410 | For `deal_products` and `mail`, a parent deal or mail thread deleted after the parent stream was read is skipped. On other streams these fail the sync. |
| 429 | Rate limited; retried as described under [Performance considerations](#performance-considerations). |
| 500, 502, 503, 504 | Temporary Pipedrive errors; retried with backoff. |

- The connector doesn't replicate deletes. A record deleted in Pipedrive stays in your destination until you clear and resync the stream.
- Only the ten streams marked Incremental above track state. The other sixteen streams are re-read in full on every sync.
- Full refresh streams ignore the Start Date, except `deal_products`, which only expands the deals returned by the `deals` stream.
- The incremental streams read Pipedrive's Recents endpoint, which returns at most one month of history. Records last modified more than a month before a sync are not backfilled, whatever the Start Date.
- `organizations` and `deal_products` call v1 endpoints that Pipedrive stopped supporting on 2026-08-01. They may stop working until the connector moves to API v2.
- The connector authenticates with a personal API token only. It doesn't support OAuth.
- The connector uses Pipedrive API v1. Newer fields that only exist in API v2 aren't available.

### Troubleshooting

- **Missing streams or empty streams**: Records are limited to what the token's user can see in Pipedrive. Use a token from a user with broader visibility, or from an admin. `mail` and `mailThreads` are empty unless that user has a mailbox connected in Pipedrive.
- **Records missing from incremental streams**: The Recents endpoint only returns records modified within the last month, so older records are not backfilled even with an earlier Start Date. Records that haven't been modified since the Start Date are excluded as well.
- **Custom fields appear as hash keys**: This is expected. See [Custom fields](#custom-fields).
- **Syncs fail with HTTP 429**: The retries were exhausted, which usually means the daily token budget is spent. Reduce the number of enabled streams, increase the interval between syncs, or upgrade the plan.
- **Setup or syncs fail with HTTP 401, 402 or 403**: The message carries Pipedrive's own error text. 401 means the token was not copied in full, has been regenerated, or API access is disabled for the user (see Step 1). 402 means the company account is not active. 403 means the token owner lacks permission for that data, or Cloudflare blocked the token after repeated rate-limit violations.

</details>

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2.4.6 | 2026-09-09 | [85770](https://github.com/airbytehq/airbyte/pull/85770) | Classify Pipedrive HTTP errors, wait on `x-ratelimit-reset` for 429s and skip inaccessible parent records in `deal_products` and `mail` |
| 2.4.5 | 2026-09-09 | [85767](https://github.com/airbytehq/airbyte/pull/85767) | Restructure the documentation and add contributor guides |
| 2.4.4 | 2026-09-09 | [85763](https://github.com/airbytehq/airbyte/pull/85763) | Set the heartbeat timeout, add a CODEOWNERS entry and tidy the changelog |
| 2.4.3 | 2026-09-09 | [85764](https://github.com/airbytehq/airbyte/pull/85764) | Use the `currencies` stream for the connection check and add suggested streams |
| 2.4.2 | 2026-09-09 | [85766](https://github.com/airbytehq/airbyte/pull/85766) | Make pagination null-safe for responses without `additional_data`, fixing the `mail` stream |
| 2.4.1 | 2026-09-09 | [85762](https://github.com/airbytehq/airbyte/pull/85762) | Fix `components.py` import failure on Python 3.11+ (use `default_factory` for decoder) and move to SDM 7.28.3 |
| 2.4.0 | 2025-02-28 | [54716](https://github.com/airbytehq/airbyte/pull/54716) | Refactor: Optimize Parameters, remove redundant code and Improve Manifest Readability |
| 2.3.8 | 2025-02-22 | [47292](https://github.com/airbytehq/airbyte/pull/47292) | Migrate to manifest only format |
| 2.3.7 | 2025-02-08 | [53488](https://github.com/airbytehq/airbyte/pull/53488) | Update dependencies |
| 2.3.6 | 2025-02-01 | [52986](https://github.com/airbytehq/airbyte/pull/52986) | Update dependencies |
| 2.3.5 | 2025-01-25 | [52477](https://github.com/airbytehq/airbyte/pull/52477) | Update dependencies |
| 2.3.4 | 2025-01-18 | [51922](https://github.com/airbytehq/airbyte/pull/51922) | Update dependencies |
| 2.3.3 | 2025-01-11 | [51305](https://github.com/airbytehq/airbyte/pull/51305) | Update dependencies |
| 2.3.2 | 2025-01-04 | [50929](https://github.com/airbytehq/airbyte/pull/50929) | Update dependencies |
| 2.3.1 | 2024-12-28 | [50288](https://github.com/airbytehq/airbyte/pull/50288) | Update dependencies |
| 2.3.0 | 2024-12-17 | [48615](https://github.com/airbytehq/airbyte/pull/48615) | Update airbyte-cdk to use concurrency |
| 2.2.28 | 2024-12-14 | [49692](https://github.com/airbytehq/airbyte/pull/49692) | Update dependencies |
| 2.2.27 | 2024-12-12 | [49041](https://github.com/airbytehq/airbyte/pull/49041) | Make the Docker image rootless (requires Airbyte platform 0.64 or later) |
| 2.2.26 | 2024-11-04 | [48293](https://github.com/airbytehq/airbyte/pull/48293) | Update dependencies |
| 2.2.25 | 2024-10-29 | [47743](https://github.com/airbytehq/airbyte/pull/47743) | Update dependencies |
| 2.2.24 | 2024-10-28 | [47103](https://github.com/airbytehq/airbyte/pull/47103) | Update dependencies |
| 2.2.23 | 2024-10-12 | [46822](https://github.com/airbytehq/airbyte/pull/46822) | Update dependencies |
| 2.2.22 | 2024-10-05 | [46487](https://github.com/airbytehq/airbyte/pull/46487) | Update dependencies |
| 2.2.21 | 2024-09-28 | [46132](https://github.com/airbytehq/airbyte/pull/46132) | Update dependencies |
| 2.2.20 | 2024-09-21 | [45748](https://github.com/airbytehq/airbyte/pull/45748) | Update dependencies |
| 2.2.19 | 2024-09-14 | [45556](https://github.com/airbytehq/airbyte/pull/45556) | Update dependencies |
| 2.2.18 | 2024-09-07 | [45303](https://github.com/airbytehq/airbyte/pull/45303) | Update dependencies |
| 2.2.17 | 2024-08-31 | [44981](https://github.com/airbytehq/airbyte/pull/44981) | Update dependencies |
| 2.2.16 | 2024-08-24 | [44644](https://github.com/airbytehq/airbyte/pull/44644) | Update dependencies |
| 2.2.15 | 2024-08-17 | [44316](https://github.com/airbytehq/airbyte/pull/44316) | Update dependencies |
| 2.2.14 | 2024-08-12 | [43888](https://github.com/airbytehq/airbyte/pull/43888) | Update dependencies |
| 2.2.13 | 2024-08-10 | [43679](https://github.com/airbytehq/airbyte/pull/43679) | Update dependencies |
| 2.2.12 | 2024-08-03 | [43056](https://github.com/airbytehq/airbyte/pull/43056) | Update dependencies |
| 2.2.11 | 2024-07-27 | [42287](https://github.com/airbytehq/airbyte/pull/42287) | Update dependencies |
| 2.2.10 | 2024-07-13 | [41729](https://github.com/airbytehq/airbyte/pull/41729) | Update dependencies |
| 2.2.9 | 2024-07-10 | [41465](https://github.com/airbytehq/airbyte/pull/41465) | Update dependencies |
| 2.2.8 | 2024-07-09 | [41082](https://github.com/airbytehq/airbyte/pull/41082) | Update dependencies |
| 2.2.7 | 2024-07-06 | [40778](https://github.com/airbytehq/airbyte/pull/40778) | Update dependencies |
| 2.2.6 | 2024-06-25 | [40501](https://github.com/airbytehq/airbyte/pull/40501) | Update dependencies |
| 2.2.5 | 2024-06-22 | [40171](https://github.com/airbytehq/airbyte/pull/40171) | Update dependencies |
| 2.2.4 | 2024-06-04 | [39095](https://github.com/airbytehq/airbyte/pull/39095) | [autopull] Upgrade base image to v1.2.1 |
| 2.2.3 | 2024-05-20 | [38405](https://github.com/airbytehq/airbyte/pull/38405) | [autopull] base image + poetry + up_to_date |
| 2.2.2 | 2024-01-11 | [34153](https://github.com/airbytehq/airbyte/pull/34153) | prepare for airbyte-lib |
| 2.2.1 | 2023-11-06 | [31147](https://github.com/airbytehq/airbyte/pull/31147) | Bugfix: handle records with a null data field |
| 2.2.0 | 2023-10-25 | [31707](https://github.com/airbytehq/airbyte/pull/31707) | Add new stream mail |
| 2.1.0 | 2023-10-10 | [31184](https://github.com/airbytehq/airbyte/pull/31184) | Add new stream goals |
| 2.0.1 | 2023-10-13 | [31151](https://github.com/airbytehq/airbyte/pull/31151) | Add additionalProperties in schemas to read custom fields |
| 2.0.0 | 2023-08-09 | [29293](https://github.com/airbytehq/airbyte/pull/29293) | Migrated to Low-Code CDK |
| 1.0.0 | 2023-06-29 | [27832](https://github.com/airbytehq/airbyte/pull/27832) | Remove `followers_count` field from `Products` stream |
| 0.1.19 | 2023-07-05 | [27967](https://github.com/airbytehq/airbyte/pull/27967) | Update `OrganizationFields` and `ProductFields` with `display_field` field |
| 0.1.18 | 2023-06-02 | [26892](https://github.com/airbytehq/airbyte/pull/26892) | Update `DialFields` schema with `pipeline_ids` property |
| 0.1.17 | 2023-03-21 | [24282](https://github.com/airbytehq/airbyte/pull/24282) | Bugfix handle missed `cursor_field` |
| 0.1.16 | 2023-03-08 | [23789](https://github.com/airbytehq/airbyte/pull/23789) | Add 11 new streams |
| 0.1.15 | 2023-03-02 | [23705](https://github.com/airbytehq/airbyte/pull/23705) | Disable OAuth |
| 0.1.14 | 2023-03-01 | [23539](https://github.com/airbytehq/airbyte/pull/23539) | Fix schema for "activities", "check" works if empty "deals" |
| 0.1.13 | 2022-09-16 | [16799](https://github.com/airbytehq/airbyte/pull/16799) | Migrate to per-stream state |
| 0.1.12 | 2022-05-23 | [13082](https://github.com/airbytehq/airbyte/pull/13082) | Remove date-time format from schemas |
| 0.1.11 | 2022-05-16 | [12867](https://github.com/airbytehq/airbyte/pull/12867) | Add unit tests |
| 0.1.10 | 2022-04-26 | [11870](https://github.com/airbytehq/airbyte/pull/11870) | Add 3 streams: DealFields, OrganizationFields and PersonFields |
| 0.1.9 | 2021-12-07 | [8582](https://github.com/airbytehq/airbyte/pull/8582) | Update connector fields title/description |
| 0.1.8 | 2021-11-16 | [7875](https://github.com/airbytehq/airbyte/pull/7875) | Extend schema for "persons" stream |
| 0.1.7 | 2021-11-15 | [7968](https://github.com/airbytehq/airbyte/pull/7968) | Update oAuth flow config |
| 0.1.6 | 2021-10-05 | [6821](https://github.com/airbytehq/airbyte/pull/6821) | Add OAuth support |
| 0.1.5 | 2021-09-27 | [6441](https://github.com/airbytehq/airbyte/pull/6441) | Fix normalization error |
| 0.1.4 | 2021-08-26 | [5943](https://github.com/airbytehq/airbyte/pull/5943) | Add organizations stream |
| 0.1.3 | 2021-08-26 | [5642](https://github.com/airbytehq/airbyte/pull/5642) | Remove date-time from deals stream |
| 0.1.2 | 2021-07-23 | [4912](https://github.com/airbytehq/airbyte/pull/4912) | Update money type to support floating point |
| 0.1.1 | 2021-07-19 | [4686](https://github.com/airbytehq/airbyte/pull/4686) | Update spec.json |
| 0.1.0 | 2021-07-19 | [4686](https://github.com/airbytehq/airbyte/pull/4686) | 🎉 New source: Pipedrive connector |
