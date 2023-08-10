## Prerequisites

- Access to the Stripe account containing the data to replicate

## Setup Guide

:::note
To authenticate the Stripe connector, you need an API key with **Read** privileges for the data to replicate. For steps on obtaining and setting permissions for this key, refer to our [full Stripe documentation](https://docs.airbyte.com/integrations/sources/stripe#setup-guide).
:::

1. For **Source name**, enter a name to help you identify this source.
2. For **Account ID**, enter your Stripe Account ID. This ID begins with `acct_`, and can be found in the top-right corner of your Stripe [account settings page](https://dashboard.stripe.com/settings/account).
3. For **Secret Key**, enter your Stripe API key, which can be found at your Stripe [API keys page](https://dashboard.stripe.com/apikeys).
4. For **Replication Start Date**, use the provided datepicker or enter a UTC date and time programmatically in the format `YYYY-MM-DDTHH:mm:ssZ`. The data added on and after this date will be replicated.
5. (Optional) For **Lookback Window**, you may specify a number of days from the present day to reread data. This allows the connector to retrieve data that might have been updated after its initial creation, and is useful for handling any post-transaction adjustments (such as tips, refunds, chargebacks, etc).

    - Leaving the **Lookback Window** at its default value of 0 means Airbyte will not re-export data after it has been synced.
    - Setting the **Lookback Window** to 1 means Airbyte will re-export and capture any data changes within the last day.
    - Setting the **Lookback Window** to 7 means Airbyte will re-export and capture any data changes within the last week.

6. (Optional) For **Data Request Window**, you may specify the time window in days used by the connector when requesting data from the Stripe API. This window defines the span of time covered in each request, with larger values encompassing more days in a single request. Generally speaking, the lack of overhead from making fewer requests means a larger window is faster to sync. However, this also means the state of the sync will persist less frequently. If an issue occurs or the sync is interrupted, a larger window means more data will need to be resynced, potentially causing a delay in the overall process.

    For example, if you are replicating three years worth of data:

    - A **Data Request Window** of 365 days means Airbyte makes 3 requests, each for a year. This is generally faster but risks needing to resync up to a year's data if the sync is interrupted.
    - A **Data Request Window** of 30 days means 36 requests, each for a month. This may be slower but minimizes the amount of data that needs to be resynced if an issue occurs.

    If you are unsure of which value to use, we recommend leaving this setting at its default value of 365 days.
7. Click **Set up source** and wait for the tests to complete.

### Stripe API limitations

- When syncing `events` data from Stripe, data is only [returned for the last 30 days](https://stripe.com/docs/api/events). Using the Full Refresh (Overwrite) sync from Airbyte will delete the events data older than 30 days from your target destination. Use an Append sync mode to ensure historical data is retained.

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Stripe](https://docs.airbyte.com/integrations/sources/stripe).
