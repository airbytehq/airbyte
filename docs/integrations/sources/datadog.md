# Datadog

This page contains the setup guide and reference information for the Datadog source connector, which reads data from the [Datadog API](https://docs.datadoghq.com/api/latest/).

## Prerequisites

- A Datadog account and the [Datadog site](https://docs.datadoghq.com/getting_started/site/) your organization uses, for example `datadoghq.com` (US1) or `datadoghq.eu` (EU1).
- A Datadog [API key](https://docs.datadoghq.com/account_management/api-app-keys/#api-keys).
- A Datadog [application key](https://docs.datadoghq.com/account_management/api-app-keys/#application-keys) with read access to the data you want to sync. See [Application key permissions](#application-key-permissions).

Datadog doesn't offer OAuth to standalone clients, so this connector authenticates with an API key and an application key only.

## Setup guide

### Step 1: Create the API key and application key in Datadog

1. In Datadog, go to [**Organization Settings** > **API Keys**](https://app.datadoghq.com/organization-settings/api-keys) and copy an existing API key or create a new one.
2. Go to [**Organization Settings** > **Application Keys**](https://app.datadoghq.com/organization-settings/application-keys) and click **New Key**.
3. Optionally, limit the key's scopes to the permissions listed in [Application key permissions](#application-key-permissions) for the streams you plan to sync.
4. Copy the application key and store it securely. If your organization uses One-Time Read mode, Datadog shows the key only once.

An application key without scopes has the same permissions as the user who created it. To avoid losing access when that user leaves your organization, consider creating the key for a [service account](https://docs.datadoghq.com/account_management/org_settings/service_accounts/).

### Step 2: Set up the Datadog connector in Airbyte

1. In Airbyte, go to **Sources** and click **New source**.
2. Search for and select **Datadog**.
3. Enter a name for the source.
4. For **API Key**, enter your Datadog API key.
5. For **Application Key**, enter your Datadog application key.
6. For **Site**, select the Datadog site your organization uses. The default is `datadoghq.com`. Both keys must belong to an organization on this site.
7. (Optional) For **Query**, enter a [log search query](https://docs.datadoghq.com/logs/explorer/search_syntax/) to filter the `logs` stream. Leave it empty to read all logs. This field doesn't apply to `audit_logs`.
8. (Optional) For **Start date**, enter the UTC date and time to start reading `logs` and `audit_logs` from, in the format `YYYY-MM-DDTHH:MM:SSZ`. The default is `2023-12-01T00:00:00Z`. If you clear this field, the connector starts 30 days before the sync.
9. (Optional) For **End date**, enter the UTC date and time to stop reading `logs` and `audit_logs`, in the same format. Leave it empty to read up to the time of the sync.
10. (Optional) For **Max records per requests**, enter the page size of the `logs` stream, from 1 to 5000. The default is 5000.
11. (Optional) For **Number of concurrent workers**, enter how many streams and partitions the connector reads at the same time, from 2 to 10. The default is 3. Lower it if syncs hit Datadog rate limits.
12. Click **Set up source**.

The **Start date** and **End date** apply to `logs` and `audit_logs` in both full refresh and incremental syncs. Other streams always read all records, because their Datadog endpoints don't accept a time filter.

The **Queries** field is not read by any stream and has no effect on syncs.

## Supported sync modes

The Datadog source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Namespaces | No |

Only the `logs` and `audit_logs` streams support incremental sync. They use the record timestamp, copied into the `sync_date` field, as the cursor. Each incremental sync starts one day before the saved cursor to pick up logs that arrive late, so expect some records to be read again. Use a deduplicated sync mode if you need each record once.

## Supported streams

| Stream | Datadog endpoint | Sync modes | Application key permission |
| :--- | :--- | :--- | :--- |
| `audit_logs` | [Get a list of Audit Logs events](https://docs.datadoghq.com/api/latest/audit/#get-a-list-of-audit-logs-events) | Full refresh, incremental | `audit_logs_read` |
| `dashboards` | [Get all dashboards](https://docs.datadoghq.com/api/latest/dashboards/#get-all-dashboards) | Full refresh | `dashboards_read` |
| `downtimes` | [Get all downtimes](https://docs.datadoghq.com/api/latest/downtimes/#get-all-downtimes) (v1) | Full refresh | `monitors_read` |
| `incident_teams` | `GET /api/v2/teams` | Full refresh | None declared |
| `incidents` | [Get a list of incidents](https://docs.datadoghq.com/api/latest/incidents/#get-a-list-of-incidents) | Full refresh | `incident_read` |
| `logs` | [Search logs (GET)](https://docs.datadoghq.com/api/latest/logs/#search-logs-get) | Full refresh, incremental | `logs_read_data` |
| `metrics` | [Metrics](https://docs.datadoghq.com/api/latest/metrics/) (`GET /api/v2/metrics`) | Full refresh | `metrics_read` |
| `monitors` | [Get all monitor details](https://docs.datadoghq.com/api/latest/monitors/#get-all-monitor-details) | Full refresh | `monitors_read` |
| `service_level_objectives` | [Get all SLOs](https://docs.datadoghq.com/api/latest/service-level-objectives/#get-all-slos) | Full refresh | `slos_read` |
| `synthetic_tests` | [Get the list of all Synthetic tests](https://docs.datadoghq.com/api/latest/synthetics/#get-the-list-of-all-synthetic-tests) | Full refresh | `synthetics_read` |
| `users` | [List all users](https://docs.datadoghq.com/api/latest/users/#list-all-users) | Full refresh | `user_access_read` |

### Stream notes

- `dashboards` and `service_level_objectives` include deleted records. The connector reads each list twice, once for active records and once for deleted records, and sets a boolean `deleted` field on every record. Datadog itself doesn't return this field.
- `metrics` lists the metrics that actively reported in the last 60 days, the longest window Datadog allows.
- `downtimes` uses the deprecated v1 endpoint, which doesn't return downtimes created with the v2 Downtimes API.
- `incident_teams` calls `GET /api/v2/teams`, which Datadog has removed from its API. The stream fails on every sync. Don't select it.

### Application key permissions

If your application key is scoped, it needs the permission listed in the [Supported streams](#supported-streams) table for each stream you sync. The connection check reads only `dashboards`, so a key without `dashboards_read` fails the check. A key that passes the check can still fail on another stream if it lacks that stream's permission.

## Limitations and troubleshooting

### Rate limits

Datadog sets [rate limits](https://docs.datadoghq.com/api/latest/rate-limits/) per endpoint and reports them in response headers. The connector tracks the `X-RateLimit-Remaining` header, and when Datadog returns a `429` response, it waits for the time given in `X-RateLimit-Reset` and retries up to five times. All workers share the same limits, so if syncs are slow or fail because of rate limits, lower **Number of concurrent workers**. You can also ask Datadog support to raise your organization's limits.

### Common errors

| Error message | Cause | Fix |
| :--- | :--- | :--- |
| The Application Key lacks the `<permission>` permission | The application key is scoped and doesn't include the permission the stream needs. | Add the named permission to the application key, or deselect the stream. |
| Datadog rejected the API Key or the Application Key | A key is incomplete, invalid, or revoked, or the keys belong to an organization on a different site than the one selected in **Site**. | Check both keys and the **Site** setting. |
| Datadog rejected the log search query | The **Query** value isn't valid Datadog log search syntax. | Correct the **Query** field. |
| Synthetic Monitoring is not active for this Datadog account | The account doesn't have Synthetic Monitoring. | Deselect the `synthetic_tests` stream, or activate Synthetic Monitoring in Datadog. |
| The page cursor of the Datadog metrics list is expired | The `metrics` page cursor expired during a long read, and the sync failed. | Run the sync again. The next sync reads the list from the first page. |

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :-------- | :----------- | :--------------------------------------------------------- | :----------------------------------------------------------------------------- |
| 2.1.1 | 2026-11-17 | [78670](https://github.com/airbytehq/airbyte/pull/78670) | Update dependencies |
| 2.1.0 | 2026-11-16 | [92985](https://github.com/airbytehq/airbyte/pull/92985) | The `logs` cursor now advances between syncs; `audit_logs` is incremental and now follows `start_date` and `end_date`; every list stream is paged at the vendor's page size, and `max_records_per_request` now sets the page size of `logs`; `metrics` covers the last 60 days; `dashboards` and `service_level_objectives` include deleted records, with a `deleted` flag; errors on keys, permissions and the log query say what to fix; new `num_workers` option |
| 2.0.25 | 2026-11-10 | [91324](https://github.com/airbytehq/airbyte/pull/91324) | Upgrade base image to `source-declarative-manifest:7.47.0` |
| 2.0.24 | 2025-05-24 | [60420](https://github.com/airbytehq/airbyte/pull/60420) | Update dependencies |
| 2.0.23 | 2025-05-10 | [59399](https://github.com/airbytehq/airbyte/pull/59399) | Update dependencies |
| 2.0.22 | 2025-04-26 | [58888](https://github.com/airbytehq/airbyte/pull/58888) | Update dependencies |
| 2.0.21 | 2025-04-19 | [58342](https://github.com/airbytehq/airbyte/pull/58342) | Update dependencies |
| 2.0.20 | 2025-04-12 | [57776](https://github.com/airbytehq/airbyte/pull/57776) | Update dependencies |
| 2.0.19 | 2025-04-05 | [57246](https://github.com/airbytehq/airbyte/pull/57246) | Update dependencies |
| 2.0.18 | 2025-03-29 | [56528](https://github.com/airbytehq/airbyte/pull/56528) | Update dependencies |
| 2.0.17 | 2025-03-25 | [54206](https://github.com/airbytehq/airbyte/pull/54206) | remove default end date value |
| 2.0.16 | 2025-03-22 | [55994](https://github.com/airbytehq/airbyte/pull/55994) | Update dependencies |
| 2.0.15 | 2025-03-08 | [55280](https://github.com/airbytehq/airbyte/pull/55280) | Update dependencies |
| 2.0.14 | 2025-03-01 | [54921](https://github.com/airbytehq/airbyte/pull/54921) | Update dependencies |
| 2.0.13 | 2025-02-22 | [54444](https://github.com/airbytehq/airbyte/pull/54444) | Update dependencies |
| 2.0.12 | 2025-02-20 | [54180](https://github.com/airbytehq/airbyte/pull/54180) | 🐛 Source Datadog : Fix the Pagination in the logs stream |
| 2.0.11 | 2025-02-15 | [53705](https://github.com/airbytehq/airbyte/pull/53705) | Update dependencies |
| 2.0.10 | 2025-02-08 | [53382](https://github.com/airbytehq/airbyte/pull/53382) | Update dependencies |
| 2.0.9 | 2025-02-01 | [52866](https://github.com/airbytehq/airbyte/pull/52866) | Update dependencies |
| 2.0.8 | 2025-01-25 | [52350](https://github.com/airbytehq/airbyte/pull/52350) | Update dependencies |
| 2.0.7 | 2025-01-18 | [51677](https://github.com/airbytehq/airbyte/pull/51677) | Update dependencies |
| 2.0.6 | 2025-01-16 | [48537](https://github.com/airbytehq/airbyte/pull/48537) | Update default start and end dates for logs stream, if they are not configured as default |
| 2.0.5 | 2025-01-11 | [51122](https://github.com/airbytehq/airbyte/pull/51122) | Update dependencies |
| 2.0.4 | 2024-12-28 | [50567](https://github.com/airbytehq/airbyte/pull/50567) | Update dependencies |
| 2.0.3 | 2024-12-21 | [49988](https://github.com/airbytehq/airbyte/pull/49988) | Update dependencies |
| 2.0.2 | 2024-12-14 | [49472](https://github.com/airbytehq/airbyte/pull/49472) | Update dependencies |
| 2.0.1 | 2024-12-12 | [48300](https://github.com/airbytehq/airbyte/pull/48300) | Update dependencies |
| 2.0.0 | 2024-12-12 | [48833](https://github.com/airbytehq/airbyte/pull/48833) | Remove `is_read_only` parameter from dashboards stream schema |
| 1.1.1 | 2024-10-28 | [46502](https://github.com/airbytehq/airbyte/pull/46502) | Update dependencies |
| 1.1.0 | 2024-10-05 | [46387](https://github.com/airbytehq/airbyte/pull/46387) | Migrate to manifest only |
| 1.0.6 | 2024-09-28 | [46190](https://github.com/airbytehq/airbyte/pull/46190) | Update dependencies |
| 1.0.5 | 2024-09-21 | [45771](https://github.com/airbytehq/airbyte/pull/45771) | Update dependencies |
| 1.0.4 | 2024-09-14 | [45581](https://github.com/airbytehq/airbyte/pull/45581) | Update dependencies |
| 1.0.3 | 2024-09-07 | [45297](https://github.com/airbytehq/airbyte/pull/45297) | Update dependencies |
| 1.0.2 | 2024-08-31 | [44992](https://github.com/airbytehq/airbyte/pull/44992) | Update dependencies |
| 1.0.1 | 2024-08-24 | [44706](https://github.com/airbytehq/airbyte/pull/44706) | Update dependencies |
| 1.0.0 | 2024-08-20 | [44371](https://github.com/airbytehq/airbyte/pull/44371) | Update CDK version and dependencies, remove parameters and migrate to inline schemas |
| 0.4.15 | 2024-08-17 | [44313](https://github.com/airbytehq/airbyte/pull/44313) | Update dependencies |
| 0.4.14 | 2024-08-12 | [43741](https://github.com/airbytehq/airbyte/pull/43741) | Update dependencies |
| 0.4.13 | 2024-08-10 | [43555](https://github.com/airbytehq/airbyte/pull/43555) | Update dependencies |
| 0.4.12 | 2024-08-03 | [43141](https://github.com/airbytehq/airbyte/pull/43141) | Update dependencies |
| 0.4.11 | 2024-07-27 | [42776](https://github.com/airbytehq/airbyte/pull/42776) | Update dependencies |
| 0.4.10 | 2024-07-20 | [42341](https://github.com/airbytehq/airbyte/pull/42341) | Update dependencies |
| 0.4.9 | 2024-07-13 | [41783](https://github.com/airbytehq/airbyte/pull/41783) | Update dependencies |
| 0.4.8 | 2024-07-10 | [41416](https://github.com/airbytehq/airbyte/pull/41416) | Update dependencies |
| 0.4.7 | 2024-07-09 | [41168](https://github.com/airbytehq/airbyte/pull/41168) | Update dependencies |
| 0.4.6 | 2024-07-06 | [40985](https://github.com/airbytehq/airbyte/pull/40985) | Update dependencies |
| 0.4.5 | 2024-06-25 | [40306](https://github.com/airbytehq/airbyte/pull/40306) | Update dependencies |
| 0.4.4 | 2024-06-22 | [40063](https://github.com/airbytehq/airbyte/pull/40063) | Update dependencies |
| 0.4.3 | 2024-06-12 | [37590](https://github.com/airbytehq/airbyte/pull/37590) | Change `last_records` to `last_record` |
| 0.4.2 | 2024-06-04 | [39060](https://github.com/airbytehq/airbyte/pull/39060) | [autopull] Upgrade base image to v1.2.1 |
| 0.4.1 | 2024-05-20 | [38424](https://github.com/airbytehq/airbyte/pull/38424) | [autopull] base image + poetry + up_to_date |
| 0.4.0 | 2023-12-04 | [30999](https://github.com/airbytehq/airbyte/pull/30999) | Add `monitors` and `service_level_objectives` Streams |
| 0.3.0 | 2023-08-29 | [29885](https://github.com/airbytehq/airbyte/pull/29885) | Migrate to low code |
| 0.2.2 | 2023-07-14 | [28089](https://github.com/airbytehq/airbyte/pull/28089) | Additional stream and query details in response |
| 0.2.1 | 2023-06-28 | [26534](https://github.com/airbytehq/airbyte/pull/26534) | Support multiple query streams and pulling data from different datadog sites |
| 0.2.0 | 2023-06-28 | [27784](https://github.com/airbytehq/airbyte/pull/27784) | Add necessary fields to schemas |
| 0.1.1 | 2023-04-27 | [25562](https://github.com/airbytehq/airbyte/pull/25562) | Update testing dependencies |
| 0.1.0 | 2022-11-03 | [18150](https://github.com/airbytehq/airbyte/pull/18150) | New Source: Datadog |

</details>
