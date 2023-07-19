## Prerequisites

- Your [Stripe `Account ID`](https://dashboard.stripe.com/settings/account)
- Your [Stripe `Secret Key`](https://dashboard.stripe.com/apikeys)

## Setup Guide

1. Enter a name for your source.
2. For **Account ID**, enter your [Stripe `Account ID`](https://dashboard.stripe.com/settings/account).
3. For **Secret Key**, enter your [Stripe `Secret Key`](https://dashboard.stripe.com/apikeys)

   We recommend creating a secret key specifically for Airbyte to control which resources Airbyte can access. For ease of use, we recommend granting read permission to all resources and configuring which resource to replicate in the Airbyte UI. You can also use the API keys for the [test mode](https://stripe.com/docs/keys#obtain-api-keys) to try out the Stripe integration with Airbyte.

4. For **Replication start date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. Data created on and after this date will be replicated.
5. (Optional) For **Lookback Window in days**, select the number of days the value in days prior to the start date that you to sync your data with. If your data is updated after setting up this connector, you can use the this option to reload data from the past N days. Example: If the Replication start date is set to `2021-01-01T00:00:00Z`, then:
   - If you leave the Lookback Window in days parameter to its the default value of 0, Airbyte will sync data from the Replication start date `2021-01-01T00:00:00Z`
   - If the Lookback Window in days value is set to 1, Airbyte will consider the Replication start date to be `2020-12-31T00:00:00Z`
   - If the Lookback Window in days value is set to 7, Airbyte will sync data from `2020-12-25T00:00:00Z`
6. Click **Set up source**.

### Stripe API limitations
- When syncing `events` data from Stripe, data is only [returned for the last 30 days](https://stripe.com/docs/api/events). Using the full-refresh-overwrite sync from Airbyte will delete the events data older than 30 days from your target destination. Use an append sync mode to ensure historical data is retained.

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Stripe](https://docs.airbyte.com/integrations/sources/stripe).
