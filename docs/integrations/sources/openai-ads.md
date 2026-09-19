# OpenAI Ads

This page contains the setup guide and reference information for the OpenAI Ads source connector.

## Prerequisites

- An [OpenAI Ads](https://ads.openai.com/) advertiser account
- An Advertiser API key for that account

## Setup guide

### Set up OpenAI Ads

#### Step 1: Create an API key

1. Log in to [Ads Manager](https://ads.openai.com/) with a user that has access to the ad account.
2. Open **Settings** and create a new API key.
3. Copy the key. Each key is scoped to one ad account. To replicate several ad accounts, create one key per account and set up one source per account.

The `spend_limit_windows` stream requires a key created by an ad account admin. With any other key it returns no records and the sync continues.

For more information, see [OpenAI's quickstart](https://developers.openai.com/ads/api-quickstart).

### Step 2: Set up the OpenAI Ads connector in Airbyte

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **OpenAI Ads** from the Source type dropdown.
4. Enter a name for the OpenAI Ads connector.
5. Enter the **API Key**.
6. (Optional) Enter the **Start Date** in YYYY-MM-DD format. Data before this date will not be replicated. The default is 2026-02-01, when ads in ChatGPT launched; there is no data before that.
7. (Optional) Enter the **End Date** in YYYY-MM-DD format. Data after this date will not be replicated. If not set, data is synced through today.
8. (Optional) Enter the **Lookback Window** in days. Set it to the longest `attribution_window_days` among your conversion event settings. OpenAI's API docs prescribe 30 for that field, which is the default.
9. (Optional) Enter the **Number of concurrent workers**. The default is 3.
10. Click **Set up source**.

#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **OpenAI Ads** from the Source type dropdown.
4. Enter a name for the OpenAI Ads connector.
5. Fill in the fields as described for Airbyte Cloud above.
6. Click **Set up source**.

## Supported sync modes

The OpenAI Ads source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

### Main Tables

| Stream                                                                                        | Primary key | Sync modes   | Notes                                                           |
| :-------------------------------------------------------------------------------------------- | :---------- | :----------- | :-------------------------------------------------------------- |
| [ad_account](https://developers.openai.com/ads/api-reference/ad-account)                      | id          | Full Refresh | The ad account the key belongs to                               |
| [campaigns](https://developers.openai.com/ads/api-reference/campaigns)                        | id          | Full Refresh |                                                                 |
| [ad_groups](https://developers.openai.com/ads/api-reference/ad-groups)                        | id          | Full Refresh | Listed per campaign, `campaign_id` added to each record         |
| [ads](https://developers.openai.com/ads/api-reference/ads)                                    | id          | Full Refresh | Listed per ad group, `ad_group_id` added to each record         |
| [conversion_event_settings](https://developers.openai.com/ads/api-reference/conversion-setup) | id          | Full Refresh | Conversion definitions of the account                           |
| [conversion_pixels](https://developers.openai.com/ads/api-reference/conversion-setup)         | id          | Full Refresh | Conversion data sources referenced by conversion_event_settings |
| custom_audiences                                                                              | id          | Full Refresh | Custom audiences of the account                                 |
| [spend_limit_windows](https://developers.openai.com/ads/api-reference/ad-account)             | window_id   | Full Refresh | Date range spend limits. Admin key required                     |

### Report Tables

All report tables are built on the [insights](https://developers.openai.com/ads/api-reference/insights) endpoint with daily granularity in the account timezone. Each row is one entity and one day. Field names follow the API's response keys.

| Stream                        | Primary key                                                  | Sync modes                | Level and breakdown                         |
| :---------------------------- | :----------------------------------------------------------- | :------------------------ | :------------------------------------------ |
| ad_account_insights           | ad_account_id, readable_time                                 | Full Refresh, Incremental | Ad account                                  |
| campaign_insights             | campaign_id, readable_time                                   | Full Refresh, Incremental | Campaign                                    |
| ad_group_insights             | ad_group_id, readable_time                                   | Full Refresh, Incremental | Ad group                                    |
| ad_insights                   | ad_id, readable_time                                         | Full Refresh, Incremental | Ad                                          |
| campaign_insights_by_country  | campaign_id, country_name, readable_time                     | Full Refresh, Incremental | Campaign by country                         |
| campaign_insights_by_device   | campaign_id, device_type, readable_time                      | Full Refresh, Incremental | Campaign by device type                     |
| campaign_insights_by_platform | campaign_id, platform, readable_time                         | Full Refresh, Incremental | Campaign by platform                        |
| campaign_insights_by_product  | campaign_id, product_feed_id, product_item_id, readable_time | Full Refresh, Incremental | Campaign by product feed item               |
| campaign_conversions          | entity_id, date                                              | Full Refresh, Incremental | Attributed conversions per campaign and day |
| ad_group_conversions          | entity_id, date                                              | Full Refresh, Incremental | Attributed conversions per ad group and day |
| ad_conversions                | entity_id, date                                              | Full Refresh, Incremental | Attributed conversions per ad and day       |

Every insights stream requests all attribute fields the API allows at its level, for its own entity and every level above it: account id, name, url and budgets; campaign id, name, description, status, start and end time and budgets; ad group id, name, description and status; ad id, name, title, copy, link, status and review status. Attributes that are unset for an entity are omitted from the row. The metrics are `impressions`, `clicks`, `spend`, `ctr`, `cpc`, `cpm`, with the same names at every level and for every segment. Days on which an entity had no impressions are not returned, so missing days mean zero delivery. The API's own row `id` is kept on the record but is not the primary key, because it embeds a query plan token that changes with the requested fields.

The conversions streams come from the [conversions insights](https://developers.openai.com/ads/api-reference/insights) endpoint and return `conversions`, `click_through_conversions` and `view_through_conversions` per entity (`entity_id`) and `date`, at campaign, ad group and ad level. Unlike the insights endpoint, this endpoint returns a row for every entity and every day of the requested range, zeros included, also for days before the entity was created. The connector keeps these rows as delivered, so each entity has a complete daily series from the start date. Set the Start Date to when the account began advertising to avoid rows for days before that; rows before an entity's own creation can be removed downstream with `created_at` from the `campaigns`, `ad_groups` and `ads` streams.

## Note on the Lookback Window

Conversions are attributed to the click that caused them for as long as the attribution window of the conversion event, so the conversions of a past day keep changing for that many days. Each conversion event setting carries its window in `attribution_window_days` (the `conversion_event_settings` stream shows them); OpenAI's API docs prescribe 30. On every sync, incremental report streams re-read the data inside the lookback window (default 30 days) and update those rows. Use the **Incremental | Append + Deduped** sync mode so the updated rows replace the earlier ones. Lower the window only if you sync delivery metrics without conversions and want fewer requests.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Performance considerations

The OpenAI Ads API allows 600 requests per minute per endpoint and 1,200 requests per minute overall. The connector keeps its own requests under 600 per minute, runs streams with the configured number of workers, and retries on 429 and 5xx responses with exponential backoff.

Insights are requested in 14 day slices with up to 2,000 rows per page and cursor pagination beyond that. The conversions endpoint does not paginate and fails with HTTP 500 above 2,000 rows per response, so the connector asks it for one entity and one 14 day slice at a time (at most 14 rows per request). This makes the conversions streams the most request-intensive part of the connector: each incremental sync issues about three requests per campaign, ad group and ad (a 30 day lookback covers three 14 day slices), and the first sync one request per entity for every 14 days between the start date and today. An account with 5,000 ads needs roughly 15,000 requests per incremental sync for `ad_conversions` alone, about 25 minutes at the rate limit, and writes one row per ad per day. If that is too much, deselect `ad_conversions` and `ad_group_conversions` and keep `campaign_conversions`, which needs three requests per campaign.

Amounts on insights rows (`spend`, `cpc`, `cpm`, and the budget columns such as `campaign_budget_daily`) are in the account currency. Fields ending in `_micros` on the entity and spend limit streams are in micros (1,000,000 micros equal one unit of currency). An `ad_account_budget_lifetime` of 1,000,000,000 means no lifetime limit is set.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                             |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------ |
| 0.1.0   | 2026-09-16 | [86351](https://github.com/airbytehq/airbyte/pull/86351) | Initial release by [@alexgreen496](https://github.com/alexgreen496) |

</details>
