# Paypal

This page contains the setup guide and reference information for the Paypal source connector.

This connector uses [PayPal APIs](https://developer.paypal.com/api/rest/authentication/) OAuth 2.0 access token to authenticate requests.

## Prerequisites

You will need a Paypal account, which you can get following [these steps](https://developer.paypal.com/docs/platforms/get-started/)

In the same page, you will also find how to setup a Sandbox so you can test the connector before using it in production.

## Setup guide

### Step 1: Get your Paypal secrets

After creating your account you will be able to get your `Client ID` and `Secret`. You can find them in your [Apps & Credentials page](https://developer.paypal.com/dashboard/applications/live).

### Step 2: Set up the Paypal Transaction connector in Airbyte

1. Log into your Airbyte account

   - For Cloud [Log in here](https://cloud.airbyte.com/workspaces).

2. In the left navigation bar, click **Sources**.

   a. If this is your first time creating a source, use the search bar and enter **Paypal Transaction** and select it.

   b. If you already have sources configured, go to the top-right corner and click **+new source**. Then enter **Paypal Transaction** in the searech bar and select the connector.

3. Set the name for your source
4. Enter your `Client ID`
5. Enter your `Client secret`
6. `Start Date`: Use the provided datepicker or enter manually a UTC date and time in the format `YYYY-MM-DDTHH:MM:SSZ`.
7. Switch ON/Off the Sandbox toggle. By defaukt the toggle is OFF, meaning it work only in a produciton environment.
8. \_(Optional) `Dispute Start Date Range`: Use the provided datepicker or enter manually a UTC date and time in the format `YYYY-MM-DDTHH:MM:SS.sssZ`. - If you don't add a date and you sync the `lists_disputes stream`, it will use the default value of 180 days in the past to retrieve data - It is mandatory to add the milliseconds is you enter a datetime. - This option only works for `lists_disputes stream`

9. _(Optional)`Refresh Token`:_ You can enter manually a refresh token. Right now the stream does this automatically.
10. _(Optional)`Number of days per request`:_ You can specify the days used by the connector when requesting data from the Paypal API. This helps in cases when you have a rate limit and you want to lower the window of retrieving data. - Paypal has a 10K record limit per request. This option is useful if your sync is every week and you have more than 10K per week - The default value is 7 - This Max value you can enter is 31 days
11. Click **Set up source**

:::info

By default, syncs are run with a slice period of 7 days. If you see errors with the message `Result set size is greater than the maximum limit` or an error code like `RESULTSET_TOO_LARGE`:

- Try lower the the size of the slice period in your optional parameters in your connection configuration.
- You can try to lower the scheduling sync window in case a day slice period is not enough. Lowering the sync period it may help avoid reaching the 10K limit.

:::

## Supported sync modes

The PayPal Transaction source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| Namespaces                | No         |

## Supported Streams

This Source is capable of syncing the following core Streams:

- [Transactions](https://developer.paypal.com/docs/api/transaction-search/v1/#transactions)
- [Balances](https://developer.paypal.com/docs/api/transaction-search/v1/#balances)
- [List Products](https://developer.paypal.com/docs/api/catalog-products/v1/#products_list)
- [Show Product Details](https://developer.paypal.com/docs/api/catalog-products/v1/#products_get)
- [List Disputes](https://developer.paypal.com/docs/api/customer-disputes/v1/#disputes_list)
- [Search Invoices](https://developer.paypal.com/docs/api/invoicing/v2/#invoices_search-invoices)
- [List Payments](https://developer.paypal.com/docs/api/payments/v1/#payment_list)

### Transactions Stream

The below table contains the configuraiton parameters available for this connector and the default values and available features

| **Param/Feature**            | `Transactions`            |
| :--------------------------- | :------------------------ |
| `Start Date`                 | Timestamp with TZ (no ms) |
| `Dispute Start Date Range`   | NA                        |
| `Refresh token`              | Auto                      |
| `Number of days per request` | Max 31 , 7(D)             |
| `Pagination Strategy`        | Page Increment            |
| `Page size `                 | Max 500 (F)               |
| `Full Refresh`               | :white_check_mark:        |
| `Incremental`                | :white_check_mark: (D)    |

**D:** Default configured Value

**F:** Fixed Value. This means it is not configurable.

---

### Balances Stream

The below table contains the configuraiton parameters available for this connector and the default values and available features

| **Param/Feature**            | `Balances`                |
| :--------------------------- | :------------------------ |
| `Start Date`                 | Timestamp with TZ (no ms) |
| `Dispute Start Date Range`   | NA                        |
| `Refresh token`              | Auto                      |
| `Number of days per request` | NA                        |
| `Pagination Strategy`        | NA                        |
| `Page size `                 | NA                        |
| `Full Refresh`               | :white_check_mark:        |
| `Incremental`                | :white_check_mark: (D)    |

**D:** Default configured Value

**F:** Fixed Value. This means it is not configurable.

---

### List Products Stream

The below table contains the configuraiton parameters available for this connector and the default values and available features

| **Param/Feature**            | `List Products`        |
| :--------------------------- | :--------------------- |
| `Start Date`                 | NA                     |
| `Dispute Start Date Range`   | NA                     |
| `Refresh token`              | Auto                   |
| `Number of days per request` | NA                     |
| `Pagination Strategy`        | Page Increment         |
| `Page size `                 | Max 20 (F)             |
| `Full Refresh`               | :white_check_mark: (D) |
| `Incremental`                | :x:                    |

**D:** Default configured Value

**F:** Fixed Value. This means it is not configurable.

:::caution

When configuring your stream take in consideration that the way the API works limits the speed on retreiving data. In some cases a +30K catalog retrieval could take between 10-15 minutes.

:::

---

### Show Products Stream

The below table contains the configuraiton parameters available for this connector and the default values and available features

| **Param/Feature**            | `Show Prod. Details`   |
| :--------------------------- | :--------------------- |
| `Start Date`                 | NA                     |
| `Dispute Start Date Range`   | NA                     |
| `Refresh token`              | Auto                   |
| `Number of days per request` | NA                     |
| `Pagination Strategy`        | NA                     |
| `Page size `                 | NA                     |
| `Full Refresh`               | :white_check_mark: (D) |
| `Incremental`                | :x:                    |

**D:** Default configured Value

**F:** Fixed Value. This means it is not configurable.

:::caution

When configuring this stream consider that the parent stream paginates with 20 number of items (Max alowed page size). The Paypal API calls are not concurrent, so the time it takes depends entirely on the server side.
This stream could take a considerable time syncing, so you should consider running the sync of this and the parent stream (`list_products`) at the end of the day.
Depending on the size of the catalog it could take several hours to sync.

:::

---

### List Disputes Stream

The below table contains the configuraiton parameters available for this connector and the default values and available features

| **Param/Feature**            | `List Disputes`          |
| :--------------------------- | :----------------------- |
| `Start Date`                 | NA                       |
| `Dispute Start Date Range`   | Timestamp with TZ (w/ms) |
| `Refresh token`              | Auto                     |
| `Number of days per request` | Max 180 , 7(D)           |
| `Pagination Strategy`        | Page Token               |
| `Page size `                 | Max 50 (F)               |
| `Full Refresh`               | :white_check_mark:       |
| `Incremental`                | :white_check_mark: (D)   |

**D:** Default configured Value

**F:** Fixed Value. This means it is not configurable.

---

### Search Invoices Stream

The below table contains the configuraiton parameters available for this connector and the default values and available features

| **Param/Feature**            | `Search Invoices`         |
| :--------------------------- | :------------------------ |
| `Start Date`                 | Timestamp with TZ (no ms) |
| `Dispute Start Date Range`   | NA                        |
| `Refresh token`              | Auto                      |
| `Number of days per request` | ND                        |
| `Pagination Strategy`        | Page Number               |
| `Page size `                 | Max 100 (F)               |
| `Full Refresh`               | :white_check_mark: (D)    |
| `Incremental`                | :x:                       |

**D:** Default configured Value

**F:** Fixed Value. This means it is not configurable.

**ND:** Not Defined in the source.

:::info

The `start_end` from the configuration, is passed to the body of the request and uses the `creation_date_range.start` and `creation_date_range.end`. More information in the [Paypal Developer API documentation](https://developer.paypal.com/docs/api/invoicing/v2/#invoices_search-invoices).

:::

---

### List Payments Stream

The below table contains the configuraiton parameters available for this connector and the default values and available features.

| **Param/Feature**            | `List Payments`           |
| :--------------------------- | :------------------------ |
| `Start Date`                 | Timestamp with TZ (no ms) |
| `Dispute Start Date Range`   | NA                        |
| `Refresh token`              | Auto                      |
| `Number of days per request` | NA , 7(D)                 |
| `Pagination Strategy`        | Page Cursor               |
| `Page size `                 | Max 20 (F)                |
| `Full Refresh`               | :white_check_mark:        |
| `Incremental`                | :white_check_mark: (D)    |

**D:** Default configured Value

**F:** Fixed Value. This means it is not configurable.

---

## Performance Considerations

- **Data Availability:** It takes a maximum of 3 hours for executed transactions to appear in the list transactions call.
- **Number of days per request:** The maximum supported date range is 31 days.
- **Historical Data:** You can't retrieve more than 3yrs of data for the `transactions` stream. For `dispute_start_date` you can only retrieve 180 days of data (see specifications per stream)
- `records_per_request`: The maximum number of records in a single request are 10K (API Server restriction)
- `page_size`: The number of records per page is differs per stream. `source-paypal-transaction` sets maximum allowed page size for each stream by default.
- `requests_per_minute`: The maximum limit is 50 requests per minute from IP address to all endpoint (API Server restriction).

## Data type map

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                      |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------- |
| 2.5.8 | 2025-01-11 | [43797](https://github.com/airbytehq/airbyte/pull/43797) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 2.5.7 | 2024-06-25 | [40269](https://github.com/airbytehq/airbyte/pull/40269) | Update dependencies |
| 2.5.6 | 2024-06-22 | [40110](https://github.com/airbytehq/airbyte/pull/40110) | Update dependencies |
| 2.5.5 | 2024-06-04 | [38983](https://github.com/airbytehq/airbyte/pull/38983) | [autopull] Upgrade base image to v1.2.1 |
| 2.5.4 | 2024-05-20 | [38265](https://github.com/airbytehq/airbyte/pull/38265) | Replace AirbyteLogger with logging.Logger |
| 2.5.3 | 2024-04-24 | [36654](https://github.com/airbytehq/airbyte/pull/36654) | Schema descriptions |
| 2.5.2 | 2024-04-19 | [37435](https://github.com/airbytehq/airbyte/pull/37435) | Updated `manifest.yaml` to use the latest CDK Manifest version to fix the Incremental STATE values |
| 2.5.1 | 2024-03-15 | [36165](https://github.com/airbytehq/airbyte/pull/36165) | Unpin CDK Version |
| 2.5.0 | 2024-03-15 | [36173](https://github.com/airbytehq/airbyte/pull/36173) | Extended `Disputes` stream schema with missing properties |
| 2.4.0 | 2024-02-20 | [35465](https://github.com/airbytehq/airbyte/pull/35465) | Per-error reporting and continue sync on stream failures |
| 2.3.0 | 2024-02-14 | [34510](https://github.com/airbytehq/airbyte/pull/34510) | Silver certified. New Streams Added |
| 2.2.2 | 2024-02-09 | [35075](https://github.com/airbytehq/airbyte/pull/35075) | Manage dependencies with Poetry. |
| 2.2.1 | 2024-01-11 | [34155](https://github.com/airbytehq/airbyte/pull/34155) | prepare for airbyte-lib |
| 2.2.0 | 2023-10-25 | [31852](https://github.com/airbytehq/airbyte/pull/31852) | The size of the time_window can be configured |
| 2.1.2 | 2023-10-23 | [31759](https://github.com/airbytehq/airbyte/pull/31759) | Keep transaction_id as a string and fetch data in 7-day batches |
| 2.1.1 | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 2.1.0 | 2023-08-14 | [29223](https://github.com/airbytehq/airbyte/pull/29223) | Migrate Python CDK to Low Code schema |
| 2.0.0 | 2023-07-05 | [27916](https://github.com/airbytehq/airbyte/pull/27916) | Update `Balances` schema |
| 1.0.0 | 2023-07-03 | [27968](https://github.com/airbytehq/airbyte/pull/27968) | mark `Client ID` and `Client Secret` as required fields |
| 0.1.13 | 2023-02-20 | [22916](https://github.com/airbytehq/airbyte/pull/22916) | Specified date formatting in specification |
| 0.1.12 | 2023-02-18 | [23211](https://github.com/airbytehq/airbyte/pull/23211) | Fix error handler |
| 0.1.11 | 2023-01-27 | [22019](https://github.com/airbytehq/airbyte/pull/22019) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 0.1.10 | 2022-09-04 | [17554](https://github.com/airbytehq/airbyte/pull/17554) | Made the spec and source config to be consistent |
| 0.1.9 | 2022-08-18 | [15741](https://github.com/airbytehq/airbyte/pull/15741) | Removed `OAuth2.0` option |
| 0.1.8 | 2022-07-25 | [15000](https://github.com/airbytehq/airbyte/pull/15000) | Added support of `OAuth2.0` authentication, fixed bug when normalization couldn't handle nested cursor field and primary key |
| 0.1.7 | 2022-07-18 | [14804](https://github.com/airbytehq/airbyte/pull/14804) | Added `RESULTSET_TOO_LARGE` error validation |
| 0.1.6 | 2022-06-10 | [13682](https://github.com/airbytehq/airbyte/pull/13682) | Updated paypal transaction schema |
| 0.1.5 | 2022-04-27 | [12335](https://github.com/airbytehq/airbyte/pull/12335) | Added fixtures to mock time.sleep for connectors that explicitly sleep |
| 0.1.4 | 2021-12-22 | [9034](https://github.com/airbytehq/airbyte/pull/9034) | Updated connector fields title/description |
| 0.1.3 | 2021-12-16 | [8580](https://github.com/airbytehq/airbyte/pull/8580) | Added more logs during `check connection` stage |
| 0.1.2 | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Removed base-python dependencies |
| 0.1.1 | 2021-08-03 | [5155](https://github.com/airbytehq/airbyte/pull/5155) | Fixed start_date_min limit |
| 0.1.0 | 2021-06-10 | [4240](https://github.com/airbytehq/airbyte/pull/4240) | PayPal Transaction Search API |

</details>
