## Prerequisites

- API Access Key

In order to get a free `API Access Key` please go to [this](https://manage.exchangeratesapi.io/signup/free) page and enter the required information. After registration and login, you will see your `API Access Key`. You can also locate it [here](https://manage.exchangeratesapi.io/dashboard).

If you have a `free` subscription plan, you will have two limitations to the plan: 

1. Limit of 1,000 API calls per month
2. You won't be able to specify the `base` parameter, meaning that you will be only be allowed to use the default base value which is EUR.

## Setup guide
1. Enter a **Name** for your source.
2. Enter your **API key** as the `access_key` from the prerequisites.
3. Enter the **Start Date** in YYYY-MM-DD format. The data added on and after this date will be replicated. 
4. (Optional) Enter a **base** currency. For those on the free plan, `EUR` is the only option available. If none are specified, `EUR` will be used.
5. Click **Set up source**.

### Exchange Rates data output
- The sync will include one stream: `exchange_rates`
- Each record in the stream contains many fields:
  - The date of the record
  - One field for every supported [currency](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html) which contain the value of that currency on that date.

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Exchange Rates](https://docs.airbyte.com/integrations/sources/exchange-rates/).
