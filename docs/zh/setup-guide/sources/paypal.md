# PayPal

This page contains the setup guide and reference information for PayPal.

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental Append Sync | Yes |
| Namespaces | No |

## Prerequisites

* Client ID
* Client secret

## Setup guide

### Step 1: Obtain PayPal crendentials

Follow these [instructions](https://developer.paypal.com/docs/multiparty/get-started/) or the below steps to obtain your `client_id` and `client_secret` needed to set up the source in Daspire.

1. Sign in to your [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/).

2. Click **Apps & credentials** from the top menu.
![Paypal Apps & Creds](/docs/setup-guide/assets/images/paypal-app-creds.jpg "Paypal Apps & Creds")

3. Click the **Create App**.
![Paypal Create App](/docs/setup-guide/assets/images/paypal-create-app.jpg "Paypal Create App")

4. Enter a name for your app. Under App Type, select **Platform**. Click **Create App**.
![Paypal App Type](/docs/setup-guide/assets/images/paypal-app-type.jpg "Paypal App Type")

5. A sandbox account with the recommended platform settings will be automatically created. And you will be directed to the App's details page.

6. Copy the **Client ID** and **Secret key**. You will use them to set up the source in Daspire.
![Paypal API Creds](/docs/setup-guide/assets/images/paypal-api-creds.jpg "Paypal API Creds")

### Step 2: Set up PayPal  in Daspire

1. Select **PayPal** from the Source list.

2. Enter a **Source Name**.

3. Enter **Client ID** and **Client secret (Secret key)** you obtained in Step 1.

4. Choose if your account is sandbox.

5. Enter the date you want your sync to start from.

4. Click **Save & Test**.

## Supported streams

This source is capable of syncing the following streams:

* [Balances](https://developer.paypal.com/docs/api/transaction-search/v1/#balances)
* [Transactions](https://developer.paypal.com/docs/api/transaction-search/v1/#transactions)

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |

## Performance considerations

PayPal transaction API has some [limits](https://developer.paypal.com/docs/integration/direct/transaction-search/):

* `start_date_min` = 3 years, API call lists transaction for the previous three years.
* `start_date_max` = 1.5 days, it takes a maximum of three hours for executed transactions to appear in the list transactions call. It is set to 1.5 days by default based on experience, otherwise API throw an error.
* `stream_slice_period` = 7 day, the maximum supported date range is 31 days.
* `records_per_request` = 10000, the maximum number of records in a single request.
* `page_size` = 500, the maximum page size is 500.
* `requests_per_minute` = 30, maximum limit is 50 requests per minute from IP address to all endpoint

By default, syncs are performed with a slice period of `7 days`. If you see errors with the message `Result set size is greater than the maximum limit. Change the filter criteria and try again.`, lower the size of the slice period in your source configuration.

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
