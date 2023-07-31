# Paypal Transaction

This page contains the setup guide and reference information for the Paypal Transaction source connector.

## Prerequisites

The [Paypal Transaction API](https://developer.paypal.com/docs/api/transaction-search/v1/) is used to get the history of transactions for a PayPal account.

## Setup guide
### Step 1: Set up Paypal Transaction

In order to get an `Client ID` and `Secret` please go to [this](https://developer.paypal.com/docs/platforms/get-started/) page and follow the instructions. After registration you may find your `Client ID` and `Secret` [here](https://developer.paypal.com/developer/accounts/).

:::note

Our Paypal Transactions Source Connector does not support OAuth at this time due to limitations outside of our control. If OAuth for Paypal Transactions is critical to your business, [please reach out to us](mailto:product@airbyte.io) to discuss how we may be able to partner on this effort.

:::

## Step 2: Set up the Paypal Transaction connector in Airbyte

<!-- env:cloud -->
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Paypal Transaction connector and select **Paypal Transaction** from the Source type dropdown.
4. Enter your client id
5. Enter your secret
6. Choose if your account is sandbox
7. Enter the date you want your sync to start from
8. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard
2. Set the name for your source
3. Enter your client id
4. Enter your secret
5. Choose if your account is sandbox
6. Enter the date you want your sync to start from
7. Click **Set up source**
<!-- /env:oss -->

## Supported sync modes

The PayPal Transaction source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         |    Yes     |
| Incremental - Append Sync |    Yes     |
| Namespaces                |     No     |

## Supported Streams

This Source is capable of syncing the following core Streams:

* [Transactions](https://developer.paypal.com/docs/api/transaction-search/v1/#transactions)
* [Balances](https://developer.paypal.com/docs/api/transaction-search/v1/#balances)

## Performance considerations

Paypal transaction API has some [limits](https://developer.paypal.com/docs/integration/direct/transaction-search/)

* `start_date_min` = 3 years, API call lists transaction for the previous three years.
* `start_date_max` = 1.5 days, it takes a maximum of three hours for executed transactions to appear in the list transactions call. It is set to 1.5 days by default based on experience, otherwise API throw an error.
* `stream_slice_period` = 1 day, the maximum supported date range is 31 days.
* `records_per_request` = 10000, the maximum number of records in a single request.
* `page_size` = 500, the maximum page size is 500.
* `requests_per_minute` = 30, maximum limit is 50 requests per minute from IP address to all endpoint

Transactions sync is performed with default `stream_slice_period` = 1 day, it means that there will be 1 request for each day between start_date and now or end_date. if `start_date` is greater then `start_date_max`. Balances sync is similarly performed with default `stream_slice_period` = 1 day, but it will do additional request for the end_date of the sync now.

## Data type map

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
|     `string`     |   `string`   |
|     `number`     |   `number`   |
|     `array`      |   `array`    |
|     `object`     |   `object`   |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                      |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------|
| 2.0.0   | 2023-07-05 | [27916](https://github.com/airbytehq/airbyte/pull/27916) | Update `Balances` schema                                                                                                     |
| 1.0.0   | 2023-07-03 | [27968](https://github.com/airbytehq/airbyte/pull/27968) | mark `Client ID` and `Client Secret` as required fields                                                                      |
| 0.1.13  | 2023-02-20 | [22916](https://github.com/airbytehq/airbyte/pull/22916) | Specified date formatting in specification                                                                                   |
| 0.1.12  | 2023-02-18 | [23211](https://github.com/airbytehq/airbyte/pull/23211) | Fix error handler                                                                                                            |
| 0.1.11  | 2023-01-27 | [22019](https://github.com/airbytehq/airbyte/pull/22019) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                                  |
| 0.1.10  | 2022-09-04 | [17554](https://github.com/airbytehq/airbyte/pull/17554) | Made the spec and source config to be consistent                                                                             |
| 0.1.9   | 2022-08-18 | [15741](https://github.com/airbytehq/airbyte/pull/15741) | Removed `OAuth2.0` option                                                                                                    |
| 0.1.8   | 2022-07-25 | [15000](https://github.com/airbytehq/airbyte/pull/15000) | Added support of `OAuth2.0` authentication, fixed bug when normalization couldn't handle nested cursor field and primary key |
| 0.1.7   | 2022-07-18 | [14804](https://github.com/airbytehq/airbyte/pull/14804) | Added `RESULTSET_TOO_LARGE` error validation                                                                                 |
| 0.1.6   | 2022-06-10 | [13682](https://github.com/airbytehq/airbyte/pull/13682) | Updated paypal transaction schema                                                                                            |
| 0.1.5   | 2022-04-27 | [12335](https://github.com/airbytehq/airbyte/pull/12335) | Added fixtures to mock time.sleep for connectors that explicitly sleep                                                       |
| 0.1.4   | 2021-12-22 | [9034](https://github.com/airbytehq/airbyte/pull/9034)   | Updated connector fields title/description                                                                                   |
| 0.1.3   | 2021-12-16 | [8580](https://github.com/airbytehq/airbyte/pull/8580)   | Added more logs during `check connection` stage                                                                              |
| 0.1.2   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Removed base-python dependencies                                                                                             |
| 0.1.1   | 2021-08-03 | [5155](https://github.com/airbytehq/airbyte/pull/5155)   | Fixed start_date_min limit                                                                                                   |
| 0.1.0   | 2021-06-10 | [4240](https://github.com/airbytehq/airbyte/pull/4240)   | PayPal Transaction Search API                                                                                                |
