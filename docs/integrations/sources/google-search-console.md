# Google Search Console

<HideInUI>

This page contains the setup guide and reference information for the [Google Search Console](https://search.google.com/search-console/about) source connector.

</HideInUI>

## Prerequisites

- Google Account
- One or more verified properties in Google Search Console. You need the exact property identifier for each one. URL-prefix properties look like `https://example.com/`, and Domain properties look like `sc-domain:example.com`. See [Google's guide to property types](https://support.google.com/webmasters/answer/34592).
<!-- env:oss -->
- Google Search Console API enabled for your project (**Airbyte Open Source** only)
<!-- /env:oss -->

## Setup guide

### Step 1: Set up Google Search Console

To authenticate the Google Search Console connector, you will need to use one of the following methods:

<!-- env:cloud -->

#### OAuth (Recommended for Airbyte Cloud)

You can authenticate using your Google Account with OAuth if you are the owner of the Google Search Console property or have view permissions. Follow [Google's instructions](https://support.google.com/webmasters/answer/7687615?sjid=11103698321670173176-NA) to ensure that your account has the necessary permissions (**Owner** or **Full User**) to view the Google Search Console property. This option is recommended for **Airbyte Cloud** users, as it significantly simplifies the setup process and allows you to authenticate the connection [directly from the Airbyte UI](#step-2-set-up-the-google-search-console-connector-in-airbyte).

<!-- /env:cloud -->

<!-- env:oss -->

To authenticate with OAuth in **Airbyte Open Source**, you will need to create an authentication app and obtain the following credentials and tokens:

- Client ID
- Client Secret
- Refresh Token

Create an OAuth app and obtain a refresh token with the `https://www.googleapis.com/auth/webmasters.readonly` scope and offline access. The connector uses the refresh token to obtain access tokens automatically; you don't need to supply an **Access Token**. See [Google's authorization guide](https://developers.google.com/webmaster-tools/v1/how-tos/authorizing) and [web-server OAuth flow](https://developers.google.com/identity/protocols/oauth2/web-server#offline).

#### Google service account with JSON key file (Recommended for Airbyte Open Source)

You can authenticate the connection using a JSON key file associated with a Google service account. This option is recommended for **Airbyte Open Source** users. Follow the steps below to create a service account and generate the JSON key file:

1. Open the [Service Accounts page](https://console.developers.google.com/iam-admin/serviceaccounts).
2. Select an existing project, or create a new project.
3. At the top of the page, click **+ Create service account**.
4. Enter a name and description for the service account, then click **Create and Continue**.
5. Skip the optional project IAM roles, then click **Continue**. Project IAM roles do not grant access to Search Console properties.
   - Optional: Under **Grant users access to this service account**, you may specify the users or groups that are allowed to use and manage the service account.
6. Go to the [API Console/Credentials](https://console.cloud.google.com/apis/credentials) and click on the email address of the service account you just created.
7. In the **Keys** tab, click **+ Add key**, then click **Create new key**.
8. Select **JSON** as the Key type. This will generate and download the JSON key file that you'll use for authentication. Click **Continue**.
9. Copy the `client_email` from the JSON key. For each property you want to sync, ask a property owner to open **Settings > Users and permissions > Add user** in Search Console and add this email with **Full** permission. See [Google's permissions guide](https://support.google.com/webmasters/answer/7687615).

:::caution
This file serves as the only copy of your JSON service key, and you will not be able to re-download it. Be sure to store it in a secure location.
:::

:::note
You can return to the [API Console/Credentials](https://console.cloud.google.com/apis/credentials) at any time to manage your service account or generate additional JSON keys. For more details about service account credentials, see [Google's IAM documentation](https://cloud.google.com/iam/docs/understanding-service-accounts).
:::

The connector requests the `https://www.googleapis.com/auth/webmasters.readonly` scope and authenticates as the service account itself. It does not impersonate a Google Workspace user, so domain-wide delegation is not required. Grant access to the service account email, not just to the person setting up the connector.

<!-- /env:oss -->

### Step 2: Set up the Google Search Console connector in Airbyte

<!-- env:cloud -->

#### For Airbyte Cloud

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the **Set up the source** page, select **Google Search Console** from the **Source type** dropdown.
4. Enter a name for the Google Search Console connector.
5. Select **OAuth** from the authentication dropdown, then click **Sign in with Google** to authorize an account with access to your properties.

<!-- /env:cloud -->

<!-- env:oss -->
#### For Airbyte Open Source

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the **Set up the source** page, select **Google Search Console** from the **Source type** dropdown.
4. Enter a name for the Google Search Console connector.
5. Choose an authentication method:
   - **Service Account Key Authentication** (recommended): Paste the entire JSON key into **Service Account JSON Key** and enter your administrator's email in **Admin Email**. The configuration schema requires the email field, but the connector does not use it to impersonate a user.
   - **OAuth**: Enter your **Client ID**, **Client Secret**, and **Refresh Token**.

<!-- /env:oss -->

#### Configure the source

1. For **Website URL Property**, enter each property exactly as Search Console shows it. Domain properties use the `sc-domain:` prefix, for example `sc-domain:example.com`. URL-prefix properties use the full URL, including the protocol and trailing slash, for example `https://www.example.com/`. You can add multiple properties.
2. For **Start Date**, use the date picker or enter a date in `YYYY-MM-DD` format. The default is `2021-01-01`, but only data within Google's [retention window](#data-retention) is available.
3. (Optional) For **End Date**, enter a date in `YYYY-MM-DD` format that is on or after the start date. The range includes both dates. Leave this blank to sync through the current date. Search Analytics dates use Pacific Time, as defined by [Google's API](https://developers.google.com/webmaster-tools/v1/searchanalytics/query).
4. (Optional) Add [custom reports](#custom-reports) using **Custom Reports**.
5. (Optional) Choose **Data Freshness**. Keep the default `final` for incremental syncs; `all` includes provisional data that may change. See [Data Freshness](#data-freshness).
6. (Optional) Adjust **Number of concurrent threads**. The form defaults to 40. Reduce concurrency if you encounter rate limit errors.
7. (Optional) Enable **Always Use Aggregation Type Auto** only if you need to override aggregation for all search analytics streams. Version 2.1.18 and later automatically handle Google News aggregation without this setting. See [Aggregation type errors](#aggregation-type-errors).
8. (Optional) Set **Search Analytics API Requests Per Minute** to match your Google Cloud project's quota, up to 1,200. See [Rate limiting](#rate-limiting).
9. Click **Set up source** and wait for the tests to complete.

<HideInUI>

## Supported sync modes

The Search Analytics streams, including custom reports, support the following sync modes. The `sites` and `sitemaps` streams support full refresh only.

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

:::note
The granularity for the cursor is 1 day, so Incremental Sync in Append mode may result in duplicating the data.
:::

## Supported Streams

- [`sites`](https://developers.google.com/webmaster-tools/v1/sites/get): Property information and the authenticated account's permission level for each configured property.
- [`sitemaps`](https://developers.google.com/webmaster-tools/v1/sitemaps/list): Sitemaps submitted for each configured property.

The remaining built-in streams use Google's [Search Analytics query endpoint](https://developers.google.com/webmaster-tools/v1/searchanalytics/query):

- `search_analytics_all_fields`: Full analytics report by date, country, device, page, and query. This detailed stream can take longer to sync.
- `search_analytics_by_country`
- `search_analytics_by_date`
- `search_analytics_by_device`
- `search_analytics_by_page`
- `search_analytics_by_query`
- `search_analytics_keyword_page_report`
- `search_analytics_keyword_site_report_by_page`
- `search_analytics_keyword_site_report_by_site`
- `search_analytics_page_report`
- `search_analytics_site_report_by_page`
- `search_analytics_site_report_by_site`

Each [custom report](#custom-reports) creates an additional Search Analytics stream with the name you configure.

### Entity-Relationship Diagram (ERD)

<EntityRelationshipDiagram></EntityRelationshipDiagram>

## Connector-specific configurations

### Custom reports

Custom reports allow you to query the API with a custom set of dimensions to group results by. Results are grouped in the order that you supply these dimensions. Each custom report should be constructed like following:

1. Click `Add` under the `Custom Reports` section
2. Enter the `Name` of the report, this will be the name of the stream
3. Select one or more `Dimensions` from the available dropdown list

The available `Dimensions` are:

- `country`
- `date`
- `device`
- `page`
- `query`

For example, to query the API for a report that groups results by country, then by date, you could enter the following custom report:

- Name: country_date
- Dimensions: ["country", "date"]

Please note, that for technical reasons `date` is the default dimension which will be included in your query whether you specify it or not. By specifying it you can change the order the results are grouped in. Primary key will consist of your custom dimensions and the default dimension along with `site_url` and `search_type`.

The information you provide via the UI Custom report builder will then be transformed into a custom stream using its `Name`.

You can use the [Google APIS Explorer](https://developers.google.com/webmaster-tools/v1/searchanalytics/query) to build and test the reports you want to use.

### Data Freshness

The **Data Freshness** parameter deals with the "freshness", or finality of the data that is being queried.

- `final`: The query will include only finalized, stable data. This is data that has been processed, verified, and is unlikely to change. When you select this option, you are querying for the definitive statistics and information that Google has analyzed and confirmed.
- `all`: The query will return both finalized data and what Google terms "fresh" data. Fresh data includes more recent data that hasn't gone through the full processing and verification that finalized data has. This option can give you more up-to-the-minute insights, but it may be subject to change as Google continues to process and analyze it.

:::caution
When using Incremental Sync mode, we recommend leaving this parameter to its default state of `final`, as the `all` option may cause discrepancies between the data in your destination table and the finalized data in Google Search Console.
:::

## Data type map

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

Search Analytics dimension values, such as `date`, `country`, `device`, `page`, and `query`, are always strings. Starting with version 2.1.19, the connector emits them exactly as Google returns them, so numeric-looking queries like `2024` or `1.20` and quoted queries like `"failed to fetch"` aren't converted or altered. These fields are part of each stream's primary key.

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Google Search Console connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

The Search Console API enforces two distinct types of quota on Search Analytics queries. The connector retries automatically when either type is exceeded, but with different backoff durations. For full details, see Google's [Usage Limits](https://developers.google.com/webmaster-tools/limits) documentation.

**Request-rate quota**: Google documents a maximum of 1,200 requests per minute per user and per site. Your project's quota may be lower; check it before choosing **Search Analytics API Requests Per Minute**. When exceeded, the connector retries with a 60-second backoff, plus jitter.

**Load quota**: Limits the internal resources consumed by queries. Complex queries — particularly those that group or filter by both `page` and `query` dimensions, or that span long date ranges — consume more load. Google measures load quota in 10-minute (short-term) and daily (long-term) windows. When exceeded, the connector retries with a 15-minute backoff, consistent with Google's recommendation to wait 15 minutes before retrying.

To check your actual QPS quota limits:

1. Go to your [Google Cloud Console](https://console.cloud.google.com/).
2. Navigate to **APIs & Services** then **Quotas**.
3. Search for "Search Console API".
4. Look for "Requests per minute per user" to see your current limit.

If you need higher request-rate limits, review the available quota increase options in the Google Cloud Console. Configure **Search Analytics API Requests Per Minute** to match your actual quota. Enabling billing does not replace checking the quota.

If you hit load quota limits, reduce the complexity of your queries. Avoid grouping or filtering by both `page` and `query` simultaneously, use shorter date ranges, and avoid requerying the same data repeatedly.

#### Data retention

Google Search Console only retains data for websites from the last 16 months. Any data prior to this cutoff point will not be accessible. For more information, see [Google's documentation on data freshness and availability](https://support.google.com/webmasters/answer/7576553).

#### Search Analytics data limits

Google's API returns top rows rather than guaranteeing every row. It exposes at most 50,000 rows per day per property and search type, and grouping by page or query can omit data. Pagination does not remove this upstream limit. See [Google's performance data guide](https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data).

#### Retired search appearance values

The `search_analytics_keyword_page_report`, `search_analytics_keyword_site_report_by_page`, and `search_analytics_keyword_site_report_by_site` streams break their data out by `search_appearance`. Google retires search appearance types over time — FAQ rich results stopped appearing in Search in May 2026, and Google's [FAQ structured data documentation](https://developers.google.com/search/docs/appearance/structured-data/faqpage) announced the removal of FAQ rich result data from the Search Console API in August 2026.

The connector discovers appearance values from the API on every sync rather than hard-coding them, so a retired value needs no configuration change: rows for that value simply stop arriving, and the remaining appearance values continue to sync normally. No stream or field is added or removed.

Two effects are worth planning for:

- `search_appearance` is part of these streams' primary key, and syncs do not delete rows. Records already synced for a retired appearance value remain in your destination indefinitely. If you aggregate across `search_appearance`, those rows keep contributing to totals.
- Re-syncing a historical window may no longer reproduce rows for a retired value, so a full refresh can return fewer records than the original sync did.

### Troubleshooting

#### Aggregation type errors

Starting with version 2.1.18, `search_analytics_site_report_by_site` automatically uses `aggregationType: auto` for `googleNews` and keeps `byProperty` for `web`, `news`, `image`, and `video`. Google [does not support `byProperty`](https://developers.google.com/webmaster-tools/v1/searchanalytics/query) for `googleNews` or `discover`. This stream queries Google News but does not query Discover.

If an older connector version fails with `'BY_PROPERTY' is not a valid aggregation type`, upgrade to version 2.1.18 or later. If you cannot upgrade, enable **Always Use Aggregation Type Auto** as a workaround. This setting overrides aggregation for all search analytics streams, not just Google News, and can change how metrics are grouped. Leave it off unless you need that override.

#### Site URL errors during setup or sync

The connection test reads the `sites` stream for every property you configured, so an incorrect **Website URL Property** value fails at setup rather than partway through a sync. The `sites` and `sitemaps` streams report the following errors as configuration errors:

- `Configured site URL is not a verified Search Console property in this account.` The value doesn't match a property in the Search Console account you authenticated with. Compare the value against the property list in Search Console. Common mismatches are a missing trailing slash, `http` instead of `https`, a missing or extra `www.`, or entering a plain domain instead of the `sc-domain:` form for a Domain property.
- `Configured site URL is not accessible with the account's Search Console permissions.` The property exists, but the authenticated account can't read it. Ask a property owner to add the Google account (for OAuth) or the service account email (for service account authentication) as a user on that property.

#### Other issues

- Check out common troubleshooting issues for the Google Search Console source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version     | Date       | Pull Request                                             | Subject                                                                                                                                                                |
|:------------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2.1.20 | 2026-11-05 | [91063](https://github.com/airbytehq/airbyte/pull/91063) | Clarify Website URL Property formats for Domain and URL-prefix properties |
| 2.1.19 | 2026-11-05 | [91068](https://github.com/airbytehq/airbyte/pull/91068) | Emit dimension values exactly as Google returns them, including quoted and numeric-looking queries |
| 2.1.18 | 2026-11-05 | [89665](https://github.com/airbytehq/airbyte/pull/89665) | Fix 400 errors on `search_analytics_site_report_by_site` by using `aggregationType: auto` for Google News; keep numeric-looking search queries as strings in keyword streams |
| 2.1.17 | 2026-10-13 | [88645](https://github.com/airbytehq/airbyte/pull/88645) | Update dependencies |
| 2.1.16 | 2026-10-06 | [87882](https://github.com/airbytehq/airbyte/pull/87882) | Update dependencies |
| 2.1.15 | 2026-09-29 | [87207](https://github.com/airbytehq/airbyte/pull/87207) | Update dependencies |
| 2.1.14 | 2026-09-22 | [86665](https://github.com/airbytehq/airbyte/pull/86665) | Update dependencies |
| 2.1.13 | 2026-09-15 | [86094](https://github.com/airbytehq/airbyte/pull/86094) | Update dependencies |
| 2.1.12 | 2026-09-09 | [75289](https://github.com/airbytehq/airbyte/pull/75289) | Improve error messages for unverified or inaccessible site URLs on the sites and sitemaps streams |
| 2.1.11 | 2026-09-08 | [85529](https://github.com/airbytehq/airbyte/pull/85529) | Update dependencies |
| 2.1.10 | 2026-08-18 | [84615](https://github.com/airbytehq/airbyte/pull/84615) | Update dependencies |
| 2.1.9 | 2026-08-11 | [83959](https://github.com/airbytehq/airbyte/pull/83959) | Update dependencies |
| 2.1.8 | 2026-07-28 | [83194](https://github.com/airbytehq/airbyte/pull/83194) | Update to CDK 7.23.8 (fixes AirbyteCustomCodeNotPermittedError for bundled custom components) and remove the temporary Cloud version override |
| 2.1.7 | 2026-07-28 | [1082](https://github.com/airbytehq/airbyte-python-cdk/issues/1082) | Roll Cloud back to 2.1.5 — 2.1.6 is built on SDM 7.23.7, which breaks bundled custom components |
| 2.1.6 | 2026-07-28 | [82942](https://github.com/airbytehq/airbyte/pull/82942) | Update dependencies |
| 2.1.5 | 2026-07-21 | [82440](https://github.com/airbytehq/airbyte/pull/82440) | Update dependencies |
| 2.1.4 | 2026-07-14 | [81851](https://github.com/airbytehq/airbyte/pull/81851) | Update dependencies |
| 2.1.3 | 2026-06-30 | [81094](https://github.com/airbytehq/airbyte/pull/81094) | Update dependencies |
| 2.1.2 | 2026-06-23 | [80489](https://github.com/airbytehq/airbyte/pull/80489) | Update dependencies |
| 2.1.1 | 2026-06-16 | [79906](https://github.com/airbytehq/airbyte/pull/79906) | Update dependencies |
| 2.1.0 | 2026-06-12 | [79146](https://github.com/airbytehq/airbyte/pull/79146) | Handle 403 "Search Analytics load quota exceeded" as rate-limited with a 15-minute backoff instead of config error |
| 2.0.4 | 2026-06-09 | [79344](https://github.com/airbytehq/airbyte/pull/79344) | Update dependencies |
| 2.0.3 | 2026-06-01 | [78545](https://github.com/airbytehq/airbyte/pull/78545) | Adds jitter to backoff strategy |
| 2.0.2 | 2026-05-21 | [78289](https://github.com/airbytehq/airbyte/pull/78289) | Reduce `search_analytics_*` paginator `page_size` from `25000` to `5000` to lower peak worker memory on high-volume tenants. See airbytehq/oncall#12246 for context. |
| 2.0.1 | 2026-05-18 | [78157](https://github.com/airbytehq/airbyte/pull/78157) | Restore `default_concurrency` to `num_workers`-driven configuration (`{{ config.get('num_workers', 3) }}`) and keep `max_concurrency` at `100`; cancels the Phase 1 concurrency tuning rollout introduced in 2.0.1-rc.1 |
| 2.0.0 | 2026-05-04 | [76306](https://github.com/airbytehq/airbyte/pull/76306) | Append `search_appearance` to existing primary keys of keyword report streams; drop duplicate unfiltered keyword rows caused by empty/null `searchAppearance` partitions; fix multi-site duplication by removing the cartesian-product over `site_urls` on keyword streams; wrap `dimensionFilterGroups.filters` in an array to match the Google Search Console API spec. This is a **breaking change** for the `search_analytics_keyword_page_report`, `search_analytics_keyword_site_report_by_page`, and `search_analytics_keyword_site_report_by_site` streams. See the [migration guide](https://docs.airbyte.com/integrations/sources/google-search-console-migrations) for details. |
| 1.10.33 | 2026-04-28 | [77276](https://github.com/airbytehq/airbyte/pull/77276) | Update dependencies |
| 1.10.32 | 2026-04-21 | [76624](https://github.com/airbytehq/airbyte/pull/76624) | Update dependencies |
| 1.10.31 | 2026-04-14 | [76190](https://github.com/airbytehq/airbyte/pull/76190) | Add access_token to extract_output and complete_oauth_output_specification to fix OAuth secretId 422 regression |
| 1.10.30 | 2026-04-13 | [76276](https://github.com/airbytehq/airbyte/pull/76276) | Rename "concurrent workers" to "concurrent threads" in connector spec |
| 1.10.29 | 2026-04-01 | [75582](https://github.com/airbytehq/airbyte/pull/75582) | Add `oauth_connector_input_specification` with granular scopes |
| 1.10.28 | 2026-03-31 | [75699](https://github.com/airbytehq/airbyte/pull/75699) | Update dependencies |
| 1.10.27 | 2026-03-30 | [75426](https://github.com/airbytehq/airbyte/pull/75426) | Guard numeric metric fields against complex types to prevent serialization failures and deadlocks |
| 1.10.26 | 2026-03-24 | [74935](https://github.com/airbytehq/airbyte/pull/74935) | Update dependencies |
| 1.10.25 | 2026-03-10 | [74685](https://github.com/airbytehq/airbyte/pull/74685) | Update dependencies |
| 1.10.24 | 2026-02-24 | [73935](https://github.com/airbytehq/airbyte/pull/73935) | Update dependencies |
| 1.10.23 | 2026-02-17 | [73372](https://github.com/airbytehq/airbyte/pull/73372) | Update dependencies |
| 1.10.22 | 2026-02-10 | [72683](https://github.com/airbytehq/airbyte/pull/72683) | Update dependencies |
| 1.10.21 | 2026-01-20 | [71877](https://github.com/airbytehq/airbyte/pull/71877) | Update dependencies |
| 1.10.20 | 2026-01-14 | [71722](https://github.com/airbytehq/airbyte/pull/71722) | Update dependencies |
| 1.10.19 | 2025-12-18 | [70517](https://github.com/airbytehq/airbyte/pull/70517) | Update dependencies |
| 1.10.18 | 2025-12-09 | [70444](https://github.com/airbytehq/airbyte/pull/70444) | Add user-configurable API rate limit option for Search Analytics streams |
| 1.10.17 | 2025-11-25 | [70059](https://github.com/airbytehq/airbyte/pull/70059) | Update dependencies |
| 1.10.16 | 2025-11-18 | [69392](https://github.com/airbytehq/airbyte/pull/69392) | Update dependencies |
| 1.10.15 | 2025-10-29 | [68771](https://github.com/airbytehq/airbyte/pull/68771) | Update dependencies |
| 1.10.14 | 2025-10-21 | [68231](https://github.com/airbytehq/airbyte/pull/68231) | Update dependencies |
| 1.10.13 | 2025-10-14 | [68004](https://github.com/airbytehq/airbyte/pull/68004) | Update dependencies |
| 1.10.12 | 2025-10-07 | [67263](https://github.com/airbytehq/airbyte/pull/67263) | Update dependencies |
| 1.10.11 | 2025-09-30 | [65384](https://github.com/airbytehq/airbyte/pull/65384) | Update dependencies |
| 1.10.10 | 2025-09-16 | [66010](https://github.com/airbytehq/airbyte/pull/66010) | Update to CDK v7 |
| 1.10.9 | 2025-08-09 | [64584](https://github.com/airbytehq/airbyte/pull/64584) | Update dependencies |
| 1.10.8 | 2025-08-02 | [64187](https://github.com/airbytehq/airbyte/pull/64187) | Update dependencies |
| 1.10.7 | 2025-07-26 | [63877](https://github.com/airbytehq/airbyte/pull/63877) | Update dependencies |
| 1.10.6 | 2025-07-23 | [63720](https://github.com/airbytehq/airbyte/pull/63720) | Ignore 403 "insufficient permission" errors |
| 1.10.5 | 2025-07-19 | [63471](https://github.com/airbytehq/airbyte/pull/63471) | Update dependencies |
| 1.10.4 | 2025-07-15 | [63309](https://github.com/airbytehq/airbyte/pull/63309) | Adds `type` property to `config_normalization_rules` in manifest |
| 1.10.3 | 2025-07-12 | [63094](https://github.com/airbytehq/airbyte/pull/63094) | Update dependencies |
| 1.10.2 | 2025-07-05 | [62613](https://github.com/airbytehq/airbyte/pull/62613) | Update dependencies |
| 1.10.1 | 2025-06-28 | [62194](https://github.com/airbytehq/airbyte/pull/62194) | Update dependencies |
| 1.10.0 | 2025-06-23 | [61425](https://github.com/airbytehq/airbyte/pull/61425) | Migrate to manifest-only |
| 1.9.4 | 2025-06-21 | [61789](https://github.com/airbytehq/airbyte/pull/61789) | Update dependencies |
| 1.9.3 | 2025-06-18 | [61706](https://github.com/airbytehq/airbyte/pull/61706) | Fix record serialization bug |
| 1.9.2 | 2025-06-14 | [60663](https://github.com/airbytehq/airbyte/pull/60663) | Update dependencies |
| 1.9.1 | 2025-06-10 | [61514](https://github.com/airbytehq/airbyte/pull/61514) | Promoting release candidate 1.9.1-rc.1 to a main version. |
| 1.9.1-rc.1 | 2025-06-10 | [61508](https://github.com/airbytehq/airbyte/pull/61508) | Add API budget, reduce concurrency levels, and catch 403 rate limiting errors |
| 1.9.0 | 2025-06-06 | [61408](https://github.com/airbytehq/airbyte/pull/61408) | Migrate custom reports streams to low-code |
| 1.8.0 | 2025-06-06 | [61335](https://github.com/airbytehq/airbyte/pull/61335) | Migrate `SearchAnalyticsAllFields`, `SearchAnalyticsByDate`, `SearchAnalyticsByDevice`, `SearchAnalyticsByPage`, and `SearchAnalyticsByQuery` to low-code |
| 1.7.0 | 2025-06-05 | [61332](https://github.com/airbytehq/airbyte/pull/61332) | Migrate search_by_keyword streams to low-code |
| 1.6.0 | 2025-06-04 | [61380](https://github.com/airbytehq/airbyte/pull/61380) | Promoting release candidate 1.6.0-rc.1 to a main version. |
| 1.6.0-rc.1 | 2025-06-02 | [60928](https://github.com/airbytehq/airbyte/pull/60928) | Migrate `search_analytics_by_country`, `sites`, and `sitemaps` to low-code |
| 1.5.18 | 2025-05-28 | [58121](https://github.com/airbytehq/airbyte/pull/58121) | Prevent KeyError raise on check connetion when account does not have access to any site. Better Error message |
| 1.5.17 | 2025-05-10 | [54946](https://github.com/airbytehq/airbyte/pull/54946) | Update dependencies |
| 1.5.16 | 2025-05-09 | [59737](https://github.com/airbytehq/airbyte/pull/59737) | Promoting release candidate 1.5.16-rc.1 to a main version. |
| 1.5.16-rc.1 | 2025-05-02 | [59140](https://github.com/airbytehq/airbyte/pull/59140) | Migrate to CDK V6 |
| 1.5.15 | 2025-02-22 | [54426](https://github.com/airbytehq/airbyte/pull/54426) | Update dependencies |
| 1.5.14 | 2025-02-15 | [53781](https://github.com/airbytehq/airbyte/pull/53781) | Update dependencies |
| 1.5.13 | 2025-02-01 | [52854](https://github.com/airbytehq/airbyte/pull/52854) | Update dependencies |
| 1.5.12 | 2025-01-25 | [52303](https://github.com/airbytehq/airbyte/pull/52303) | Update dependencies |
| 1.5.11 | 2025-01-18 | [51629](https://github.com/airbytehq/airbyte/pull/51629) | Update dependencies |
| 1.5.10 | 2025-01-11 | [51129](https://github.com/airbytehq/airbyte/pull/51129) | Update dependencies |
| 1.5.9 | 2025-01-04 | [50919](https://github.com/airbytehq/airbyte/pull/50919) | Update dependencies |
| 1.5.8 | 2024-12-28 | [50579](https://github.com/airbytehq/airbyte/pull/50579) | Update dependencies |
| 1.5.7 | 2024-12-21 | [50040](https://github.com/airbytehq/airbyte/pull/50040) | Update dependencies |
| 1.5.6 | 2024-12-14 | [49173](https://github.com/airbytehq/airbyte/pull/49173) | Update dependencies |
| 1.5.5 | 2024-11-25 | [43730](https://github.com/airbytehq/airbyte/pull/43730) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 1.5.4 | 2024-09-06 | [45196](https://github.com/airbytehq/airbyte/pull/45196) | Fix request body for report streams by keyword |
| 1.5.3 | 2024-08-03 | [43067](https://github.com/airbytehq/airbyte/pull/43067) | Update dependencies |
| 1.5.2 | 2024-07-27 | [42786](https://github.com/airbytehq/airbyte/pull/42786) | Update dependencies |
| 1.5.1 | 2024-07-20 | [42142](https://github.com/airbytehq/airbyte/pull/42142) | Update dependencies |
| 1.5.0 | 2024-07-17 | [42073](https://github.com/airbytehq/airbyte/pull/42073) | Migrate to CDK v1.8.0 |
| 1.4.13 | 2024-07-13 | [41734](https://github.com/airbytehq/airbyte/pull/41734) | Update dependencies |
| 1.4.12 | 2024-07-10 | [41440](https://github.com/airbytehq/airbyte/pull/41440) | Update dependencies |
| 1.4.11 | 2024-07-09 | [41164](https://github.com/airbytehq/airbyte/pull/41164) | Update dependencies |
| 1.4.10 | 2024-07-06 | [40981](https://github.com/airbytehq/airbyte/pull/40981) | Update dependencies |
| 1.4.9 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 1.4.8 | 2024-06-26 | [40532](https://github.com/airbytehq/airbyte/pull/40532) | Update dependencies |
| 1.4.7 | 2024-06-25 | [40312](https://github.com/airbytehq/airbyte/pull/40312) | Update dependencies |
| 1.4.6 | 2024-06-22 | [40077](https://github.com/airbytehq/airbyte/pull/40077) | Update dependencies |
| 1.4.5 | 2024-06-17 | [39516](https://github.com/airbytehq/airbyte/pull/39516) | Update state handling for incremental streams |
| 1.4.4 | 2024-06-04 | [39059](https://github.com/airbytehq/airbyte/pull/39059) | [autopull] Upgrade base image to v1.2.1 |
| 1.4.3 | 2024-05-24 | [38649](https://github.com/airbytehq/airbyte/pull/38649) | Update deprecated auth package |
| 1.4.2 | 2024-04-19 | [36639](https://github.com/airbytehq/airbyte/pull/36639) | Updating to 0.80.0 CDK |
| 1.4.1 | 2024-04-12 | [36639](https://github.com/airbytehq/airbyte/pull/36639) | Schema descriptions |
| 1.4.0 | 2024-03-19 | [36267](https://github.com/airbytehq/airbyte/pull/36267) | Pin airbyte-cdk version to `^0` |
| 1.3.7 | 2024-02-12 | [35163](https://github.com/airbytehq/airbyte/pull/35163) | Manage dependencies with Poetry |
| 1.3.6 | 2023-10-26 | [31863](https://github.com/airbytehq/airbyte/pull/31863) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 1.3.5 | 2023-09-28 | [30822](https://github.com/airbytehq/airbyte/pull/30822) | Fix primary key for custom reports |
| 1.3.4 | 2023-09-27 | [30785](https://github.com/airbytehq/airbyte/pull/30785) | Do not migrate config for the newly created connections |
| 1.3.3 | 2023-08-29 | [29941](https://github.com/airbytehq/airbyte/pull/29941) | Added `primary key` to each stream, added `custom_report` config migration |
| 1.3.2 | 2023-08-25 | [29829](https://github.com/airbytehq/airbyte/pull/29829) | Make `Start Date` a non-required, added the `suggested streams`, corrected public docs |
| 1.3.1 | 2023-08-24 | [29329](https://github.com/airbytehq/airbyte/pull/29329) | Update tooltip descriptions |
| 1.3.0 | 2023-08-24 | [29750](https://github.com/airbytehq/airbyte/pull/29750) | Add new `Keyword-Site-Report-By-Site` stream |
| 1.2.2 | 2023-08-23 | [29741](https://github.com/airbytehq/airbyte/pull/29741) | Handle `HTTP-401`, `HTTP-403` errors |
| 1.2.1 | 2023-07-04 | [27952](https://github.com/airbytehq/airbyte/pull/27952) | Removed deprecated `searchType`, added `discover`(Discover results) and `googleNews`(Results from news.google.com, etc.) types |
| 1.2.0 | 2023-06-29 | [27831](https://github.com/airbytehq/airbyte/pull/27831) | Add new streams |
| 1.1.0 | 2023-06-26 | [27738](https://github.com/airbytehq/airbyte/pull/27738) | License Update: Elv2 |
| 1.0.2 | 2023-06-13 | [27307](https://github.com/airbytehq/airbyte/pull/27307) | Fix `data_state` config typo |
| 1.0.1 | 2023-05-30 | [26746](https://github.com/airbytehq/airbyte/pull/26746) | Remove `authSpecification` from connector spec in favour of advancedAuth |
| 1.0.0 | 2023-05-24 | [26452](https://github.com/airbytehq/airbyte/pull/26452) | Add data_state parameter to specification |
| 0.1.22 | 2023-03-20 | [22295](https://github.com/airbytehq/airbyte/pull/22295) | Update specification examples |
| 0.1.21 | 2023-02-14 | [22984](https://github.com/airbytehq/airbyte/pull/22984) | Specified date formatting in specification |
| 0.1.20 | 2023-02-02 | [22334](https://github.com/airbytehq/airbyte/pull/22334) | Turn on default HttpAvailabilityStrategy |
| 0.1.19 | 2023-01-27 | [22007](https://github.com/airbytehq/airbyte/pull/22007) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 0.1.18 | 2022-10-27 | [18568](https://github.com/airbytehq/airbyte/pull/18568) | Improved config validation: custom_reports.dimension |
| 0.1.17 | 2022-10-08 | [17751](https://github.com/airbytehq/airbyte/pull/17751) | Improved config validation: start_date, end_date, site_urls |
| 0.1.16 | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream state. |
| 0.1.15 | 2022-09-16 | [16819](https://github.com/airbytehq/airbyte/pull/16819) | Check available site urls to avoid 403 error on sync |
| 0.1.14 | 2022-09-08 | [16433](https://github.com/airbytehq/airbyte/pull/16433) | Add custom analytics stream. |
| 0.1.13 | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from specs |
| 0.1.12 | 2022-05-04 | [12482](https://github.com/airbytehq/airbyte/pull/12482) | Update input configuration copy |
| 0.1.11 | 2022-01-05 | [9186](https://github.com/airbytehq/airbyte/pull/9186) | Fix incremental sync: keep all urls in state object |
| 0.1.10 | 2021-12-23 | [9073](https://github.com/airbytehq/airbyte/pull/9073) | Add slicing by date range |
| 0.1.9 | 2021-12-22 | [9047](https://github.com/airbytehq/airbyte/pull/9047) | Add 'order' to spec.json props |
| 0.1.8 | 2021-12-21 | [8248](https://github.com/airbytehq/airbyte/pull/8248) | Enable Sentry for performance and errors tracking |
| 0.1.7 | 2021-11-26 | [7431](https://github.com/airbytehq/airbyte/pull/7431) | Add default `end_date` param value |
| 0.1.6 | 2021-09-27 | [6460](https://github.com/airbytehq/airbyte/pull/6460) | Update OAuth Spec File |
| 0.1.4 | 2021-09-23 | [6394](https://github.com/airbytehq/airbyte/pull/6394) | Update Doc link Spec File |
| 0.1.3 | 2021-09-23 | [6405](https://github.com/airbytehq/airbyte/pull/6405) | Correct Spec File |
| 0.1.2 | 2021-09-17 | [6222](https://github.com/airbytehq/airbyte/pull/6222) | Correct Spec File |
| 0.1.1 | 2021-09-22 | [6315](https://github.com/airbytehq/airbyte/pull/6315) | Verify access to all sites when performing connection check |
| 0.1.0 | 2021-09-03 | [5350](https://github.com/airbytehq/airbyte/pull/5350) | Initial Release |

</details>

</HideInUI>
