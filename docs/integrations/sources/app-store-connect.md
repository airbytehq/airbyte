# App Store Connect

The App Store Connect source replicates app metadata, customer reviews, Sales
and Trends reports, finance reports, and App Store Analytics reports from the
[App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi).

## Prerequisites

- An App Store Connect **team** API key. Apple's individual API keys can't
  access Sales and Trends or finance reports, so the connector doesn't support
  them.
- The key's issuer ID, key ID, and downloaded `.p8` private key.
- Your vendor number, which the Sales and Trends and finance report endpoints
  require.
- A role on the API key that covers every report family you plan to sync (see
  [Choose a role for the API key](#choose-a-role-for-the-api-key)).
- For the analytics streams, an existing analytics report request for each app
  whose analytics data you want to sync. The connector reads existing `ONGOING`
  and `ONE_TIME_SNAPSHOT` requests but doesn't create them.

## Setup guide

### Create a team API key

You need the Admin role in App Store Connect to generate team keys.

1. In [App Store Connect](https://appstoreconnect.apple.com/), go to
   **Users and Access** > **Integrations** > **App Store Connect API**.
2. On the **Team Keys** tab, click **Generate API Key** (or **+**).
3. Enter a name, choose a role under **Access**, and click **Generate**.
4. Copy the **Issuer ID** shown at the top of the page and the **Key ID** for
   the new key.
5. Click **Download API Key** and save the `.p8` file. Apple only lets you
   download the private key once and doesn't keep a copy.

When you configure the connector, paste the complete contents of the `.p8`
file, including the `-----BEGIN PRIVATE KEY-----` and
`-----END PRIVATE KEY-----` lines, into **JWT Secret Key**.

For Apple's own instructions, see
[Creating API Keys for App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi/creating-api-keys-for-app-store-connect-api).

### Choose a role for the API key

The key's role determines which streams return data. Streams the key can't
access sync as empty rather than failing.

- **Sales and Reports**: Apple's recommended role for third-party reporting
  tools. It can read Sales and Trends reports and analytics reports, but not
  finance reports, so `finance_report` is empty with this role.
- **Finance**: Can read analytics reports and finance reports.
- **Admin**: Can read everything and is the only role that can create
  analytics report requests.

See
[Downloading Analytics Reports](https://developer.apple.com/documentation/appstoreconnectapi/downloading-analytics-reports#Understand-roles-and-reports)
for Apple's role table.

### Find your vendor number

In App Store Connect, open **Payments and Financial Reports** and copy the
vendor number shown there. Enter it in the **vendorID** field.

### Create analytics report requests

The analytics streams only return data for apps that already have an analytics
report request. Apple's API is the only way to create these requests, and the
`POST /v1/analyticsReportRequests` endpoint requires the Admin role. Create an
`ONGOING` request for each app you want to sync daily, and optionally a
`ONE_TIME_SNAPSHOT` request for historical data. See
[Request reports](https://developer.apple.com/documentation/appstoreconnectapi/downloading-analytics-reports#Request-analytics-reports).

Apple takes one to two days to produce the first reports after you create a
request, and doesn't backfill `ONGOING` reports from before the request's
creation date. Set **Analytics reports start date** to the date you created
the request, or later.

If nobody downloads reports for a request for an extended period, Apple changes
the request's status to `stoppedDueToInactivity` and stops generating reports.
Create a new request to resume.

## Configuration

| Input | Required | Description |
| --- | --- | --- |
| `iss` | Yes | Issuer ID for the App Store Connect team API key. |
| `kid` | Yes | Key ID for the App Store Connect API key. |
| `secret_key` | Yes | Complete `.p8` private key. The connector uses it to sign ES256 JWTs. |
| `vendorID` | Yes | Your vendor number from **Payments and Financial Reports**. |
| `analytics_reports_start_date` | Yes | Earliest processing date to read for the ongoing analytics streams, in `YYYY-MM-DD` format. Use the `ONGOING` request creation date or later. |
| `reviews_start_date` | No | Earliest customer review creation time to read, in UTC `YYYY-MM-DDTHH:MM:SSZ` format. Defaults to `2020-01-01T00:00:00Z`. |
| `sales_reports_start_date` | No | Earliest daily report date for `sales_report`, `subscriber_report`, and `subscription_report`, in `YYYY-MM-DD` format. Defaults to 365 days before the sync. Dates older than 365 days are moved forward to Apple's retention limit. |
| `subscription_event_reports_start_date` | No | Earliest daily report date for `subscription_event_report`, in `YYYY-MM-DD` format. Independent of `sales_reports_start_date`. Defaults to 365 days before the sync. |
| `subscription_event_skip_dates` | No | Report dates (`YYYY-MM-DD`) to skip for `subscription_event_report`. Use this when Apple returns an archive for a specific day that can't be decoded. The connector advances past skipped dates without emitting rows. |
| `finance_reports_start_date` | No | Earliest finance report month, in `YYYY-MM` format. Defaults to 11 months before the current month. Months older than that are moved forward to Apple's retention limit. |

## Streams

### Apps and reviews

| Stream | Sync mode | Description |
| --- | --- | --- |
| `list_id_apps` | Full refresh | Apps visible to the API key. Parent stream for every other stream that's scoped to an app. |
| `customer_reviews_per_app` | Incremental | Customer reviews for each app, flattened to include `rating`, `title`, `body`, `reviewerNickname`, `territory`, `createdDate`, and `app_id`. Cursor: `createdDate`. Each sync re-reads the last seven days to pick up late-arriving reviews. |

### Sales and Trends reports

Each stream downloads one daily gzip TSV report from the `salesReports`
endpoint per report date and emits one record per row. The connector adds a
`report_date` field with the report's date and a `_sync_cursor` field it uses
for incremental state.

| Stream | Sync mode | Apple report | Description |
| --- | --- | --- | --- |
| `sales_report` | Incremental | `SALES`, `SUMMARY`, version `1_1` | Daily sales summary. The most recent report date requested is two days before the sync. |
| `subscriber_report` | Incremental | `SUBSCRIBER`, `DETAILED`, version `1_3` | Daily subscriber detail. The most recent report date requested is two days before the sync. |
| `subscription_report` | Incremental | `SUBSCRIPTION`, `SUMMARY`, version `1_3` | Daily subscription summary. The most recent report date requested is two days before the sync. |
| `subscription_event_report` | Incremental | `SUBSCRIPTION_EVENT`, `SUMMARY`, version `1_3` | Daily subscription event summary. The most recent report date requested is three days before the sync, because Apple finalizes event data later than other reports. |

### Finance reports

| Stream | Sync mode | Description |
| --- | --- | --- |
| `finance_report` | Incremental | Monthly `FINANCIAL` report for region `ZZ` (all regions, consolidated). Syncs through the month that ended at least 35 days ago, which is when Apple has typically published it. Requires the Finance or Admin role. |

### App Store Analytics reports

Apple produces analytics data through a hierarchy: report request > report >
instance > segment > downloaded file. The connector exposes each level so you
can audit what Apple generated. The streams ending in `_historical` read
`ONE_TIME_SNAPSHOT` requests; the others read `ONGOING` requests.

The connector reads two Apple reports: **App Store Installation and Deletion
Standard** and **App Downloads Standard**, both at `DAILY` granularity. Other
analytics reports aren't supported.

| Stream | Sync mode | Description |
| --- | --- | --- |
| `analytics_report_requests_ongoing` | Full refresh | `ONGOING` report requests for each app. |
| `analytics_installations_reports` | Full refresh | The Installation and Deletion report for each ongoing request. |
| `analytics_installations_instances` | Incremental | Daily instances of the Installation and Deletion report. Cursor: `processing_date`. |
| `analytics_installations_segments` | Incremental | Segments for each instance. Cursor: `processing_date`. |
| `analytics_installations_segment_details` | Full refresh | Metadata for each segment, including the pre-signed `download_url`. |
| `app_store_installations_and_deletions` | Incremental | Rows from the downloaded Installation and Deletion report files. Cursor: `processing_date`. |
| `analytics_app_download_reports` | Full refresh | The App Downloads report for each ongoing request. |
| `analytics_app_download_instances` | Incremental | Daily instances of the App Downloads report. Cursor: `processing_date`. |
| `analytics_app_download_segments` | Incremental | Segments for each instance. Cursor: `processing_date`. |
| `analytics_app_download_segment_details` | Full refresh | Metadata for each segment, including the pre-signed `download_url`. |
| `app_download` | Incremental | Rows from the downloaded App Downloads report files. Cursor: `processing_date`. |
| `analytics_report_requests_historical` | Full refresh | `ONE_TIME_SNAPSHOT` report requests for each app. |
| `analytics_installations_reports_historical` | Full refresh | The Installation and Deletion report for each snapshot request. |
| `analytics_installations_instances_historical` | Full refresh | Instances of the historical Installation and Deletion report. |
| `analytics_installations_segments_historical` | Full refresh | Segments of the historical Installation and Deletion report. |
| `analytics_installations_segment_details_historical` | Full refresh | Segment metadata for the historical Installation and Deletion report. |
| `app_store_installations_and_deletions_historical` | Full refresh | Rows from the downloaded historical Installation and Deletion report files. |
| `analytics_app_download_reports_historical` | Full refresh | The App Downloads report for each snapshot request. |
| `analytics_app_download_instances_historical` | Full refresh | Instances of the historical App Downloads report. |
| `analytics_app_download_segments_historical` | Full refresh | Segments of the historical App Downloads report. |
| `analytics_app_download_segment_details_historical` | Full refresh | Segment metadata for the historical App Downloads report. |
| `app_download_historical` | Full refresh | Rows from the downloaded historical App Downloads report files. |

Incremental analytics streams read every processing date from
`analytics_reports_start_date` (or the saved cursor) up to two days before the
sync. The
`app_download` and `app_store_installations_and_deletions` streams download
each segment's gzip TSV file from Apple's short-lived pre-signed Amazon S3 URL
and emit one record per row.

## Limitations and data availability

- Sales and Trends reports are only available for Apple's rolling 365-day
  retention window. The connector never requests dates older than that, even
  if you set an earlier start date.
- Finance reports are limited to roughly the most recent 11 months and end at
  the latest complete fiscal month.
- `ONGOING` analytics requests don't backfill data from before their creation
  date. Use a `ONE_TIME_SNAPSHOT` request and the `_historical` streams for
  earlier data.
- A report stream is empty, rather than failing, when the API key's role can't
  access that report, the app doesn't produce that report type, or Apple hasn't
  published the requested period yet. The Sales and Trends and finance streams
  treat `400`, `404`, and `410` responses as "no data"; the analytics streams
  also treat `403` that way.
- The connector runs analytics download jobs one at a time.

### Rate limits

Apple limits each API key to a per-hour request budget and reports it in the
`X-Rate-Limit` response header. See
[Identifying Rate Limits](https://developer.apple.com/documentation/appstoreconnectapi/identifying-rate-limits).
The connector retries `429` and transient `5xx` responses up to three times
with exponential backoff.

### Authentication

The connector signs a new ES256 JWT for each App Store Connect request, with a
15-minute lifetime and the `appstoreconnect-v1` audience. Analytics report
downloads go to Apple's pre-signed S3 URLs and don't include the JWT.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| --- | --- | --- | --- |
| 0.0.2 | 2026-09-22 | [86549](https://github.com/airbytehq/airbyte/pull/86549) | Update dependencies |
| 0.0.1 | 2026-09-16 | [85821](https://github.com/airbytehq/airbyte/pull/85821) | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
