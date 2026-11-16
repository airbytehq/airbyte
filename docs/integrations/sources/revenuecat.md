# RevenueCat

This connector syncs data from the [RevenueCat REST API v2](https://www.revenuecat.com/docs/api-v2), including projects, apps, customers and their subscriptions, purchases, entitlements, invoices, and product catalog configuration.

## Prerequisites

- A RevenueCat account with access to the projects you want to sync.
- A RevenueCat V2 secret API key. The connector doesn't support V1 keys.

## Create a V2 secret API key

1. In the RevenueCat dashboard, open your project and go to **Project settings** > **API keys**.
2. Click **+ New**.
3. Enter a name and select **V2** as the API version.
4. Grant read access for the following permissions:
   - `project_configuration:projects:read`
   - `project_configuration:apps:read`
   - `project_configuration:entitlements:read`
   - `project_configuration:offerings:read`
   - `project_configuration:products:read`
   - `charts_metrics:overview:read`
   - `customer_information:customers:read`
   - `customer_information:subscriptions:read`
   - `customer_information:purchases:read`
   - `customer_information:invoices:read`
5. Click **Generate** and copy the key.

For more information, see [RevenueCat authentication](https://www.revenuecat.com/docs/projects/authentication).

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your RevenueCat V2 secret API key. |  |
| `start_date` | `string` | Start date. The earliest record date to sync, in the format `YYYY-MM-DDTHH:MM:SSZ`, for example `2024-01-01T00:00:00Z`. Records with a cursor value before this date aren't synced. |  |

## Supported sync modes

The connector supports the following sync modes:

- Full Refresh - Overwrite
- Full Refresh - Append
- Incremental - Append
- Incremental - Append + Deduped

## Streams

The connector reads every project the API key can access. All streams except `projects` are read per project, and the `customers_*` streams are read per customer.

| Stream Name | Primary Key | Cursor Field | Supports Full Sync | Supports Incremental |
|-------------|-------------|--------------|--------------------|----------------------|
| projects | id | created_at | ✅ | ✅ |
| apps | id | created_at | ✅ | ✅ |
| metrics_overview | id | | ✅ | ❌ |
| customers | id | last_seen_at | ✅ | ✅ |
| customers_subscriptions | id | starts_at | ✅ | ✅ |
| customers_purchases | id | purchased_at | ✅ | ✅ |
| customers_active_entitlements | entitlement_id | expires_at | ✅ | ✅ |
| customers_aliases | id | created_at | ✅ | ✅ |
| customers_invoices | id | issued_at | ✅ | ✅ |
| entitlements | id | created_at | ✅ | ✅ |
| entitlements_products | id, entitlement_id | created_at | ✅ | ✅ |
| offerings | id | created_at | ✅ | ✅ |
| offerings_packages | id | created_at | ✅ | ✅ |
| offerings_packages_products | id, package_id | created_at | ✅ | ✅ |
| products | id | created_at | ✅ | ✅ |

## Limitations and troubleshooting

### Incremental syncs read every page

RevenueCat list endpoints don't accept a date filter and don't document a sort order. The connector reads every page on each sync and drops records older than the saved state. An incremental sync makes as many API requests as a full refresh, so it takes about as long.

If you upgraded from a version earlier than 0.2.0, incremental syncs might have skipped records. Existing state is kept on upgrade, so those records aren't backfilled. Refresh your incremental streams to recover them.

### Some cursors don't capture updates

Several cursor fields are set when a record is created and don't change afterward. Incremental syncs on these streams don't pick up later changes to existing records:

- `customers_subscriptions` uses `starts_at`, so status and billing-period changes aren't re-synced.
- `customers_purchases` uses `purchased_at`, so a purchase that's later refunded isn't re-synced.
- `customers_invoices` uses `issued_at`, so a `paid_at` value set after the first sync isn't re-synced.

To capture these changes, use a full refresh sync mode for these streams.

### Primary keys that aren't globally unique

- `customers_active_entitlements` uses `entitlement_id`, which repeats across customers.
- `metrics_overview` uses `id`, such as `active_trials`, which repeats across projects.

If you use **Incremental - Append + Deduped** or sync multiple projects, records from different customers or projects can overwrite each other in the destination.

### `metrics_overview` is a snapshot

The `metrics_overview` stream returns the current value of each overview metric. It doesn't contain historical values.

### Rate limits

RevenueCat applies separate [per-minute rate limits](https://www.revenuecat.com/docs/api-v2#tag/Rate-Limit) to each endpoint domain: 480 requests per minute for customer information endpoints, 60 for project configuration endpoints, and 25 for charts and metrics. When RevenueCat returns a `429` response, the connector waits for the time in the `Retry-After` header before retrying.

The `customers_subscriptions`, `customers_purchases`, `customers_active_entitlements`, `customers_aliases`, and `customers_invoices` streams each send at least one request per customer. For projects with many customers, enabling these streams can make syncs take a long time.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.2.0 | 2026-11-15 | [91549](https://github.com/airbytehq/airbyte/pull/91549) | Fix pagination looping on anonymous customer IDs, read 100 records per page, stop incremental syncs from skipping records on unsorted endpoints, and declare missing and nullable schema fields. Incremental syncs now read every page, so they take about as long as a full refresh. Existing state is kept, so records that earlier versions skipped are not backfilled: refresh your incremental streams to recover them |
| 0.1.55 | 2026-11-10 | [91719](https://github.com/airbytehq/airbyte/pull/91719) | Update dependencies |
| 0.1.54 | 2026-11-03 | [90741](https://github.com/airbytehq/airbyte/pull/90741) | Update dependencies |
| 0.1.53 | 2026-10-20 | [89401](https://github.com/airbytehq/airbyte/pull/89401) | Update dependencies |
| 0.1.52 | 2026-10-13 | [88790](https://github.com/airbytehq/airbyte/pull/88790) | Update dependencies |
| 0.1.51 | 2026-10-06 | [88001](https://github.com/airbytehq/airbyte/pull/88001) | Update dependencies |
| 0.1.50 | 2026-09-29 | [87322](https://github.com/airbytehq/airbyte/pull/87322) | Update dependencies |
| 0.1.49 | 2026-09-22 | [86785](https://github.com/airbytehq/airbyte/pull/86785) | Update dependencies |
| 0.1.48 | 2026-09-15 | [86237](https://github.com/airbytehq/airbyte/pull/86237) | Update dependencies |
| 0.1.47 | 2026-09-08 | [85644](https://github.com/airbytehq/airbyte/pull/85644) | Update dependencies |
| 0.1.46 | 2026-08-18 | [84723](https://github.com/airbytehq/airbyte/pull/84723) | Update dependencies |
| 0.1.45 | 2026-08-11 | [84099](https://github.com/airbytehq/airbyte/pull/84099) | Update dependencies |
| 0.1.44 | 2026-08-04 | [83629](https://github.com/airbytehq/airbyte/pull/83629) | Update dependencies |
| 0.1.43 | 2026-07-28 | [83103](https://github.com/airbytehq/airbyte/pull/83103) | Update dependencies |
| 0.1.42 | 2026-07-21 | [82565](https://github.com/airbytehq/airbyte/pull/82565) | Update dependencies |
| 0.1.41 | 2026-07-14 | [81974](https://github.com/airbytehq/airbyte/pull/81974) | Update dependencies |
| 0.1.40 | 2026-06-30 | [81216](https://github.com/airbytehq/airbyte/pull/81216) | Update dependencies |
| 0.1.39 | 2026-06-23 | [80618](https://github.com/airbytehq/airbyte/pull/80618) | Update dependencies |
| 0.1.38 | 2026-06-16 | [80019](https://github.com/airbytehq/airbyte/pull/80019) | Update dependencies |
| 0.1.37 | 2026-06-09 | [79492](https://github.com/airbytehq/airbyte/pull/79492) | Update dependencies |
| 0.1.36 | 2026-06-02 | [78979](https://github.com/airbytehq/airbyte/pull/78979) | Update dependencies |
| 0.1.35 | 2026-04-28 | [77410](https://github.com/airbytehq/airbyte/pull/77410) | Update dependencies |
| 0.1.34 | 2026-04-21 | [76744](https://github.com/airbytehq/airbyte/pull/76744) | Update dependencies |
| 0.1.33 | 2026-03-31 | [75827](https://github.com/airbytehq/airbyte/pull/75827) | Update dependencies |
| 0.1.32 | 2026-03-24 | [75351](https://github.com/airbytehq/airbyte/pull/75351) | Update dependencies |
| 0.1.31 | 2026-03-10 | [74699](https://github.com/airbytehq/airbyte/pull/74699) | Update dependencies |
| 0.1.30 | 2026-02-24 | [73745](https://github.com/airbytehq/airbyte/pull/73745) | Update dependencies |
| 0.1.29 | 2026-02-17 | [73178](https://github.com/airbytehq/airbyte/pull/73178) | Update dependencies |
| 0.1.28 | 2026-01-20 | [72038](https://github.com/airbytehq/airbyte/pull/72038) | Update dependencies |
| 0.1.27 | 2026-01-14 | [71453](https://github.com/airbytehq/airbyte/pull/71453) | Update dependencies |
| 0.1.26 | 2025-12-18 | [70606](https://github.com/airbytehq/airbyte/pull/70606) | Update dependencies |
| 0.1.25 | 2025-11-25 | [70038](https://github.com/airbytehq/airbyte/pull/70038) | Update dependencies |
| 0.1.24 | 2025-11-18 | [69602](https://github.com/airbytehq/airbyte/pull/69602) | Update dependencies |
| 0.1.23 | 2025-10-29 | [68863](https://github.com/airbytehq/airbyte/pull/68863) | Update dependencies |
| 0.1.22 | 2025-10-21 | [68339](https://github.com/airbytehq/airbyte/pull/68339) | Update dependencies |
| 0.1.21 | 2025-10-14 | [67895](https://github.com/airbytehq/airbyte/pull/67895) | Update dependencies |
| 0.1.20 | 2025-10-07 | [67536](https://github.com/airbytehq/airbyte/pull/67536) | Update dependencies |
| 0.1.19 | 2025-09-30 | [66440](https://github.com/airbytehq/airbyte/pull/66440) | Update dependencies |
| 0.1.18 | 2025-09-09 | [65665](https://github.com/airbytehq/airbyte/pull/65665) | Update dependencies |
| 0.1.17 | 2025-08-24 | [65424](https://github.com/airbytehq/airbyte/pull/65424) | Update dependencies |
| 0.1.16 | 2025-08-16 | [65028](https://github.com/airbytehq/airbyte/pull/65028) | Update dependencies |
| 0.1.15 | 2025-08-02 | [64427](https://github.com/airbytehq/airbyte/pull/64427) | Update dependencies |
| 0.1.14 | 2025-07-26 | [64007](https://github.com/airbytehq/airbyte/pull/64007) | Update dependencies |
| 0.1.13 | 2025-07-19 | [63631](https://github.com/airbytehq/airbyte/pull/63631) | Update dependencies |
| 0.1.12 | 2025-07-05 | [62718](https://github.com/airbytehq/airbyte/pull/62718) | Update dependencies |
| 0.1.11 | 2025-06-28 | [62229](https://github.com/airbytehq/airbyte/pull/62229) | Update dependencies |
| 0.1.10 | 2025-06-21 | [61796](https://github.com/airbytehq/airbyte/pull/61796) | Update dependencies |
| 0.1.9 | 2025-05-25 | [60465](https://github.com/airbytehq/airbyte/pull/60465) | Update dependencies |
| 0.1.8 | 2025-05-10 | [60077](https://github.com/airbytehq/airbyte/pull/60077) | Update dependencies |
| 0.1.7 | 2025-05-04 | [59029](https://github.com/airbytehq/airbyte/pull/59029) | Update dependencies |
| 0.1.6 | 2025-04-19 | [58421](https://github.com/airbytehq/airbyte/pull/58421) | Update dependencies |
| 0.1.5 | 2025-04-12 | [57966](https://github.com/airbytehq/airbyte/pull/57966) | Update dependencies |
| 0.1.4 | 2025-04-05 | [57293](https://github.com/airbytehq/airbyte/pull/57293) | Update dependencies |
| 0.1.3 | 2025-03-29 | [56757](https://github.com/airbytehq/airbyte/pull/56757) | Update dependencies |
| 0.1.2 | 2025-03-22 | [56229](https://github.com/airbytehq/airbyte/pull/56229) | Update dependencies |
| 0.1.1 | 2025-03-08 | [55546](https://github.com/airbytehq/airbyte/pull/55546) | Update dependencies |
| 0.1.0 | 2025-03-07 | [55247](https://github.com/airbytehq/airbyte/pull/55247) | Add cursor pagination, add schemas |
| 0.0.5 | 2025-03-01 | [55042](https://github.com/airbytehq/airbyte/pull/55042) | Update dependencies |
| 0.0.4 | 2025-02-23 | [54621](https://github.com/airbytehq/airbyte/pull/54621) | Update dependencies |
| 0.0.3 | 2025-02-15 | [49343](https://github.com/airbytehq/airbyte/pull/49343) | Update dependencies |
| 0.0.2 | 2024-12-11 | [47735](https://github.com/airbytehq/airbyte/pull/47735) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-09-23 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
