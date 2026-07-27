# MNTN

MNTN is a connected TV advertising platform that lets brands create and launch TV commercials on shows, movies, and live sports.

This source reads campaign, creative, and advertiser reporting data from MNTN's Reporting API (API 3.0) at `https://api3.mountain.com/apidata`.

## Prerequisites

- An MNTN account with API access
- An MNTN API key

## Set up the MNTN source connector

### Step 1: Get your API key

1. Sign in to MNTN.
2. Click the account menu in the upper-right corner, then click **My Account**.
3. Under **MY ACCOUNT** in the left navigation, click **API**.
4. Click **Copy**.

Every user on your MNTN account can see this key, and the connector sends it as a query parameter (`key`) on each request. Treat it like a password. For more details, see MNTN's [Access Your API Key](https://help.mountain.com/en/articles/6511970-access-your-api-key).

### Step 2: Configure the source

Set the API key you copied, then choose a start date. The start date is the earliest day of reporting data the connector requests, in `YYYY-MM-DD` format. Choose the most recent date that covers your reporting needs. Incremental streams request one day of data per API call, so an early start date means a long first sync.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_time` | `string` | start_time.  | 2023-01-01 |

## Streams

`CampaignDetails` and `CreativeDetails` return the configuration of your campaigns and creatives. The other three streams return daily performance metrics — impressions, spend, visits, conversions, order value, ROAS, and their last-touch equivalents — aggregated at different levels.

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| CampaignDetails | ID | No pagination | ✅ |  ❌  |
| CreativeDetails | ID.Day | No pagination | ✅ |  ✅  |
| Campaign | ID.Day | No pagination | ✅ |  ✅  |
| Creative | ID.Day | No pagination | ✅ |  ✅  |
| Advertiser | ID.Day | No pagination | ✅ |  ✅  |

- **CampaignDetails**: Name, status, budget, flight dates, and goal for each campaign. This stream has no date dimension, so it's full refresh only and always requests the full window from your start date through today.
- **CreativeDetails**: Name, creative group, template, click URL, and active flag for each creative, reported by day.
- **Campaign**, **Creative**, **Advertiser**: Daily performance metrics for each campaign, creative, or advertiser.

The incremental streams use `Day` as the cursor and sync one day per request.

## Limitations and known issues

- Every field, including metrics such as `Spend` and `Impressions`, arrives as a string. Cast these values downstream before you aggregate them.
- The connector uses MNTN's synchronous reporting endpoint. MNTN recommends its asynchronous batch endpoint for high-cardinality requests and for windows longer than four months, so a `CampaignDetails` sync with an early start date can time out.
- MNTN doesn't publish rate limits for the reporting API.
- MNTN's API doesn't paginate these responses, so each request returns the full result set for its date range.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-07-27 | [81334](https://github.com/airbytehq/airbyte/pull/81334) | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
