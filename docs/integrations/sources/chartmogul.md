# Chartmogul

This page contains the setup guide and reference information for the [Chartmogul](https://chartmogul.com/) source connector.

## Prerequisites

- A Chartmogul API Key.
- A desired start date from which to begin replicating data.

## Setup guide

### Step 1: Set up a Chartmogul API key

1. Log in to your Chartmogul account.
2. In the left navbar, select **Profile** > **View Profile**.
3. Select **NEW API KEY**.
4. In the **Name** field, enter a unique name for the key.
5. If you are a Staff, Admin, or Owner, set the **Access Level** to either **Read-only** or **Read & Write** using the dropdown menu. We recommend **Read-only**.
6. Click **ADD** to create the key.
7. Click the **Reveal** icon to see the key, and the **Copy** icon to copy it to your clipboard.

For further reading on Chartmogul API Key creation and maintenance, please refer to the official
[Chartmogul documentation](https://help.chartmogul.com/hc/en-us/articles/4407796325906-Creating-and-Managing-API-keys#creating-an-api-key).

### Step 2: Set up the Chartmogul connector in Airbyte

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account, or navigate to the Airbyte Open Source dashboard.
2. From the Airbyte UI, click **Sources**, then click on **+ New Source** and select **Chartmogul** from the list of available sources.
3. Enter a **Source name** of your choosing.
4. Enter the **API key** that you obtained.
5. Enter a **Start date**. If you are configuring this connector programmatically, please format the date as such: `yyyy-mm-ddThh:mm:ssZ`. For example, an input of `2017-01-25T06:30:00Z` will signify a start date of 6:30 AM UTC on January 25th, 2017. When feasible, any data before this date will not be replicated.

:::note
The **Start date** will only apply to the `Activities` stream. The `Customers` endpoint does not provide a way to filter by the creation or update dates.
:::

6. Click **Set up source** and wait for the tests to complete.

## Supported sync modes

The Chartmogul source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

## Supported streams

This connector outputs the following full refresh streams:

- [Activities](https://dev.chartmogul.com/reference/list-activities)
- [CustomerCountDaily](https://dev.chartmogul.com/reference/retrieve-customer-count)
- [CustomerCountWeekly](https://dev.chartmogul.com/reference/retrieve-customer-count)
- [CustomerCountMonthly](https://dev.chartmogul.com/reference/retrieve-customer-count)
- [CustomerCountQuarterly](https://dev.chartmogul.com/reference/retrieve-customer-count)
- [Customers](https://dev.chartmogul.com/reference/list-customers)

## Performance considerations

The Chartmogul connector should not run into Chartmogul API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                          |
|:--------|:-----------| :------------------------------------------------------- |:---------------------------------------------------------------------------------------------------------------------------------|
| 1.1.11 | 2025-02-15 | [53932](https://github.com/airbytehq/airbyte/pull/53932) | Update dependencies |
| 1.1.10 | 2025-02-08 | [53411](https://github.com/airbytehq/airbyte/pull/53411) | Update dependencies |
| 1.1.9 | 2025-02-01 | [52933](https://github.com/airbytehq/airbyte/pull/52933) | Update dependencies |
| 1.1.8 | 2025-01-25 | [52202](https://github.com/airbytehq/airbyte/pull/52202) | Update dependencies |
| 1.1.7 | 2025-01-18 | [51709](https://github.com/airbytehq/airbyte/pull/51709) | Update dependencies |
| 1.1.6 | 2025-01-11 | [51276](https://github.com/airbytehq/airbyte/pull/51276) | Update dependencies |
| 1.1.5 | 2024-12-28 | [50503](https://github.com/airbytehq/airbyte/pull/50503) | Update dependencies |
| 1.1.4 | 2024-12-21 | [50210](https://github.com/airbytehq/airbyte/pull/50210) | Update dependencies |
| 1.1.3 | 2024-12-14 | [49563](https://github.com/airbytehq/airbyte/pull/49563) | Update dependencies |
| 1.1.2 | 2024-12-12 | [48951](https://github.com/airbytehq/airbyte/pull/48951) | Update dependencies |
| 1.1.1 | 2024-10-28 | [47637](https://github.com/airbytehq/airbyte/pull/47637) | Update dependencies |
| 1.1.0 | 2024-08-19 | [44418](https://github.com/airbytehq/airbyte/pull/44418) | Refactor connector to manifest-only format |
| 1.0.13 | 2024-08-17 | [44342](https://github.com/airbytehq/airbyte/pull/44342) | Update dependencies |
| 1.0.12 | 2024-08-12 | [43847](https://github.com/airbytehq/airbyte/pull/43847) | Update dependencies |
| 1.0.11 | 2024-08-10 | [43660](https://github.com/airbytehq/airbyte/pull/43660) | Update dependencies |
| 1.0.10 | 2024-08-03 | [43231](https://github.com/airbytehq/airbyte/pull/43231) | Update dependencies |
| 1.0.9 | 2024-07-27 | [42589](https://github.com/airbytehq/airbyte/pull/42589) | Update dependencies |
| 1.0.8 | 2024-07-20 | [42349](https://github.com/airbytehq/airbyte/pull/42349) | Update dependencies |
| 1.0.7 | 2024-07-13 | [41854](https://github.com/airbytehq/airbyte/pull/41854) | Update dependencies |
| 1.0.6 | 2024-07-10 | [41259](https://github.com/airbytehq/airbyte/pull/41259) | Update dependencies |
| 1.0.5 | 2024-07-06 | [40963](https://github.com/airbytehq/airbyte/pull/40963) | Update dependencies |
| 1.0.4 | 2024-06-25 | [40448](https://github.com/airbytehq/airbyte/pull/40448) | Update dependencies |
| 1.0.3 | 2024-06-21 | [39932](https://github.com/airbytehq/airbyte/pull/39932) | Update dependencies |
| 1.0.2 | 2024-06-06 | [39289](https://github.com/airbytehq/airbyte/pull/39289) | [autopull] Upgrade base image to v1.2.2 |
| 1.0.1 | 2024-05-14 | [38145](https://github.com/airbytehq/airbyte/pull/38145) | Make connector compatible with builder |
| 1.0.0 | 2023-11-09 | [23075](https://github.com/airbytehq/airbyte/pull/23075) | Refactor CustomerCount stream into CustomerCountDaily, CustomerCountWeekly, CustomerCountMonthly, CustomerCountQuarterly Streams |
| 0.2.1 | 2023-02-15 | [23075](https://github.com/airbytehq/airbyte/pull/23075) | Specified date formatting in specification |
| 0.2.0 | 2022-11-15 | [19276](https://github.com/airbytehq/airbyte/pull/19276) | Migrate connector from Alpha (Python) to Beta (YAML) |
| 0.1.1 | 2022-03-02 | [10756](https://github.com/airbytehq/airbyte/pull/10756) | Add new stream: customer-count |
| 0.1.0 | 2022-01-10 | [9381](https://github.com/airbytehq/airbyte/pull/9381) | New Source: Chartmogul |

</details>
