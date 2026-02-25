# Criteo Marketing

<HideInUI>

This page contains the setup guide and reference information for the [Criteo Marketing](https://developers.criteo.com/marketing-solutions/reference/) source connector.

</HideInUI>

## Prerequisites

- A [Criteo](https://www.criteo.com/) account with access to the [Criteo Partners Portal](https://partners.criteo.com/)
- A Criteo API application configured with client credentials authentication
- An OAuth **Client ID** and **Client Secret** generated from your Criteo API application

## Setup guide

### Step 1: Create a Criteo API application

1. Log in to the [Criteo Partners Portal](https://partners.criteo.com/).
2. Navigate to **My Apps** and click the **+** button to create a new application.
3. Provide a name and description for your application.
4. Select **Client Credentials** as the authentication method.
5. Select **C-Growth** as the service (for Marketing Solutions).
6. Select the domains your application needs access to. At minimum, enable permissions for campaign analytics and ad set data.
7. Click **Activate app** to finalize the application setup.

### Step 2: Generate your API credentials

1. In your application's page on the Criteo Partners Portal, click **Create new key**.
2. A text file containing your **Client ID** and **Client Secret** downloads automatically. Store these credentials securely, as the Client Secret is only available at the time of creation.

### Step 3: Set up the connector in Airbyte

<FieldAnchor field="client_id">

1. Enter the **OAuth Client ID** from the credentials you generated in Step 2.

</FieldAnchor>

<FieldAnchor field="client_secret">

2. Enter the **OAuth Client Secret** from the credentials you generated in Step 2.

</FieldAnchor>

<FieldAnchor field="start_date">

3. Enter a **Start Date** in `YYYY-MM-DD` format. The connector replicates data from this date onward.

</FieldAnchor>

<FieldAnchor field="end_date">

4. (Optional) Enter an **End Date** in `YYYY-MM-DD` format. If not set, the connector syncs data up to the current date.

</FieldAnchor>

<FieldAnchor field="currency">

5. Enter a **Currency** code in [ISO 4217](https://en.wikipedia.org/wiki/ISO_4217) format (for example, `USD`, `EUR`, `GBP`). This currency is used for the cost data in the `ad_spend_daily` report.

</FieldAnchor>

6. Click **Set up source** and wait for the connection test to complete.

<HideInUI>

## Supported sync modes

The Criteo Marketing source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported streams

| Stream | Primary Key | Incremental | API Endpoint |
|:-------|:------------|:------------|:-------------|
| ad_spend_daily | AdvertiserId, CampaignId, Day | Yes | [Statistics Report](https://developers.criteo.com/marketing-solutions/reference/getadsetreport) |
| adsets | id | No | [Ad Sets Search](https://developers.criteo.com/marketing-solutions/docs/ad-set) |

### ad_spend_daily

Reports daily advertiser cost data, broken down by advertiser, campaign, and ad set. This stream uses the Criteo Statistics API and reports the `AdvertiserCost` metric. It supports incremental sync with a cursor on the `Day` field and applies a 3-day lookback window to capture late-arriving data corrections.

### adsets

Returns the configuration details for all ad sets in your Criteo account, including name, campaign association, targeting settings, budget, bidding strategy, and schedule. This stream supports full refresh sync only.

## Performance considerations

The Criteo Marketing API enforces a rate limit of 250 requests per minute. The connector handles rate limiting automatically with exponential backoff and retries up to 5 times.

The Statistics API has a maximum of 100,000 rows per request. If your account generates a high volume of data, you may need to use a narrower date range.

</HideInUI>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|:--------|:-----|:-------------|:--------|
| 0.0.1 | 2026-02-25 | [72827](https://github.com/airbytehq/airbyte/pull/72827) | Initial release by [@mvfc](https://github.com/mvfc) via Connector Builder |

</details>
