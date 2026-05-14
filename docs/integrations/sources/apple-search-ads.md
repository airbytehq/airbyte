# Apple Ads (Apple Search Ads)

This page contains the setup guide and reference information for the Apple Ads source connector.

## Prerequisites

- An Apple Ads account with an administrator who can invite users with API permissions.
- Your Apple Ads organization id (`orgId`), shown in the Apple Ads UI. Each Airbyte source syncs data for a single `orgId`.
- An OAuth client id and client secret generated for an API user (see Step 1 below).

## Setup guide

### Step 1: Create an API user and OAuth credentials in Apple Ads

The connector authenticates to the Apple Ads Campaign Management API using OAuth 2 client credentials. An account administrator creates an API user, generates a key pair, and produces a client id and client secret. Apple's full guide is at [Implementing OAuth for the Apple Ads API](https://developer.apple.com/documentation/apple_ads/implementing-oauth-for-the-apple-search-ads-api). The high-level steps are:

1. From Apple Ads, sign in as an account administrator and go to **Account Settings** → **User Management**.
2. Click **Invite Users** and assign the user an **API user role**.
3. Generate a private and public key pair, upload the public key for the API user, and create a client secret.
4. Note the resulting **Client ID** and **Client Secret**. You'll enter them into Airbyte in Step 2.

### Step 2: Set up the source connector in Airbyte

1. In Airbyte, click **Sources** and then click **+ New source**.
2. Select **Apple Ads** from the **Source type** dropdown and enter a name for the source.
3. For **Org Id**, enter the `orgId` of your Apple Ads organization (found in the Apple Ads UI).
4. Enter the **Client ID** and **Client Secret** from [Step 1](#step-1-create-an-api-user-and-oauth-credentials-in-apple-ads).
5. For **Start Date** and **End Date**, enter dates in `YYYY-MM-DD` format. If **End Date** is blank, Airbyte syncs up to today. Apple's reporting API limits how far back daily data is available; requests for dates outside the supported window return no data.
6. For **Time Zone**, select either `UTC` (Coordinated Universal Time) or `ORTZ` (Organization Time Zone). The default is `UTC`.
7. For **Lookback Window**, enter a value between 1 and 30. Apple Ads applies a 30-day attribution window, so the default of 30 ensures late-attributed conversions are captured on each incremental sync. Lower values shorten incremental syncs but may miss late attributions.
8. For **Exponential Backoff Factor**, enter a value between 1 and 20. This controls how aggressively the connector backs off when Apple's API returns rate-limit (`429`) or server (`500`) errors. The default is 5; increase it for very large accounts that frequently hit rate limits.
9. (Optional) For **Number of Workers**, enter a value between 1 and 20 (default `2`). This controls how many partitions (campaigns or ad groups) the connector fetches in parallel. Increase it for accounts with many campaigns or ad groups to shorten sync time, at the cost of higher API request volume.
10. (Optional) For **Token Refresh Endpoint**, override the default Apple OAuth token endpoint. Use this only if you proxy outbound requests; most users should leave it at the default.
11. Click **Set up source**.

## Supported sync modes

The Apple Ads source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/):

- [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped)

## Supported streams

The Apple Ads source connector exposes the following streams. For full schema and field details, see the [Apple Ads API reference](https://developer.apple.com/documentation/apple_ads).

### Object streams

- [`campaigns`](https://developer.apple.com/documentation/apple_ads/get-all-campaigns) — all campaigns in the organization.
- [`adgroups`](https://developer.apple.com/documentation/apple_ads/get-all-ad-groups) — ad groups across all campaigns.
- [`keywords`](https://developer.apple.com/documentation/apple_ads/get-all-targeting-keywords-in-an-ad-group) — targeting keywords across all ad groups.
- [`ads`](https://developer.apple.com/documentation/apple_ads/get-all-ads) — ads across all ad groups.

### Daily report streams

The connector requests daily reports from Apple's Reports API, grouped by `countryOrRegion`. Apple [supports](https://developer.apple.com/documentation/apple_ads/reportingrequest) hourly, daily, weekly, and monthly granularity, but this connector only requests daily.

- [`campaigns_report_daily`](https://developer.apple.com/documentation/apple_ads/get-campaign-level-reports) — campaign-level daily metrics.
- [`adgroups_report_daily`](https://developer.apple.com/documentation/apple_ads/get-ad-group-level-reports) — ad-group-level daily metrics.
- [`keywords_report_daily`](https://developer.apple.com/documentation/apple_ads/get-keyword-level-reports) — keyword-level daily metrics.
- [`ads_report_daily`](https://developer.apple.com/documentation/apple_ads/get-ad-level-reports) — ad-level daily metrics.

:::note
Report streams use `date` as the cursor field and default to `(date, campaignId)` as the primary key. Because each row is also broken out by `countryOrRegion`, the connector exposes a separate `countryorregion` field. If your account targets multiple countries or regions, add `countryorregion` to the primary key in the connection's stream settings to deduplicate correctly.
:::

## Performance considerations

- Apple's API returns `401 Unauthorized` when an access token is invalid or expired. The connector automatically refreshes expired access tokens and retries the failed request.
- Apple's API enforces rate limits and recommends exponential retry. The connector automatically retries `429` rate-limit responses and `500` server errors; tune the **Exponential Backoff Factor** to control how aggressively it backs off.
- For accounts with many campaigns or ad groups, increase **Number of Workers** to fetch partitions in parallel and reduce sync time.
- Apple Ads applies a 30-day attribution window. Reducing **Lookback Window** below 30 days shortens incremental syncs but may miss late conversions.

## Reference

This connector uses the [Apple Ads Campaign Management API v5](https://developer.apple.com/documentation/apple_ads). Airbyte calls `https://api.searchads.apple.com/api/v5` and sends the selected Apple Ads organization in the `X-AP-Context` header as `orgId={orgId}`.

For programmatic configuration, use these parameter names:

| Field | Required | Description |
| ----- | :------: | ----------- |
| `org_id` | Yes | Apple Ads organization ID to sync. |
| `client_id` | Yes | OAuth client ID for the Apple Ads API user. |
| `client_secret` | Yes | OAuth client secret for the Apple Ads API user. |
| `start_date` | Yes | Earliest report date to sync, in `YYYY-MM-DD` format. |
| `end_date` | No | Latest report date to sync, in `YYYY-MM-DD` format. If omitted, Airbyte syncs through the current date. |
| `timezone` | Yes | Reporting time zone. Valid values are `UTC` and `ORTZ`. |
| `lookback_window` | No | Number of days to sync again on incremental report streams. Valid values are `1` through `30`. Defaults to `30`. |
| `backoff_factor` | No | Exponential retry delay factor for Apple Ads API errors that Airbyte can retry. Valid values are `1` through `20`. Defaults to `5`. |
| `token_refresh_endpoint` | Yes | OAuth token endpoint. Defaults to Apple's token endpoint with the `client_credentials` grant and `searchadsorg` scope. |
| `num_workers` | No | Number of concurrent workers for partitioned streams. Valid values are `1` through `20`. Defaults to `2`. |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--- | :----------- | :------ |
| 1.1.4 | 2026-05-12 | [78029](https://github.com/airbytehq/airbyte/pull/78029) | Refresh expired OAuth access tokens before retrying failed Apple Ads API requests |
| 1.1.3 | 2026-05-05 | [76973](https://github.com/airbytehq/airbyte/pull/76973) | Fix `ads_report_daily` broken incremental sync, remove incorrect keyword error predicate, and enable concurrent partition processing to reduce heartbeat timeouts |
| 1.1.2 | 2026-04-28 | [77141](https://github.com/airbytehq/airbyte/pull/77141) | Update dependencies |
| 1.1.1 | 2026-04-21 | [76507](https://github.com/airbytehq/airbyte/pull/76507) | Update dependencies |
| 1.1.0 | 2026-04-01 | [69218](https://github.com/airbytehq/airbyte/pull/69218) | Add two new streams - `ads` & `ads_report_daily` |
| 1.0.11 | 2026-03-31 | [75879](https://github.com/airbytehq/airbyte/pull/75879) | Update dependencies |
| 1.0.10 | 2026-03-24 | [75015](https://github.com/airbytehq/airbyte/pull/75015) | Update dependencies |
| 1.0.9 | 2026-03-10 | [74512](https://github.com/airbytehq/airbyte/pull/74512) | Update dependencies |
| 1.0.8 | 2026-03-03 | [74180](https://github.com/airbytehq/airbyte/pull/74180) | Update dependencies |
| 1.0.7 | 2026-02-03 | [72690](https://github.com/airbytehq/airbyte/pull/72690) | Update dependencies |
| 1.0.6 | 2026-01-20 | [71888](https://github.com/airbytehq/airbyte/pull/71888) | Update dependencies |
| 1.0.5 | 2026-01-14 | [71435](https://github.com/airbytehq/airbyte/pull/71435) | Update dependencies |
| 1.0.4 | 2025-12-18 | [70810](https://github.com/airbytehq/airbyte/pull/70810) | Update dependencies |
| 1.0.3 | 2025-11-25 | [69891](https://github.com/airbytehq/airbyte/pull/69891) | Update dependencies |
| 1.0.2 | 2025-11-18 | [69577](https://github.com/airbytehq/airbyte/pull/69577) | Update dependencies |
| 1.0.1 | 2025-10-29 | [68392](https://github.com/airbytehq/airbyte/pull/68392) | Update dependencies |
| 1.0.0 | 2025-10-21 | [66557](https://github.com/airbytehq/airbyte/pull/66557) | Update `adgroups_report_daily` and `keywords_report_daily` to use global state cursor |
| 0.8.10 | 2025-10-14 | [67979](https://github.com/airbytehq/airbyte/pull/67979) | Update dependencies |
| 0.8.9 | 2025-10-07 | [67173](https://github.com/airbytehq/airbyte/pull/67173) | Update dependencies |
| 0.8.8 | 2025-09-30 | [66272](https://github.com/airbytehq/airbyte/pull/66272) | Update dependencies |
| 0.8.7 | 2025-09-15 | [66197](https://github.com/airbytehq/airbyte/pull/66197) | Update to CDK v7 |
| 0.8.6 | 2025-08-23 | [65312](https://github.com/airbytehq/airbyte/pull/65312) | Update dependencies |
| 0.8.5 | 2025-08-09 | [64663](https://github.com/airbytehq/airbyte/pull/64663) | Update dependencies |
| 0.8.4 | 2025-07-19 | [63453](https://github.com/airbytehq/airbyte/pull/63453) | Update dependencies |
| 0.8.3 | 2025-07-12 | [63087](https://github.com/airbytehq/airbyte/pull/63087) | Update dependencies |
| 0.8.2 | 2025-06-15 | [61626](https://github.com/airbytehq/airbyte/pull/61626) | Update dependencies |
| 0.8.1 | 2025-05-17 | [60627](https://github.com/airbytehq/airbyte/pull/60627) | Update dependencies |
| 0.8.0 | 2025-05-13 | [60241](https://github.com/airbytehq/airbyte/pull/60241) | Add token refresh endpoint override configuration override |
| 0.7.9 | 2025-05-10 | [59888](https://github.com/airbytehq/airbyte/pull/59888) | Update dependencies |
| 0.7.8 | 2025-05-03 | [59308](https://github.com/airbytehq/airbyte/pull/59308) | Update dependencies |
| 0.7.7 | 2025-04-26 | [58712](https://github.com/airbytehq/airbyte/pull/58712) | Update dependencies |
| 0.7.6 | 2025-04-19 | [58275](https://github.com/airbytehq/airbyte/pull/58275) | Update dependencies |
| 0.7.5 | 2025-04-12 | [57658](https://github.com/airbytehq/airbyte/pull/57658) | Update dependencies |
| 0.7.4 | 2025-04-05 | [57158](https://github.com/airbytehq/airbyte/pull/57158) | Update dependencies |
| 0.7.3 | 2025-03-29 | [56573](https://github.com/airbytehq/airbyte/pull/56573) | Update dependencies |
| 0.7.2 | 2025-03-25 | [56383](https://github.com/airbytehq/airbyte/pull/56383) | add countryorregion to report schemas |
| 0.7.1 | 2025-03-22 | [56109](https://github.com/airbytehq/airbyte/pull/56109) | Update dependencies |
| 0.7.0 | 2025-03-20 | [55839](https://github.com/airbytehq/airbyte/pull/55839) | countryOrRegion metadata info included |
| 0.6.0 | 2025-03-20 | [55785](https://github.com/airbytehq/airbyte/pull/55785) | Add timezone config parameter |
| 0.5.1 | 2025-03-08 | [55366](https://github.com/airbytehq/airbyte/pull/55366) | Update dependencies |
| 0.5.0 | 2025-03-05 | [55210](https://github.com/airbytehq/airbyte/pull/55210) | Remove primary keys |
| 0.4.3 | 2025-03-01 | [54873](https://github.com/airbytehq/airbyte/pull/54873) | Update dependencies |
| 0.4.2 | 2025-02-24 | [54646](https://github.com/airbytehq/airbyte/pull/54646) | Fix paginator settings for incremental report streams |
| 0.4.1 | 2025-02-22 | [54284](https://github.com/airbytehq/airbyte/pull/54284) | Update dependencies |
| 0.4.0 | 2025-02-20 | [54170](https://github.com/airbytehq/airbyte/pull/54170) | Externalize backoff factor and lookback window configurations |
| 0.3.3 | 2025-02-15 | [53920](https://github.com/airbytehq/airbyte/pull/53920) | Update dependencies |
| 0.3.2 | 2025-02-14 | [53685](https://github.com/airbytehq/airbyte/pull/53685) | Fix granularity to daily |
| 0.3.1 | 2025-02-08 | [53422](https://github.com/airbytehq/airbyte/pull/53422) | Update dependencies |
| 0.3.0 | 2025-02-03 | [53136](https://github.com/airbytehq/airbyte/pull/53136) | Update API version to V5 |
| 0.2.9 | 2025-02-01 | [52899](https://github.com/airbytehq/airbyte/pull/52899) | Update dependencies |
| 0.2.8 | 2025-01-25 | [52197](https://github.com/airbytehq/airbyte/pull/52197) | Update dependencies |
| 0.2.7 | 2025-01-18 | [51745](https://github.com/airbytehq/airbyte/pull/51745) | Update dependencies |
| 0.2.6 | 2025-01-11 | [51249](https://github.com/airbytehq/airbyte/pull/51249) | Update dependencies |
| 0.2.5 | 2024-12-28 | [50469](https://github.com/airbytehq/airbyte/pull/50469) | Update dependencies |
| 0.2.4 | 2024-12-21 | [50155](https://github.com/airbytehq/airbyte/pull/50155) | Update dependencies |
| 0.2.3 | 2024-12-14 | [49561](https://github.com/airbytehq/airbyte/pull/49561) | Update dependencies |
| 0.2.2 | 2024-12-12 | [47751](https://github.com/airbytehq/airbyte/pull/47751) | Update dependencies |
| 0.2.1 | 2024-11-08 | [48440](https://github.com/airbytehq/airbyte/pull/48440) | Set authentication grant_type to client_credentials |
| 0.2.0 | 2024-10-01 | [46288](https://github.com/airbytehq/airbyte/pull/46288) | Migrate to Manifest-only |
| 0.1.20 | 2024-09-28 | [46153](https://github.com/airbytehq/airbyte/pull/46153) | Update dependencies |
| 0.1.19 | 2024-09-21 | [45803](https://github.com/airbytehq/airbyte/pull/45803) | Update dependencies |
| 0.1.18 | 2024-09-14 | [45474](https://github.com/airbytehq/airbyte/pull/45474) | Update dependencies |
| 0.1.17 | 2024-09-07 | [45326](https://github.com/airbytehq/airbyte/pull/45326) | Update dependencies |
| 0.1.16 | 2024-08-31 | [45013](https://github.com/airbytehq/airbyte/pull/45013) | Update dependencies |
| 0.1.15 | 2024-08-24 | [44654](https://github.com/airbytehq/airbyte/pull/44654) | Update dependencies |
| 0.1.14 | 2024-08-17 | [44322](https://github.com/airbytehq/airbyte/pull/44322) | Update dependencies |
| 0.1.13 | 2024-08-12 | [43912](https://github.com/airbytehq/airbyte/pull/43912) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43514](https://github.com/airbytehq/airbyte/pull/43514) | Update dependencies |
| 0.1.11 | 2024-08-03 | [43195](https://github.com/airbytehq/airbyte/pull/43195) | Update dependencies |
| 0.1.10 | 2024-07-27 | [42660](https://github.com/airbytehq/airbyte/pull/42660) | Update dependencies |
| 0.1.9 | 2024-07-20 | [42225](https://github.com/airbytehq/airbyte/pull/42225) | Update dependencies |
| 0.1.8 | 2024-07-13 | [41722](https://github.com/airbytehq/airbyte/pull/41722) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41546](https://github.com/airbytehq/airbyte/pull/41546) | Update dependencies |
| 0.1.6 | 2024-07-09 | [40832](https://github.com/airbytehq/airbyte/pull/40832) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40364](https://github.com/airbytehq/airbyte/pull/40364) | Update dependencies |
| 0.1.4 | 2024-06-22 | [40186](https://github.com/airbytehq/airbyte/pull/40186) | Update dependencies |
| 0.1.3 | 2024-06-04 | [38967](https://github.com/airbytehq/airbyte/pull/38967) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.2 | 2024-05-21 | [38502](https://github.com/airbytehq/airbyte/pull/38502) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2023-07-11 | [28153](https://github.com/airbytehq/airbyte/pull/28153) | Fix manifest duplicate key (no change in behavior for the syncs) |
| 0.1.0 | 2022-11-17 | [19557](https://github.com/airbytehq/airbyte/pull/19557) | Initial release with campaigns, adgroups & keywords streams (base and daily reports) |

</details>
