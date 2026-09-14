# App Store Connect

This page contains the setup guide and reference information for the App Store Connect source connector.

The connector reads sales and finance reports, App Store Analytics reports, customer reviews, and app metadata from the [App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi).

## Prerequisites

- An App Store Connect account with the Account Holder having accepted the current Paid Apps agreement. The API returns `403 FORBIDDEN.REQUIRED_AGREEMENTS_MISSING_OR_EXPIRED` for report endpoints when the agreement has lapsed.
- A team API key with at least the **Sales and Reports** role. See [Creating API Keys for App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi/creating-api-keys-for-app-store-connect-api).
- Your vendor number, shown in App Store Connect under **Payments and Financial Reports**.
- For the App Store Analytics streams, an existing `ONGOING` and/or `ONE_TIME_SNAPSHOT` analytics report request for each app. The connector reads existing requests; it does not create them. See [Downloading Analytics Reports](https://developer.apple.com/documentation/appstoreconnectapi/downloading-analytics-reports).

## Setup guide

### Step 1: Create an API key in App Store Connect

1. In App Store Connect, go to **Users and Access** and then **Integrations**, then **App Store Connect API**.
2. Under **Team Keys**, click **Generate API Key**. Give it a name and the **Sales and Reports** role (or higher).
3. Download the `.p8` private key. Apple lets you download it once; keep it somewhere safe.
4. Note the **Issuer ID** at the top of the page and the **Key ID** for the key you created.

### Step 2: Set up the source connector in Airbyte

1. In Airbyte, click **Sources** and then **+ New source**.
2. Select **App Store Connect** from the **Source type** dropdown and enter a name for the source.
3. For **JWT Payload ISS**, enter the Issuer ID.
4. For **JWT Header KID**, enter the Key ID.
5. For **JWT Secret Key**, paste the full contents of the `.p8` file, including the `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----` lines.
6. For **vendorID**, enter your vendor number.
7. For **Analytics reports start date**, enter the earliest processing date (`YYYY-MM-DD`) to sync for the ongoing App Store Analytics streams. Apple does not backfill ongoing reports before the date the report request was created.
8. (Optional) Set **Reviews start date**, **Sales reports start date**, **Subscription event reports start date**, and **Finance reports start date** to control how far back the corresponding streams sync. When unset, the sales and finance streams default to Apple's retention window (365 days for daily sales reports, about 11 months for finance reports).
9. (Optional) For **Subscription event skip dates**, list any report dates Apple returns as an undecodable archive. The connector skips those days instead of failing the sync.
10. Click **Set up source**.

## Supported sync modes

The App Store Connect source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/):

- [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped)

## Supported streams

### Apps and reviews

- [`list_id_apps`](https://developer.apple.com/documentation/appstoreconnectapi/get-v1-apps) — apps in the team. Parent stream for every per-app stream.
- [`customer_reviews_per_app`](https://developer.apple.com/documentation/appstoreconnectapi/get-v1-apps-_id_-customerreviews) — customer reviews for each app, incremental on `createdDate`.

### Sales and Trends reports

Daily gzip-compressed TSV reports from [`GET /v1/salesReports`](https://developer.apple.com/documentation/appstoreconnectapi/get-v1-salesreports). Each stream is incremental with a one-day step and adds `report_date` and `_sync_cursor` fields to every row.

- `sales_report` — `SALES` / `SUMMARY`, report version `1_1`.
- `subscription_report` — `SUBSCRIPTION` / `SUMMARY`, report version `1_3`.
- `subscriber_report` — `SUBSCRIBER` / `DETAILED`, report version `1_3`.
- `subscription_event_report` — `SUBSCRIPTION_EVENT` / `SUMMARY`, report version `1_3`.

### Finance reports

- [`finance_report`](https://developer.apple.com/documentation/appstoreconnectapi/get-v1-financereports) — monthly `FINANCIAL` report for all regions, incremental with a one-month step.

### App Store Analytics reports

Apple's analytics reports are exposed through a chain of resources: report request, report, instance, segment, and then a signed download URL for each segment. The connector models each link in the chain as its own stream so the download streams can be partitioned correctly. The chain exists twice for each report type: once for `ONGOING` requests and once for `ONE_TIME_SNAPSHOT` (historical) requests.

Report request streams:

- `analytics_report_requests_ongoing` and `analytics_report_requests_historical` — analytics report requests per app.

Chains for the **App Store Installation and Deletion** report:

- `analytics_installations_reports`, `analytics_installations_instances`, `analytics_installations_segments`, `analytics_installations_segment_details`, and `app_store_installations_and_deletions` (the report rows).
- The same five streams with a `_historical` suffix for `ONE_TIME_SNAPSHOT` requests.

Chains for the **App Downloads** report:

- `analytics_app_download_reports`, `analytics_app_download_instances`, `analytics_app_download_segments`, `analytics_app_download_segment_details`, and `app_download` (the report rows).
- The same five streams with a `_historical` suffix for `ONE_TIME_SNAPSHOT` requests.

The report row streams (`app_store_installations_and_deletions`, `app_download`, and their `_historical` variants) use an asynchronous retriever: they poll each segment until Apple returns a download URL, then download and decode the gzip-compressed TSV. Each row is enriched with `app_id`, `report_id`, `instance_id`, `access_type`, and `processing_date`.

## Performance considerations

- The connector retries `429` and `5xx` responses with exponential backoff. Apple's rate limits are documented in [Identifying Rate Limits](https://developer.apple.com/documentation/appstoreconnectapi/identifying-rate-limits).
- Sales and finance reports return `404` or `410` for dates with no data. The connector treats those responses as empty and advances the cursor.
- The analytics download streams process one asynchronous job at a time to stay within Apple's limits on concurrent report downloads.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                 |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------ |
| 0.1.0   | 2026-09-01 | [85279](https://github.com/airbytehq/airbyte/pull/85279) | Add App Store Connect source connector (manifest-only) |

</details>
