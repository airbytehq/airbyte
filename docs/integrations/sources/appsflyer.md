# AppsFlyer

<HideInUI>

This page contains the setup guide and reference information for the [AppsFlyer](https://www.appsflyer.com/) source connector.

</HideInUI>

## Prerequisites

- An AppsFlyer account
- An AppsFlyer [API V2 token](https://support.appsflyer.com/hc/en-us/articles/360004562377-Managing-AppsFlyer-tokens). Only account admins can view and manage API tokens.
- Your AppsFlyer App ID

## Setup guide

### Step 1: Obtain your API token

1. In the AppsFlyer dashboard, open the account menu and go to **Security center**.
2. In the **AppsFlyer API tokens** section, click **Manage your AppsFlyer API tokens**.
3. Copy an existing API V2 token, or click **+ New token** to create one.

For more details, see AppsFlyer's [token management documentation](https://support.appsflyer.com/hc/en-us/articles/360004562377-Managing-AppsFlyer-tokens).

### Step 2: Find your App ID

Your App ID is the app identifier as registered in AppsFlyer. You can find it in the AppsFlyer dashboard URL or in your app's settings page.

### Step 3: Set up the connector in Airbyte

1. Enter your **App ID**.
2. Enter your **API Token**.
3. Enter a **Start Date** in `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS` format. Raw data reports are limited to the last 90 days; if your start date is more than 90 days ago, the connector automatically adjusts it to 90 days before the current date.
4. Optionally, set the **Timezone**. This controls the timezone for date parameters in API requests. Defaults to `UTC`. Use the timezone configured in your AppsFlyer app settings to align data with the AppsFlyer dashboard.

## Supported sync modes

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |

## Supported streams

All streams support incremental sync based on a date cursor.

### Raw data streams (non-organic)

| Stream              | Cursor Field   | Description |
| :------------------ | :------------- | :---------- |
| Installs            | `install_time` | Non-organic installs. Updated in real time. |
| In-App Events       | `event_time`   | In-app events performed by users. Updated in real time. |
| Uninstall Events    | `event_time`   | App uninstalls. Updated daily. |

### Raw data streams (organic)

| Stream                    | Cursor Field   | Description |
| :------------------------ | :------------- | :---------- |
| Organic Installs          | `install_time` | Organic installs. Updated continuously. |
| Organic In-App Events     | `event_time`   | Organic in-app events. Updated continuously. |
| Organic Uninstall Events  | `event_time`   | Organic app uninstalls. Updated daily. |

### Raw data streams (retargeting)

| Stream                     | Cursor Field   | Description |
| :------------------------- | :------------- | :---------- |
| Retargeting In-App Events  | `event_time`   | In-app events from retargeting campaigns. Updated in real time. |
| Retargeting Installs       | `install_time` | Conversions from retargeting campaigns. Updated in real time. |

### Aggregate report streams

| Stream                              | Cursor Field | Description |
| :---------------------------------- | :----------- | :---------- |
| Daily Report                        | `date`       | Daily performance metrics. |
| Partners Report                     | `date`       | Performance metrics by media source. |
| Geo Report                          | `date`       | Performance metrics by geography. |
| Geo Events Report                   | `date`       | In-app event metrics by geography. |
| Partners Events Report              | `date`       | In-app event metrics by media source. |

### Aggregate retargeting report streams

| Stream                                | Cursor Field | Description |
| :------------------------------------ | :----------- | :---------- |
| Retargeting Daily Report              | `date`       | Retargeting daily performance metrics. |
| Retargeting Partners Report           | `date`       | Retargeting metrics by media source. |
| Retargeting Geo Report                | `date`       | Retargeting metrics by geography. |
| Retargeting Geo Events Report         | `date`       | Retargeting event metrics by geography. |
| Retargeting Partners Events Report    | `date`       | Retargeting event metrics by media source. |

### Unsupported report categories

The following AppsFlyer Pull API report categories aren't supported by this connector:

- Raw data reinstall reports (organic and non-organic)
- Ad revenue reports
- Postback reports
- Protect360 fraud reports

## Limitations and troubleshooting

- **90-day limit for raw data**: The AppsFlyer Pull API limits raw data report requests to the last 90 days. The connector enforces this automatically.
- **1,000,000 row maximum per request**: Each API request returns a maximum of 1,000,000 rows. If a report exceeds this limit, the response is truncated.
- **Rate limits**: AppsFlyer applies daily rate limits per report type, per app, and per account. For aggregate reports with a date range of 2 days or fewer, the limit is 1 request per minute per app. For raw data reports, limits vary by subscription plan. See [AppsFlyer's rate limit documentation](https://support.appsflyer.com/hc/en-us/articles/207034366-Report-generation-quotas-rate-limitations) for details.
- **Currency**: Raw data streams use the currency configured in your AppsFlyer app settings (`preferred` currency mode).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                           | Subject                                     |
| :------ | :--------- | :----------------------------------------------------- | :------------------------------------------ |
| 0.3.0 | 2026-04-29 | [77123](https://github.com/airbytehq/airbyte/pull/77123) | Migrate to airbyte-cdk 7.x and update base image |
| 0.2.40 | 2025-05-17 | [60656](https://github.com/airbytehq/airbyte/pull/60656) | Update dependencies |
| 0.2.39 | 2025-05-10 | [59774](https://github.com/airbytehq/airbyte/pull/59774) | Update dependencies |
| 0.2.38 | 2025-05-03 | [59359](https://github.com/airbytehq/airbyte/pull/59359) | Update dependencies |
| 0.2.37 | 2025-04-26 | [58748](https://github.com/airbytehq/airbyte/pull/58748) | Update dependencies |
| 0.2.36 | 2025-04-19 | [58244](https://github.com/airbytehq/airbyte/pull/58244) | Update dependencies |
| 0.2.35 | 2025-04-12 | [57618](https://github.com/airbytehq/airbyte/pull/57618) | Update dependencies |
| 0.2.34 | 2025-04-05 | [57111](https://github.com/airbytehq/airbyte/pull/57111) | Update dependencies |
| 0.2.33 | 2025-03-29 | [56605](https://github.com/airbytehq/airbyte/pull/56605) | Update dependencies |
| 0.2.32 | 2025-03-22 | [56154](https://github.com/airbytehq/airbyte/pull/56154) | Update dependencies |
| 0.2.31 | 2025-03-08 | [55380](https://github.com/airbytehq/airbyte/pull/55380) | Update dependencies |
| 0.2.30 | 2025-03-01 | [54869](https://github.com/airbytehq/airbyte/pull/54869) | Update dependencies |
| 0.2.29 | 2025-02-22 | [54228](https://github.com/airbytehq/airbyte/pull/54228) | Update dependencies |
| 0.2.28 | 2025-02-15 | [53895](https://github.com/airbytehq/airbyte/pull/53895) | Update dependencies |
| 0.2.27 | 2025-02-01 | [52901](https://github.com/airbytehq/airbyte/pull/52901) | Update dependencies |
| 0.2.26 | 2025-01-25 | [51286](https://github.com/airbytehq/airbyte/pull/51286) | Update dependencies |
| 0.2.25 | 2024-12-28 | [50438](https://github.com/airbytehq/airbyte/pull/50438) | Update dependencies |
| 0.2.24 | 2024-12-21 | [50173](https://github.com/airbytehq/airbyte/pull/50173) | Update dependencies |
| 0.2.23 | 2024-12-14 | [49296](https://github.com/airbytehq/airbyte/pull/49296) | Update dependencies |
| 0.2.22 | 2024-11-25 | [48652](https://github.com/airbytehq/airbyte/pull/48652) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.21 | 2024-10-29 | [47039](https://github.com/airbytehq/airbyte/pull/47039) | Update dependencies |
| 0.2.20 | 2024-10-12 | [46823](https://github.com/airbytehq/airbyte/pull/46823) | Update dependencies |
| 0.2.19 | 2024-10-05 | [46393](https://github.com/airbytehq/airbyte/pull/46393) | Update dependencies |
| 0.2.18 | 2024-09-28 | [46202](https://github.com/airbytehq/airbyte/pull/46202) | Update dependencies |
| 0.2.17 | 2024-09-21 | [45746](https://github.com/airbytehq/airbyte/pull/45746) | Update dependencies |
| 0.2.16 | 2024-09-14 | [45510](https://github.com/airbytehq/airbyte/pull/45510) | Update dependencies |
| 0.2.15 | 2024-09-07 | [45234](https://github.com/airbytehq/airbyte/pull/45234) | Update dependencies |
| 0.2.14 | 2024-08-31 | [44956](https://github.com/airbytehq/airbyte/pull/44956) | Update dependencies |
| 0.2.13 | 2024-08-24 | [44633](https://github.com/airbytehq/airbyte/pull/44633) | Update dependencies |
| 0.2.12 | 2024-08-17 | [44226](https://github.com/airbytehq/airbyte/pull/44226) | Update dependencies |
| 0.2.11 | 2024-08-10 | [43572](https://github.com/airbytehq/airbyte/pull/43572) | Update dependencies |
| 0.2.10 | 2024-08-03 | [43229](https://github.com/airbytehq/airbyte/pull/43229) | Update dependencies |
| 0.2.9 | 2024-07-27 | [42681](https://github.com/airbytehq/airbyte/pull/42681) | Update dependencies |
| 0.2.8 | 2024-07-20 | [42322](https://github.com/airbytehq/airbyte/pull/42322) | Update dependencies |
| 0.2.7 | 2024-07-13 | [41831](https://github.com/airbytehq/airbyte/pull/41831) | Update dependencies |
| 0.2.6 | 2024-07-10 | [41600](https://github.com/airbytehq/airbyte/pull/41600) | Update dependencies |
| 0.2.5 | 2024-07-09 | [41146](https://github.com/airbytehq/airbyte/pull/41146) | Update dependencies |
| 0.2.4 | 2024-07-06 | [40766](https://github.com/airbytehq/airbyte/pull/40766) | Update dependencies |
| 0.2.3 | 2024-06-25 | [40476](https://github.com/airbytehq/airbyte/pull/40476) | Update dependencies |
| 0.2.2 | 2024-06-22 | [40059](https://github.com/airbytehq/airbyte/pull/40059) | Update dependencies |
| 0.2.1 | 2024-06-11 | [39407](https://github.com/airbytehq/airbyte/pull/39407) | Fix Organic In-App Events Stream |
| 0.2.0 | 2024-05-19 | [38339](https://github.com/airbytehq/airbyte/pull/38339) | Migrate to [AppsFlyer API V2](https://support.appsflyer.com/hc/en-us/articles/12399683708305-Bulletin-API-token-changes?query=token) |
| 0.1.2 | 2024-06-06 | [39187](https://github.com/airbytehq/airbyte/pull/39187) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38436](https://github.com/airbytehq/airbyte/pull/38436) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2021-03-22 | [2544](https://github.com/airbytehq/airbyte/pull/2544) | Adding the appsflyer singer based connector |

</details>
