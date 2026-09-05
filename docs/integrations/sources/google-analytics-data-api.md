# Google Analytics 4 (GA4)

<HideInUI>

This page contains the setup guide and reference information for the [Google Analytics 4 (GA4)](https://developers.google.com/analytics) source connector.

</HideInUI>

Google Analytics 4 (GA4) is the latest version of Google Analytics, introduced in 2020. It offers a new data model that emphasizes events and user properties, rather than pageviews and sessions. This updated model allows for more flexibility and customization in reporting, and provides more accurate measurement of user behavior across various devices and platforms.

This connector reads report data with the [Google Analytics Data API v1beta](https://developers.google.com/analytics/devguides/reporting/data/v1). It works with Google Analytics 4 (GA4) and [Google Analytics 360](https://support.google.com/analytics/answer/11202874#limits) (GA360) properties. Universal Analytics properties aren't supported, because the Data API can't report on them.

## Prerequisites

- One or more GA4 properties, and the numeric **Property ID** of each one. To find a property ID, see [Google's documentation](https://developers.google.com/analytics/devguides/reporting/data/v1/property-id#what_is_my_property_id).
- An identity with at least the **Viewer** role on every property you want to sync. This is the Google account you authenticate with on Airbyte Cloud, or the service account you create for Airbyte Open Source.
- For Airbyte Open Source: a Google Cloud project with the Google Analytics Data API enabled, and a service account JSON key.

## Setup guide

### Step 1: Set up authentication

<!-- env:cloud -->

#### Airbyte Cloud: authenticate with Google

Airbyte Cloud authenticates through OAuth, so you don't need a Google Cloud project or a service account. Sign in with a Google account that has at least the **Viewer** role on every property you plan to sync. The connector requests the read-only `https://www.googleapis.com/auth/analytics.readonly` scope.

<!-- /env:cloud -->

<!-- env:oss -->

#### Airbyte Open Source: create a service account

1. Sign in to the Google Account you use for Google Analytics as an admin.
2. Go to the [Service Accounts](https://console.developers.google.com/iam-admin/serviceaccounts) page in the Google Cloud console.
3. Select the project you want to use, or create a new one, then click **Continue**.
4. Click **+ Create Service Account** at the top of the page.
5. Enter a name for the service account and, optionally, a description. Click **Create and Continue**.
6. Skip the optional step that grants the service account a role in the project. Access to Analytics data comes from the property access you grant in Google Analytics, not from a project role. Click **Continue**.
7. Select your new service account from the list, then open the **Keys** tab. Click **Add Key** > **Create New Key**.
8. Select **JSON** as the key type. Google generates and downloads the JSON key file you use to authenticate.

#### Enable the Google APIs the connector calls

In the project that owns your service account, enable:

- The [Google Analytics Data API](https://console.developers.google.com/apis/api/analyticsdata.googleapis.com/overview), which serves every report stream. This one is required.
- The [Google Analytics Admin API](https://console.developers.google.com/apis/api/analyticsadmin.googleapis.com/overview), which serves only the `property_metadata` stream. Enable it if you plan to sync that stream.

You don't need the Analytics Reporting API or the Analytics API, which serve Universal Analytics.

#### Grant the service account access to your properties

Creating a service account and downloading its JSON key doesn't give it permission to read Analytics data. Grant that access in Google Analytics for every property you want to sync:

1. In Google Analytics, go to **Admin**, then under **Property**, click **Property access management**.
2. Click **+** > **Add users**, then add the service account email address, which looks like `<name>@<project>.iam.gserviceaccount.com`.
3. Grant at least the **Viewer** role.

<!-- /env:oss -->

### Step 2: Set up the Google Analytics 4 (GA4) source in Airbyte

1. In the Airbyte UI, click **Sources**, then click **+ New source**.
2. Find and select **Google Analytics 4 (GA4)** from the list of available sources, and enter a name for the source.
3. Select an authentication method:

   <!-- env:cloud -->

   - **Authenticate via Google (Oauth)**: click **Authenticate your Google Analytics 4 (GA4) account** and complete the Google sign-in flow in the pop-up window.

   <!-- /env:cloud -->

   <!-- env:oss -->

   - **Service Account Key Authentication**: paste the **Service Account JSON Key** you downloaded in Step 1.

   <!-- /env:oss -->

4. In the **Property IDs** field, add the numeric ID of each property you want to sync, such as `123456789`. Adding more than one property affects stream names, so read [Syncing multiple properties](#syncing-multiple-properties) first.

   :::note
   If the property settings show a tracking ID like `UA-123...-1`, the property is a Universal Analytics property, and this connector can't report on it. To create a GA4 property, follow [Google's instructions](https://support.google.com/analytics/answer/9744165?hl=en).
   :::

5. Set the optional fields you need. See [Configuration options](#configuration-options) for what each one does.
6. Click **Set up source** and wait for the connection test to finish.

## Configuration options

| Field | Default | Description |
| :------ | :-------- | :------------ |
| **Property IDs** (required) | — | The numeric IDs of the GA4 properties to sync. |
| **One Stream per Report** | Off | When on, each report becomes a single stream covering every configured property instead of one stream per report per property. See [One stream per report](#one-stream-per-report). |
| **Start Date** | 730 days before the sync | The earliest date to replicate, in `YYYY-MM-DD` format. Doesn't apply to cohort reports. |
| **End Date** | Today | The latest date to replicate, in `YYYY-MM-DD` format. If you leave it empty, the connector syncs through today. Doesn't apply to cohort reports. |
| **Custom Reports** | — | Extra reports to sync, each with its own dimensions, metrics, and optional filters. See [Custom reports](#custom-reports). |
| **Data Request Interval (Days)** | 1 | The size in days of each date range the connector requests, from 1 to 364. Larger values sync faster but increase the chance of sampling. Doesn't apply to cohort reports. See [Data sampling and data request intervals](#data-sampling-and-data-request-intervals). |
| **Lookback window (Days)** | 2 | How many days before the last synced date each incremental sync re-reads, from 2 to 60. Attribution and Google's processing latency both change recent data after the fact, so a lookback window keeps recent rows accurate. |
| **Keep Empty Rows** | Off | When on, the connector keeps rows whose metrics are all `0`. When off, Google omits them. |
| **Convert `conversions:*` Metrics to Float** | Off | The current version of the connector doesn't use this option. Metric types come from the type the API reports for each metric, so `conversions:*` metrics are already floats when Google returns them as floats. |
| **Subscription Plan/Tier** | Standard Property | The quota tier of your properties. Select **Analytics 360 Property** only if every property ID in the config belongs to an Analytics 360 subscription. See [Performance considerations](#performance-considerations). |

## Supported sync modes

The Google Analytics 4 (GA4) source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

A stream syncs incrementally when its dimensions include `date`, `yearWeek`, `yearMonth`, or `year`, which the connector uses as the cursor field. Every preconfigured stream below is incremental and uses `date` as its cursor, except `weekly_events_report`, which uses `yearWeek`. Custom reports without one of those dimensions, and all cohort reports, are full refresh only.

## Supported streams

Every report stream, preconfigured or custom, is a fixed combination of dimensions and metrics that the connector sends to the Data API [`properties.runReport`](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport) method. Custom reports that include pivots use [`properties.runPivotReport`](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runPivotReport) instead.

Each report record contains the report's dimensions and metrics as top-level fields, plus the `property_id` it came from. Records from non-cohort report streams also include the `startDate` and `endDate` of the date range that produced them.

- Preconfigured streams:
  - daily_active_users
  - devices
  - four_weekly_active_users
  - locations
  - pages
  - traffic_sources
  - website_overview
  - weekly_active_users
  - user_acquisition_first_user_medium_report
  - user_acquisition_first_user_source_report
  - user_acquisition_first_user_source_medium_report
  - user_acquisition_first_user_source_platform_report
  - user_acquisition_first_user_campaign_report
  - user_acquisition_first_user_google_ads_ad_network_type_report
  - user_acquisition_first_user_google_ads_ad_group_name_report
  - traffic_acquisition_session_source_medium_report
  - traffic_acquisition_session_medium_report
  - traffic_acquisition_session_source_report
  - traffic_acquisition_session_campaign_report
  - traffic_acquisition_session_default_channel_grouping_report
  - traffic_acquisition_session_source_platform_report
  - events_report
  - weekly_events_report
  - conversions_report
  - pages_title_and_screen_class_report
  - pages_path_report
  - pages_title_and_screen_name_report
  - content_group_report
  - ecommerce_purchases_item_name_report
  - ecommerce_purchases_item_id_report
  - ecommerce_purchases_item_category_report_combined
  - ecommerce_purchases_item_category_report
  - ecommerce_purchases_item_category_2_report
  - ecommerce_purchases_item_category_3_report
  - ecommerce_purchases_item_category_4_report
  - ecommerce_purchases_item_category_5_report
  - ecommerce_purchases_item_brand_report
  - publisher_ads_ad_unit_report
  - publisher_ads_page_path_report
  - publisher_ads_ad_format_report
  - publisher_ads_ad_source_report
  - demographic_country_report
  - demographic_region_report
  - demographic_city_report
  - demographic_language_report
  - demographic_age_report
  - demographic_gender_report
  - demographic_interest_report
  - tech_browser_report
  - tech_device_category_report
  - tech_device_model_report
  - tech_screen_resolution_report
  - tech_app_version_report
  - tech_platform_report
  - tech_platform_device_category_report
  - tech_operating_system_report
  - tech_os_with_version_report
- Property metadata stream:
  - `property_metadata`
- Custom stream(s)

The `property_metadata` stream is full-refresh and uses the Admin API [`properties.get`](https://developers.google.com/analytics/admin-rest/v1beta/properties/get) method. It emits one record for each configured property ID and includes a `property_id` field for joining with report streams.

The `property_metadata` stream requires the Google Analytics Admin API (`analyticsadmin.googleapis.com`) to be enabled for the GCP project associated with the credentials; service-account users must enable it in their own project. If it is not enabled, this stream fails with a `403 SERVICE_DISABLED` error, while report streams continue to work.

## Connector-specific features

### Syncing multiple properties

One source can sync several properties. The connector queries every stream against every property ID in the config, and names the resulting streams for backward compatibility with connector versions that only supported one property:

- Streams for the first property ID keep their plain name, such as `website_overview`.
- Streams for every additional property ID are suffixed with `Property` and the property ID, such as `website_overviewProperty987654321`.

Because all property IDs share one config, options like **Subscription Plan/Tier** and **Start Date** apply to all of them. If your properties need different settings, or you'd rather keep stream names stable as you add properties, configure one source per property instead.

If this per-property fan-out produces more streams than you want to manage, enable [One stream per report](#one-stream-per-report) instead.

### One stream per report

By default, the connector creates a separate stream for every combination of report and property ID. With 57 preconfigured reports and 70 properties, that's close to 4,000 streams, which makes the catalog slow to load and the stream list hard to work with.

Enabling **One Stream per Report** creates one stream per report instead, covering every configured property. Every record carries the `property_id` it came from, and `property_id` is part of the primary key, so rows from different properties stay distinct in the destination. Each property keeps its own incremental cursor, so properties sync independently.

Consolidated streams are named `<report_name>Consolidated`, so the `devices` report becomes `devicesConsolidated`. The per-property streams, such as `devices` and `devicesProperty987654321`, aren't created while this setting is on. The different name is deliberate: it means a consolidated stream starts from an empty destination table and empty state rather than inheriting them from the single-property stream it replaces.

A consolidated stream's schema is the union of the field definitions the API reports for each configured property. This matters for custom metrics, which GA4 defines per property: a custom metric that exists on only some of your properties is still in the schema, so its data isn't dropped. If the same field is typed differently across properties, the connector uses the type from the property listed first in **Property IDs**.

Syncs make the same number of API requests either way. This setting reduces catalog size and the number of destination tables, not sync duration.

:::caution
Turning this setting on or off changes stream names, so data lands in new destination tables and incremental state starts over. Don't toggle it casually on an established connection.

**Changing it on an existing connection requires a schema refresh.** The stream list in a connection is a snapshot of the last schema discovery, so the per-property streams keep appearing, and keep syncing nothing, until you refresh it. Work in this order:

1. Enable the setting on the source and save.
2. Run **Refresh source schema** on each connection that uses this source. The per-property streams are reported as removed, and the `<report_name>Consolidated` streams appear.
3. Enable the consolidated streams you want and apply the changes.
4. Run a sync. The consolidated streams are new, so this is a full backfill covering every property.
5. After you confirm the backfill, you can drop the old per-property tables in your destination. Airbyte leaves them in place. Keep them if there's any chance you'll revert.

Between steps 1 and 3, the connection still lists stream names that no longer exist in the source, and syncs return no records for them.

**Reverting loses no data.** Disable the setting and refresh the schema again, and the per-property streams come back under their original names. Each one resumes from the cursor it held before you enabled the setting, so the period the setting was on is re-fetched on the next sync.

The exception is step 5. Dropping a destination table doesn't reset the stream's cursor, so per-property streams whose tables you deleted resume from their old cursor and their recreated tables are missing everything before it. Clear those streams when you revert to backfill them in full.
:::

:::caution
**Adding a property ID while this setting is on.** A new property becomes a new partition of the existing consolidated streams, and a new partition starts from the stream's current cursor rather than from your **Start Date**. The new property's historical data isn't backfilled, and no error is raised. Clear the affected streams after adding the property ID to backfill it.

This doesn't apply when the setting is off, where a new property ID produces new streams that backfill on their own.
:::

### Custom reports

Custom reports let you sync dimension and metric combinations that the preconfigured streams don't cover. Each entry in the **Custom Reports** field defines one stream:

- **Name**: the stream name.
- **Dimensions**: the dimensions to group by, such as `city` or `date`. Include `date`, `yearWeek`, `yearMonth`, or `year` if you want the stream to sync incrementally.
- **Metrics**: the metrics to report, such as `sessions` or `screenPageViews`.
- **Dimensions filter**: (Optional) a [FilterExpression](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/FilterExpression) that restricts which dimension values the API returns. Build it from an `andGroup`, `orGroup`, `notExpression`, or a single `filter`.
- **Cohort Reports**: (Optional) cohort analysis settings. See [Cohort reports](#cohort-reports).

A custom report can also include a `pivots` array, following the API's [Pivot](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/Pivot) definition. The Airbyte UI doesn't expose this field, so you can only set it by editing the source configuration directly, such as through the API or Terraform provider. A report with pivots uses `properties.runPivotReport` and isn't paginated.

For the dimensions and metrics the API supports, see the [API schema](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema). To check that a combination is valid for your property, use the [GA4 Dimensions & Metrics Explorer](https://ga-dev-tools.google/ga4/dimensions-metrics-explorer/). Invalid combinations make the sync fail with the API's error message, because the Data API rejects them with an HTTP 400 response.

The following custom report tracks sessions and bounce rate by city, and syncs incrementally because it includes the `date` dimension:

```json
[
  {
    "name": "User Engagement Report",
    "dimensions": ["date", "city"],
    "metrics": ["sessions", "bounceRate"]
  }
]
```

This one adds a dimension filter that keeps only sessions from mobile devices:

```json
[
  {
    "name": "Mobile User Engagement Report",
    "dimensions": ["date", "city"],
    "metrics": ["sessions", "bounceRate"],
    "dimensionFilter": {
      "filter_type": "filter",
      "field_name": "deviceCategory",
      "filter": {
        "filter_name": "stringFilter",
        "value": "mobile",
        "matchType": ["EXACT"]
      }
    }
  }
]
```

### Cohort reports

A cohort report tracks a group of users who share a first-session date over time. To sync one, set **Cohort Reports** to **Enabled** in a custom report and describe the cohorts you want. Cohorts require the `firstSessionDate` dimension and an explicit date range.

Cohort reports ignore the **Start Date**, **End Date**, and **Data Request Interval (Days)** options, because their date range comes from the cohort definition. They're always full refresh, and their records don't include `startDate` or `endDate` fields.

```json
[
  {
    "name": "Weekly Retention Report",
    "dimensions": ["cohort", "cohortNthWeek"],
    "metrics": ["cohortActiveUsers"],
    "cohortSpec": {
      "enabled": "true",
      "cohorts": [
        {
          "name": "Last 7 Days",
          "dimension": "firstSessionDate",
          "dateRange": {
            "startDate": "2026-07-01",
            "endDate": "2026-07-07"
          }
        }
      ],
      "cohortsRange": {
        "granularity": "WEEKLY",
        "startOffset": 0,
        "endOffset": 4
      },
      "cohortReportSettings": {
        "accumulate": true
      }
    }
  }
]
```

For the full set of cohort options, see [CohortSpec](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/CohortSpec) in Google's documentation.

### Data sampling and data request intervals

Google Analytics applies [data sampling](https://support.google.com/analytics/answer/13331292) when a request covers more data than its compute thresholds allow, which means the response contains estimates instead of exact numbers. Smaller date ranges make sampling less likely.

The **Data Request Interval (Days)** option controls how much data each request covers. The default of 1 day minimizes sampling. Raising it up to 364 days reduces the number of requests and speeds up syncs, at the cost of accuracy. Cohort reports ignore this option.

:::caution
Dimensions such as `month` and `yearMonth` group data within each requested date range, not across ranges. With a short interval, a report that groups by month emits one row per interval per month, which looks like duplicated data. If your report uses those dimensions, set **Data Request Interval (Days)** to 364 so each request covers a full period.
:::

## Performance considerations

The Data API enforces [quotas](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas) per property. Core quotas are much larger for Analytics 360 properties than for standard ones, including concurrent requests and hourly and daily token budgets. The connector uses the **Subscription Plan/Tier** option to pick which request rate it applies locally, so setting it to **Analytics 360 Property** when your properties are standard makes the connector send requests faster than the API allows, which produces quota errors.

Requests that hit a quota or another retryable error are retried up to 10 times, 30 seconds apart. HTTP 400 responses and responses whose API status is `PERMISSION_DENIED` fail immediately as `config_error`; other HTTP 403 responses are retried.

Report requests page through results 100,000 rows at a time. Pivot reports aren't paginated, so the row limits in the pivot definition determine how much data a pivot report returns.

## Troubleshooting

Common issues and their causes:

- **`PERMISSION_DENIED` or a 403 error on connection check.** The authenticated identity doesn't have access to the property. On Airbyte Open Source, confirm you added the service account email to **Property access management** for every property ID in the config. Enabling the Data API in Google Cloud isn't enough on its own.
- **The connection check fails and the property ID looks like `UA-123...-1`.** That's a Universal Analytics property. The Data API only serves GA4 properties.
- **An HTTP 400 error naming a dimension or metric.** The dimension and metric combination isn't valid for the property. Verify it in the [GA4 Dimensions & Metrics Explorer](https://ga-dev-tools.google/ga4/dimensions-metrics-explorer/).
- **Recent numbers change between syncs.** Google can take 24 to 48 hours to finalize data, and attribution keeps shifting during that window. Increase **Lookback window (Days)** so each sync re-reads more recent days. See [Google's documentation](https://support.google.com/analytics/answer/9333790?hl=en) on data freshness.
- **Metrics don't match the Google Analytics UI.** Check whether sampling applied to the request, and lower **Data Request Interval (Days)** if it did. Google also [thresholds](https://support.google.com/analytics/answer/9383630) rows that could identify individual users, so reports with demographic or interest dimensions can omit data that aggregate reports include.

## Data type map

| Integration Type | Airbyte Type |
|:-----------------|:-------------|
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version        | Date       | Pull Request                                             | Subject                                                                                                                                                                |
|:---------------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2.11.0-rc.1 | 2026-08-17 | [83783](https://github.com/airbytehq/airbyte/pull/83783) | Add an opt-in **One Stream per Report** mode that combines all configured property IDs into one stream per report named `<report_name>Consolidated`, with schemas merged across properties. Off by default; existing connections are unchanged |
| 2.10.2 | 2026-08-12 | [83343](https://github.com/airbytehq/airbyte/pull/83343) | Preserve nested `name` fields when resolving dynamic streams |
| 2.10.1 | 2026-08-11 | [83952](https://github.com/airbytehq/airbyte/pull/83952) | Update dependencies |
| 2.10.0 | 2026-08-10 | [83273](https://github.com/airbytehq/airbyte/pull/83273) | Add the `property_metadata` stream with GA4 property metadata from the Admin API |
| 2.9.45 | 2026-07-28 | [82938](https://github.com/airbytehq/airbyte/pull/82938) | Update dependencies |
| 2.9.44 | 2026-07-21 | [82436](https://github.com/airbytehq/airbyte/pull/82436) | Update dependencies |
| 2.9.43 | 2026-07-14 | [81845](https://github.com/airbytehq/airbyte/pull/81845) | Update dependencies |
| 2.9.42 | 2026-06-30 | [81086](https://github.com/airbytehq/airbyte/pull/81086) | Update dependencies |
| 2.9.41 | 2026-06-23 | [80482](https://github.com/airbytehq/airbyte/pull/80482) | Update dependencies |
| 2.9.40 | 2026-06-16 | [79881](https://github.com/airbytehq/airbyte/pull/79881) | Update dependencies |
| 2.9.39 | 2026-06-09 | [79340](https://github.com/airbytehq/airbyte/pull/79340) | Update dependencies |
| 2.9.38 | 2026-06-02 | [77618](https://github.com/airbytehq/airbyte/pull/77618) | Infer `auth_type` from credentials when missing to fix OAuth connection failures |
| 2.9.37 | 2026-06-02 | [77243](https://github.com/airbytehq/airbyte/pull/77243) | Update dependencies |
| 2.9.36 | 2026-06-01 | [77877](https://github.com/airbytehq/airbyte/pull/77877) | Update the connector runtime to the latest CDK version and reduce intermittent stream read hangs |
| 2.9.35 | 2026-05-20 | [78275](https://github.com/airbytehq/airbyte/pull/78275) | Restore `default_concurrency` to 4 after c=6 rollout showed heartbeat timeout outliers |
| 2.9.34 | 2026-05-18 | [78161](https://github.com/airbytehq/airbyte/pull/78161) | Promoted release candidate to GA |
| 2.9.34-rc.2 | 2026-05-06 | [77781](https://github.com/airbytehq/airbyte/pull/77781) | Phase 1 step 3: bump `default_concurrency` 5 to 6 (tier-aware `api_budget` stays live) |
| 2.9.34-rc.1 | 2026-04-28 | [77550](https://github.com/airbytehq/airbyte/pull/77550) | Phase 1 step 2: bump `default_concurrency` 4 to 5 and activate the tier-aware `api_budget` (Standard 10 req/s, Analytics 360 50 req/s on opt-in via `subscription_tier`) |
| 2.9.33-rc.1 | 2026-04-27 | [76956](https://github.com/airbytehq/airbyte/pull/76956) | Add `concurrency_level` (default 4, max 16) and `subscription_tier` spec field (Standard or Analytics 360) for the Path B concurrency tuning rollout (RC); existing and tier-aware `api_budget` kept commented during tuning |
| 2.9.32 | 2026-04-21 | [76600](https://github.com/airbytehq/airbyte/pull/76600) | Update dependencies |
| 2.9.31 | 2026-04-20 | [76185](https://github.com/airbytehq/airbyte/pull/76185) | Surface the GA4 API error message on 400 and 403 responses, and stop retrying permission errors |
| 2.9.30 | 2026-04-14 | [76190](https://github.com/airbytehq/airbyte/pull/76190) | Add access_token to extract_output and complete_oauth_output_specification to fix OAuth secretId 422 regression |
| 2.9.29 | 2026-04-02 | [75580](https://github.com/airbytehq/airbyte/pull/75580) | Add `oauth_connector_input_specification` with granular scopes |
| 2.9.28 | 2026-03-31 | [75678](https://github.com/airbytehq/airbyte/pull/75678) | Update dependencies |
| 2.9.27 | 2026-03-24 | [74568](https://github.com/airbytehq/airbyte/pull/74568) | Update dependencies |
| 2.9.26 | 2026-02-25 | [73632](https://github.com/airbytehq/airbyte/pull/73632) | Use the GA4 `today` keyword for timezone-correct end dates |
| 2.9.25 | 2026-02-24 | [73750](https://github.com/airbytehq/airbyte/pull/73750) | Update dependencies |
| 2.9.24 | 2026-02-17 | [73404](https://github.com/airbytehq/airbyte/pull/73404) | Update dependencies |
| 2.9.23 | 2026-02-10 | [73067](https://github.com/airbytehq/airbyte/pull/73067) | Update dependencies |
| 2.9.22 | 2026-02-06 | [72590](https://github.com/airbytehq/airbyte/pull/72590) | Update dependencies |
| 2.9.21 | 2026-01-20 | [71924](https://github.com/airbytehq/airbyte/pull/71924) | Update dependencies |
| 2.9.20 | 2026-01-14 | [71432](https://github.com/airbytehq/airbyte/pull/71432) | Update dependencies |
| 2.9.19 | 2025-12-18 | [70693](https://github.com/airbytehq/airbyte/pull/70693) | Update dependencies |
| 2.9.18 | 2025-11-25 | [69892](https://github.com/airbytehq/airbyte/pull/69892) | Update dependencies |
| 2.9.17 | 2025-11-18 | [69414](https://github.com/airbytehq/airbyte/pull/69414) | Update dependencies |
| 2.9.16 | 2025-11-12 | [69279](https://github.com/airbytehq/airbyte/pull/69279) | Flag authentication issues as config_error |
| 2.9.15 | 2025-10-29 | [69011](https://github.com/airbytehq/airbyte/pull/69011) | Update dependencies |
| 2.9.14 | 2025-10-21 | [68302](https://github.com/airbytehq/airbyte/pull/68302) | Update dependencies |
| 2.9.13 | 2025-10-14 | [67722](https://github.com/airbytehq/airbyte/pull/67722)     | Promoting release candidate 2.9.13-rc.1 to a main version. |
| 2.9.13-rc.1 | 2025-10-08 | [67148](https://github.com/airbytehq/airbyte/pull/67148) | Add dimensionFilter into the body of requests for custom reports and custom DimensionFilterConfigTransformation component                                              |
| 2.9.12 | 2025-10-07 | [67262](https://github.com/airbytehq/airbyte/pull/67262) | Update dependencies |
| 2.9.11 | 2025-09-30 | [66306](https://github.com/airbytehq/airbyte/pull/66306) | Update dependencies |
| 2.9.10 | 2025-09-10 | [66008](https://github.com/airbytehq/airbyte/pull/66008) | Update to CDK v7 |
| 2.9.9 | 2025-09-09 | [65895](https://github.com/airbytehq/airbyte/pull/65895) | Update dependencies |
| 2.9.8 | 2025-08-23 | [65311](https://github.com/airbytehq/airbyte/pull/65311) | Update dependencies |
| 2.9.7 | 2025-08-09 | [64631](https://github.com/airbytehq/airbyte/pull/64631) | Update dependencies |
| 2.9.6 | 2025-08-02 | [64254](https://github.com/airbytehq/airbyte/pull/64254) | Update dependencies |
| 2.9.5 | 2025-07-26 | [63820](https://github.com/airbytehq/airbyte/pull/63820) | Update dependencies |
| 2.9.4 | 2025-07-19 | [63528](https://github.com/airbytehq/airbyte/pull/63528) | Update dependencies |
| 2.9.3 | 2025-07-16 | [63339](https://github.com/airbytehq/airbyte/pull/63339) | Promoting release candidate 2.9.3-rc.2 to a main version. |
| 2.9.3-rc.2 | 2025-07-15 | [63297](https://github.com/airbytehq/airbyte/pull/63297) | Enable progressive rollout |
| 2.9.3-rc.1 | 2025-07-15 | [63297](https://github.com/airbytehq/airbyte/pull/63297) | Fix bug where concurrent partitions are not merged back together properly so sequential state can't progress to the latest record |
| 2.9.2 | 2025-07-12 | [63129](https://github.com/airbytehq/airbyte/pull/63129) | Update dependencies |
| 2.9.1 | 2025-07-05 | [61135](https://github.com/airbytehq/airbyte/pull/61135) | Update dependencies |
| 2.9.0 | 2025-07-03 | [62507](https://github.com/airbytehq/airbyte/pull/62507) | Promoting release candidate 2.9.0-rc.1 to a main version. |
| 2.9.0-rc.1     | 2025-06-30 | [61550](https://github.com/airbytehq/airbyte/pull/61550) | Unwrap to manifest-only                                                                                                                                                |
| 2.8.2          | 2025-06-17 | [61678](https://github.com/airbytehq/airbyte/pull/61678) | Bump Memory on CHECK to 1600Mi |
| 2.8.1          | 2025-06-12 | [61555](https://github.com/airbytehq/airbyte/pull/61555) | Fixes time data parsing issue |
| 2.8.0          | 2025-06-11 | [61533](https://github.com/airbytehq/airbyte/pull/61533) | Promoting release candidate 2.8.0-rc.2 to a main version. |
| 2.8.0-rc.2     | 2025-06-11 | [61491](https://github.com/airbytehq/airbyte/pull/61491) | Fixed cohort check, record extractor and discovery                                                                                                                     |
| 2.8.0-rc.1     | 2025-05-20 | [60342](https://github.com/airbytehq/airbyte/pull/60342) | Migrate to low-code                                                                                                                                                    |
| 2.7.7          | 2025-05-17 | [60708](https://github.com/airbytehq/airbyte/pull/60708) | Update dependencies                                                                                                                                                    |
| 2.7.6          | 2025-05-10 | [59870](https://github.com/airbytehq/airbyte/pull/59870) | Update dependencies                                                                                                                                                    |
| 2.7.5          | 2025-05-03 | [59225](https://github.com/airbytehq/airbyte/pull/59225) | Update dependencies                                                                                                                                                    |
| 2.7.4          | 2025-04-26 | [58808](https://github.com/airbytehq/airbyte/pull/58808) | Update dependencies                                                                                                                                                    |
| 2.7.3          | 2025-04-12 | [57703](https://github.com/airbytehq/airbyte/pull/57703) | Update dependencies                                                                                                                                                    |
| 2.7.2          | 2025-04-05 | [57063](https://github.com/airbytehq/airbyte/pull/57063) | Update dependencies                                                                                                                                                    |
| 2.7.1          | 2025-03-29 | [50048](https://github.com/airbytehq/airbyte/pull/50048) | Update dependencies                                                                                                                                                    |
| 2.7.0          | 2025-02-12 | [48381](https://github.com/airbytehq/airbyte/pull/48381) | add end date optional parameter                                                                                                                                        |
| 2.6.2          | 2024-12-14 | [48649](https://github.com/airbytehq/airbyte/pull/48649) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 2.6.1          | 2024-10-29 | [47899](https://github.com/airbytehq/airbyte/pull/47899) | Update dependencies                                                                                                                                                    |
| 2.6.0          | 2024-10-28 | [47013](https://github.com/airbytehq/airbyte/pull/47013) | Migrate to CDK v5                                                                                                                                                      |
| 2.5.13         | 2024-10-28 | [47061](https://github.com/airbytehq/airbyte/pull/47061) | Update dependencies                                                                                                                                                    |
| 2.5.12         | 2024-10-12 | [46819](https://github.com/airbytehq/airbyte/pull/46819) | Update dependencies                                                                                                                                                    |
| 2.5.11         | 2024-10-05 | [46475](https://github.com/airbytehq/airbyte/pull/46475) | Update dependencies                                                                                                                                                    |
| 2.5.10         | 2024-09-28 | [46158](https://github.com/airbytehq/airbyte/pull/46158) | Update dependencies                                                                                                                                                    |
| 2.5.9          | 2024-09-21 | [45773](https://github.com/airbytehq/airbyte/pull/45773) | Update dependencies                                                                                                                                                    |
| 2.5.8          | 2024-09-14 | [45503](https://github.com/airbytehq/airbyte/pull/45503) | Update dependencies                                                                                                                                                    |
| 2.5.7          | 2024-09-07 | [45289](https://github.com/airbytehq/airbyte/pull/45289) | Update dependencies                                                                                                                                                    |
| 2.5.6          | 2024-08-31 | [44980](https://github.com/airbytehq/airbyte/pull/44980) | Update dependencies                                                                                                                                                    |
| 2.5.5          | 2024-08-24 | [44645](https://github.com/airbytehq/airbyte/pull/44645) | Update dependencies                                                                                                                                                    |
| 2.5.4          | 2024-08-17 | [44337](https://github.com/airbytehq/airbyte/pull/44337) | Update dependencies                                                                                                                                                    |
| 2.5.3          | 2024-08-13 | [43929](https://github.com/airbytehq/airbyte/pull/43929) | Increase streams max_time to backoff                                                                                                                                   |
| 2.5.2          | 2024-08-12 | [43909](https://github.com/airbytehq/airbyte/pull/43909) | Update dependencies                                                                                                                                                    |
| 2.5.1          | 2024-08-10 | [43289](https://github.com/airbytehq/airbyte/pull/43289) | Update dependencies                                                                                                                                                    |
| 2.5.0          | 2024-08-07 | [42841](https://github.com/airbytehq/airbyte/pull/42841) | Upgrade to CDK 3                                                                                                                                                       |
| 2.4.14         | 2024-07-27 | [42746](https://github.com/airbytehq/airbyte/pull/42746) | Update dependencies                                                                                                                                                    |
| 2.4.13         | 2024-07-20 | [42347](https://github.com/airbytehq/airbyte/pull/42347) | Update dependencies                                                                                                                                                    |
| 2.4.12         | 2024-07-13 | [41801](https://github.com/airbytehq/airbyte/pull/41801) | Update dependencies                                                                                                                                                    |
| 2.4.11         | 2024-07-10 | [41561](https://github.com/airbytehq/airbyte/pull/41561) | Update dependencies                                                                                                                                                    |
| 2.4.10         | 2024-07-09 | [41295](https://github.com/airbytehq/airbyte/pull/41295) | Update dependencies                                                                                                                                                    |
| 2.4.9          | 2024-07-06 | [40935](https://github.com/airbytehq/airbyte/pull/40935) | Update dependencies                                                                                                                                                    |
| 2.4.8          | 2024-06-25 | [40429](https://github.com/airbytehq/airbyte/pull/40429) | Update dependencies                                                                                                                                                    |
| 2.4.7          | 2024-06-22 | [40140](https://github.com/airbytehq/airbyte/pull/40140) | Update dependencies                                                                                                                                                    |
| 2.4.6          | 2024-06-21 | [39916](https://github.com/airbytehq/airbyte/pull/39916) | Added ability to skip `missing stream` in the CATALOG                                                                                                                  |
| 2.4.5          | 2024-06-06 | [38884](https://github.com/airbytehq/airbyte/pull/38884) | Make lookback window configurable.                                                                                                                                     |
| 2.4.4          | 2024-06-06 | [39209](https://github.com/airbytehq/airbyte/pull/39209) | [autopull] Upgrade base image to v1.2.2                                                                                                                                |
| 2.4.3          | 2024-06-03 | [38865](https://github.com/airbytehq/airbyte/pull/38865) | Enforce unique property IDs                                                                                                                                            |
| 2.4.2          | 2024-03-20 | [36302](https://github.com/airbytehq/airbyte/pull/36302) | Don't extract state from the latest record if stream doesn't have a cursor_field                                                                                       |
| 2.4.1          | 2024-02-09 | [35073](https://github.com/airbytehq/airbyte/pull/35073) | Manage dependencies with Poetry.                                                                                                                                       |
| 2.4.0          | 2024-02-07 | [34951](https://github.com/airbytehq/airbyte/pull/34951) | Replace the spec parameter from previous version to convert all `conversions:*` fields                                                                                 |
| 2.3.0          | 2024-02-06 | [34907](https://github.com/airbytehq/airbyte/pull/34907) | Add new parameter to spec to convert `conversions:purchase` field to float                                                                                             |
| 2.2.2          | 2024-02-01 | [34708](https://github.com/airbytehq/airbyte/pull/34708) | Add rounding integer values that may be float                                                                                                                          |
| 2.2.1          | 2024-01-18 | [34352](https://github.com/airbytehq/airbyte/pull/34352) | Add incorrect custom reports config handling                                                                                                                           |
| 2.2.0          | 2024-01-10 | [34176](https://github.com/airbytehq/airbyte/pull/34176) | Add a report option keepEmptyRows                                                                                                                                      |
| 2.1.1          | 2024-01-08 | [34018](https://github.com/airbytehq/airbyte/pull/34018) | prepare for airbyte-lib                                                                                                                                                |
| 2.1.0          | 2023-12-28 | [33802](https://github.com/airbytehq/airbyte/pull/33802) | Add `CohortSpec` to custom report in specification                                                                                                                     |
| 2.0.3          | 2023-11-03 | [32149](https://github.com/airbytehq/airbyte/pull/32149) | Fixed bug with missing `metadata` when the credentials are not valid                                                                                                   |
| 2.0.2          | 2023-11-02 | [32094](https://github.com/airbytehq/airbyte/pull/32094) | Added handling for `JSONDecodeError` while checking for `api qouta` limits                                                                                             |
| 2.0.1          | 2023-10-18 | [31543](https://github.com/airbytehq/airbyte/pull/31543) | Base image migration: remove Dockerfile and use the python-connector-base image                                                                                        |
| 2.0.0          | 2023-09-29 | [30930](https://github.com/airbytehq/airbyte/pull/30930) | Use distinct stream naming in case there are multiple properties in the config.                                                                                        |
| 1.6.0          | 2023-09-19 | [30460](https://github.com/airbytehq/airbyte/pull/30460) | Migrated custom reports from string to array; add `FilterExpressions` support                                                                                          |
| 1.5.1          | 2023-09-20 | [30608](https://github.com/airbytehq/airbyte/pull/30608) | Revert `:` auto replacement name to underscore                                                                                                                         |
| 1.5.0          | 2023-09-18 | [30421](https://github.com/airbytehq/airbyte/pull/30421) | Add `yearWeek`, `yearMonth`, `year` dimensions cursor                                                                                                                  |
| 1.4.1          | 2023-09-17 | [30506](https://github.com/airbytehq/airbyte/pull/30506) | Fix None type error when metrics or dimensions response does not have name                                                                                             |
| 1.4.0          | 2023-09-15 | [30417](https://github.com/airbytehq/airbyte/pull/30417) | Change start date to optional; add suggested streams and update errors handling                                                                                        |
| 1.3.1          | 2023-09-14 | [30424](https://github.com/airbytehq/airbyte/pull/30424) | Fixed duplicated stream issue                                                                                                                                          |
| 1.3.0          | 2023-09-13 | [30152](https://github.com/airbytehq/airbyte/pull/30152) | Ability to add multiple property ids                                                                                                                                   |
| 1.2.0          | 2023-09-11 | [30290](https://github.com/airbytehq/airbyte/pull/30290) | Add new preconfigured reports                                                                                                                                          |
| 1.1.3          | 2023-08-04 | [29103](https://github.com/airbytehq/airbyte/pull/29103) | Update input field descriptions                                                                                                                                        |
| 1.1.2          | 2023-07-03 | [27909](https://github.com/airbytehq/airbyte/pull/27909) | Limit the page size of custom report streams                                                                                                                           |
| 1.1.1          | 2023-06-26 | [27718](https://github.com/airbytehq/airbyte/pull/27718) | Limit the page size when calling `check()`                                                                                                                             |
| 1.1.0          | 2023-06-26 | [27738](https://github.com/airbytehq/airbyte/pull/27738) | License Update: Elv2                                                                                                                                                   |
| 1.0.0          | 2023-06-22 | [26283](https://github.com/airbytehq/airbyte/pull/26283) | Added primary_key and lookback window                                                                                                                                  |
| 0.2.7          | 2023-06-21 | [27531](https://github.com/airbytehq/airbyte/pull/27531) | Fix formatting                                                                                                                                                         |
| 0.2.6          | 2023-06-09 | [27207](https://github.com/airbytehq/airbyte/pull/27207) | Improve api rate limit messages                                                                                                                                        |
| 0.2.5          | 2023-06-08 | [27175](https://github.com/airbytehq/airbyte/pull/27175) | Improve Error Messages                                                                                                                                                 |
| 0.2.4          | 2023-06-01 | [26887](https://github.com/airbytehq/airbyte/pull/26887) | Remove `authSpecification` from connector spec in favour of `advancedAuth`                                                                                             |
| 0.2.3          | 2023-05-16 | [26126](https://github.com/airbytehq/airbyte/pull/26126) | Fix pagination                                                                                                                                                         |
| 0.2.2          | 2023-05-12 | [25987](https://github.com/airbytehq/airbyte/pull/25987) | Categorized Config Errors Accurately                                                                                                                                   |
| 0.2.1          | 2023-05-11 | [26008](https://github.com/airbytehq/airbyte/pull/26008) | Added handling for `429 - potentiallyThresholdedRequestsPerHour` error                                                                                                 |
| 0.2.0          | 2023-04-13 | [25179](https://github.com/airbytehq/airbyte/pull/25179) | Implement support for custom Cohort and Pivot reports                                                                                                                  |
| 0.1.3          | 2023-03-10 | [23872](https://github.com/airbytehq/airbyte/pull/23872) | Fix parse + cursor for custom reports                                                                                                                                  |
| 0.1.2          | 2023-03-07 | [23822](https://github.com/airbytehq/airbyte/pull/23822) | Improve `rate limits` customer faced error messages and retry logic for `429`                                                                                          |
| 0.1.1          | 2023-01-10 | [21169](https://github.com/airbytehq/airbyte/pull/21169) | Slicer updated, unit tests added                                                                                                                                       |
| 0.1.0          | 2023-01-08 | [20889](https://github.com/airbytehq/airbyte/pull/20889) | Improved config validation, SAT                                                                                                                                        |
| 0.0.3          | 2022-08-15 | [15229](https://github.com/airbytehq/airbyte/pull/15229) | Source Google Analytics Data Api: code refactoring                                                                                                                     |
| 0.0.2          | 2022-07-27 | [15087](https://github.com/airbytehq/airbyte/pull/15087) | fix documentationUrl                                                                                                                                                   |
| 0.0.1          | 2022-05-09 | [12701](https://github.com/airbytehq/airbyte/pull/12701) | Introduce Google Analytics Data API source                                                                                                                             |

</details>
