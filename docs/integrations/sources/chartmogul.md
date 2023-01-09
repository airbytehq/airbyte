# Chartmogul
This page contains the setup guide and reference information for the Chartmogul source connector.

## Prerequisites
* API key
* Start date
* Interval

## Setup guide
### Step 1: Set up Chartmogul

1. To get access to the Chartmogul API you need to create an API key, please follow the instructions in this [documentation](https://help.chartmogul.com/hc/en-us/articles/4407796325906-Creating-and-Managing-API-keys#creating-an-api-key).

### Step 2: Set up the Chartmogul connector in Airbyte
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Chartmogul** from the Source type dropdown and enter a name for this connector.
4. Enter the **API key** that you obtained.
5. Enter **Start date** - UTC date and time in the format 2017-01-25T00:00:00Z. The data added on and after this date will be replicated.
6. Enter the **Interval** - day, week, month, quarter for `CustomerCount` stream.

## Supported sync modes

The Chartmogul source connector supports the following [ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

## Supported Streams

This connector outputs the following full refresh streams:

* [Activities](https://dev.chartmogul.com/reference/list-activities)
* [CustomerCount](https://dev.chartmogul.com/reference/retrieve-customer-count)
* [Customers](https://dev.chartmogul.com/reference/list-customers)

### Notes

The **Start date** will only apply to the `Activities` stream. The `Customers` endpoint does not provide a way to filter by the creation or update dates.

### Performance considerations

The Chartmogul connector should not run into Chartmogul API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.2.0 | 2022-11-15 | [19276](https://github.com/airbytehq/airbyte/pull/19276) | Migrate connector from Alpha (Python) to Beta (YAML) |
| 0.1.1 | 2022-03-02 | [10756](https://github.com/airbytehq/airbyte/pull/10756) | Add new stream: customer-count |
| 0.1.0 | 2022-01-10 | [9381](https://github.com/airbytehq/airbyte/pull/9381) | New Source: Chartmogul |
