# Instatus

This page contains the setup guide and reference information for the [Instatus](https://instatus.com/) source connector. The connector uses the [Instatus REST API](https://instatus.com/help/api) to sync data about your status pages, including components, incidents, maintenances, subscribers, and metrics.

## Prerequisites

- An Instatus account that owns or has access to the status pages you want to sync.
- An Instatus API key.

## Setup guide

### Step 1: Get your Instatus API key

1. Sign in to your [Instatus dashboard](https://dashboard.instatus.com/).
2. Go to **User settings** > **Developer settings**, or open the [Developer settings](https://dashboard.instatus.com/developer) page directly.
3. Copy your API key.

The connector discovers all status pages that the API key can access, so you don't need to provide page IDs. If the Instatus API returns a `401 Unauthorized` error for a page, the connector skips that page's data instead of failing the sync. To make sure the connector syncs everything, use an API key that belongs to an owner of the status pages you want to sync.

### Step 2: Set up the Instatus connector in Airbyte

1. In Airbyte, go to **Sources** and select **Instatus**.
2. Enter a name for the source.
3. In **Rest API Key**, paste the API key from Step 1.
4. Click **Set up source**.

## Supported sync modes

The Instatus source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

The connector doesn't support incremental syncs.

## Supported streams

| Stream | Instatus API reference | Description |
| :----- | :--------------------- | :---------- |
| `status_pages` | [Status pages](https://instatus.com/help/api/status-pages) | Status pages that the API key can access. Other streams use this stream to discover page IDs. |
| `page_components` | [Components](https://instatus.com/help/api/components) | Components for each status page. |
| `incidents` | [Incidents](https://instatus.com/help/api/incidents) | Incidents for each status page. |
| `incident_updates` | [Incident updates](https://instatus.com/help/api/incident-updates) | Individual updates for each incident. The connector requests each update separately. |
| `maintenances` | [Maintenances](https://instatus.com/help/api/maintenances) | Scheduled maintenances for each status page. |
| `maintenance_updates` | [Maintenance updates](https://instatus.com/help/api/maintenance-updates) | Individual updates for each maintenance. The connector requests each update separately. |
| `templates` | [Templates](https://instatus.com/help/api/templates) | Templates for each status page. |
| `team` | [Teammates](https://instatus.com/help/api/teammates) | Team members for each status page. |
| `subscribers` | [Subscribers](https://instatus.com/help/api/subscribers) | Subscribers for each status page. |
| `metrics` | [Metrics](https://instatus.com/help/api/metrics) | Metrics for each status page. |
| `user` | [User profile](https://instatus.com/help/api/user-profile) | Profile of the user who owns the API key. |
| `public_data` | [Public data](https://instatus.com/help/api/public-data) | Public summary for each status page, read from `https://<subdomain>.instatus.com/summary.json`. |

## Limitations

- **Pagination:** The connector doesn't paginate. Each request returns only the first page of results, and the Instatus API returns 50 records per page by default. As a result, the connector syncs at most 50 status pages, and at most 50 records per status page for the `page_components`, `incidents`, `maintenances`, `templates`, `team`, `subscribers`, and `metrics` streams. The `incident_updates` and `maintenance_updates` streams only include updates for the incidents and maintenances in those first 50 records.
- **Rate limits:** If the Instatus API returns a `429 Too Many Requests` response, the connector waits for the duration in the `Retry-After` header and retries the request.

## Data type mapping

| Integration Type    | Airbyte Type | Notes |
| :------------------ | :----------- | :---- |
| `string`            | `string`     |       |
| `integer`, `number` | `number`     |       |
| `array`             | `array`      |       |
| `object`            | `object`     |       |

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                 |
| :------ | :--------- | :------------------------------------------------------- | :---------------------- |
| 0.2.16 | 2026-10-16 | [88959](https://github.com/airbytehq/airbyte/pull/88959) | Update to source-declarative-manifest 7.37.0 and CDK v7 for unit tests |
| 0.2.15 | 2025-05-24 | [60617](https://github.com/airbytehq/airbyte/pull/60617) | Update dependencies |
| 0.2.14 | 2025-05-10 | [59859](https://github.com/airbytehq/airbyte/pull/59859) | Update dependencies |
| 0.2.13 | 2025-05-03 | [59233](https://github.com/airbytehq/airbyte/pull/59233) | Update dependencies |
| 0.2.12 | 2025-04-26 | [58793](https://github.com/airbytehq/airbyte/pull/58793) | Update dependencies |
| 0.2.11 | 2025-04-19 | [57738](https://github.com/airbytehq/airbyte/pull/57738) | Update dependencies |
| 0.2.10 | 2025-04-05 | [57106](https://github.com/airbytehq/airbyte/pull/57106) | Update dependencies |
| 0.2.9 | 2025-03-29 | [56683](https://github.com/airbytehq/airbyte/pull/56683) | Update dependencies |
| 0.2.8 | 2025-03-22 | [56069](https://github.com/airbytehq/airbyte/pull/56069) | Update dependencies |
| 0.2.7 | 2025-03-08 | [55495](https://github.com/airbytehq/airbyte/pull/55495) | Update dependencies |
| 0.2.6 | 2025-03-01 | [54745](https://github.com/airbytehq/airbyte/pull/54745) | Update dependencies |
| 0.2.5 | 2025-02-22 | [54309](https://github.com/airbytehq/airbyte/pull/54309) | Update dependencies |
| 0.2.4 | 2025-02-15 | [53804](https://github.com/airbytehq/airbyte/pull/53804) | Update dependencies |
| 0.2.3 | 2025-02-08 | [53295](https://github.com/airbytehq/airbyte/pull/53295) | Update dependencies |
| 0.2.2 | 2025-02-01 | [52783](https://github.com/airbytehq/airbyte/pull/52783) | Update dependencies |
| 0.2.1 | 2025-01-25 | [52230](https://github.com/airbytehq/airbyte/pull/52230) | Update dependencies |
| 0.2.0 | 2025-01-14 | [47242](https://github.com/airbytehq/airbyte/pull/47242) | Migrate to manifest-only format |
| 0.1.29 | 2025-01-11 | [51197](https://github.com/airbytehq/airbyte/pull/51197) | Update dependencies |
| 0.1.28 | 2025-01-04 | [50887](https://github.com/airbytehq/airbyte/pull/50887) | Update dependencies |
| 0.1.27 | 2024-12-28 | [50609](https://github.com/airbytehq/airbyte/pull/50609) | Update dependencies |
| 0.1.26 | 2024-12-21 | [50076](https://github.com/airbytehq/airbyte/pull/50076) | Update dependencies |
| 0.1.25 | 2024-12-14 | [49268](https://github.com/airbytehq/airbyte/pull/49268) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.1.24 | 2024-12-12 | [49147](https://github.com/airbytehq/airbyte/pull/49147) | Update dependencies |
| 0.1.23 | 2024-10-28 | [47027](https://github.com/airbytehq/airbyte/pull/47027) | Update dependencies |
| 0.1.22 | 2024-10-12 | [46843](https://github.com/airbytehq/airbyte/pull/46843) | Update dependencies |
| 0.1.21 | 2024-10-05 | [46484](https://github.com/airbytehq/airbyte/pull/46484) | Update dependencies |
| 0.1.20 | 2024-09-28 | [46115](https://github.com/airbytehq/airbyte/pull/46115) | Update dependencies |
| 0.1.19 | 2024-09-21 | [45731](https://github.com/airbytehq/airbyte/pull/45731) | Update dependencies |
| 0.1.18 | 2024-09-14 | [45514](https://github.com/airbytehq/airbyte/pull/45514) | Update dependencies |
| 0.1.17 | 2024-09-07 | [45275](https://github.com/airbytehq/airbyte/pull/45275) | Update dependencies |
| 0.1.16 | 2024-08-31 | [44990](https://github.com/airbytehq/airbyte/pull/44990) | Update dependencies |
| 0.1.15 | 2024-08-24 | [44634](https://github.com/airbytehq/airbyte/pull/44634) | Update dependencies |
| 0.1.14 | 2024-08-17 | [44241](https://github.com/airbytehq/airbyte/pull/44241) | Update dependencies |
| 0.1.13 | 2024-08-12 | [43747](https://github.com/airbytehq/airbyte/pull/43747) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43495](https://github.com/airbytehq/airbyte/pull/43495) | Update dependencies |
| 0.1.11 | 2024-08-03 | [43135](https://github.com/airbytehq/airbyte/pull/43135) | Update dependencies |
| 0.1.10 | 2024-07-27 | [42724](https://github.com/airbytehq/airbyte/pull/42724) | Update dependencies |
| 0.1.9 | 2024-07-20 | [42208](https://github.com/airbytehq/airbyte/pull/42208) | Update dependencies |
| 0.1.8 | 2024-07-13 | [41779](https://github.com/airbytehq/airbyte/pull/41779) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41549](https://github.com/airbytehq/airbyte/pull/41549) | Update dependencies |
| 0.1.6 | 2024-07-09 | [41115](https://github.com/airbytehq/airbyte/pull/41115) | Update dependencies |
| 0.1.5 | 2024-07-06 | [40872](https://github.com/airbytehq/airbyte/pull/40872) | Update dependencies |
| 0.1.4 | 2024-06-25 | [40425](https://github.com/airbytehq/airbyte/pull/40425) | Update dependencies |
| 0.1.3 | 2024-06-22 | [40179](https://github.com/airbytehq/airbyte/pull/40179) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39167](https://github.com/airbytehq/airbyte/pull/39167) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-21 | [38506](https://github.com/airbytehq/airbyte/pull/38506) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2023-04-01 | [21008](https://github.com/airbytehq/airbyte/pull/21008) | Initial (alpha) release |

</details>
