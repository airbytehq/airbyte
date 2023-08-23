## Prerequisites

- An Amazon user with access to an [Amazon Ads account](https://advertising.amazon.com).

<!-- env:oss -->
:::info
To use the Amazon Ads source connector with **Airbyte Open Source**, you will first need to complete Amazon's onboarding process and obtain the credentials to authenticate the connection. Please refer to [our full Amazon Ads documentation](https://docs.airbyte.com/integrations/sources/amazon-ads/#setup-guide) for more information.
:::
<!-- /env:oss -->

## Setup Guide

1. Enter a **Source name** to help you identify this source.
2. To authenticate the connection:

<!-- env:cloud -->
  - **For Airbyte Cloud**: Click **Authenticate your Amazon Ads account**. Follow the instructions to authorize Airbyte to access your Amazon Ads account.
<!-- /env:cloud -->
<!-- env:oss -->
  - **For Airbyte Open Source**: Enter your Amazon Ads **Client ID**, **Client Secret** and **Refresh Token**.
<!-- /env:oss -->

3. Select the **Region** of the country you selected when registering your Amazon account. The options are **North America (NA)**, **Europe (EU)**, and **Far East (FE)**. See the [Amazon docs](https://advertising.amazon.com/API/docs/en-us/info/api-overview#api-endpoints) for a list of each region's associated Marketplaces.
4. (Optional) For **Start Date**, use the provided datepicker or enter a date programmatically in the format `YYYY-MM-DD`. This determines the starting date for pulling reports generated from the API. Please do not set this value more than [60 days in the past](https://advertising.amazon.com/API/docs/en-us/guides/reporting/v2/faq#what-is-the-available-report-history-for-the-version-2-reporting-api). If left blank, today's date is used. The date is tied to the timezone of the associated profile.
5. (Optional) For **Profile IDs**, you may enter one or more IDs of profiles associated with your account that you want to fetch data for. If left blank, data will be fetched from all profiles associated with the Amazon Ads account. See the [Amazon docs](https://advertising.amazon.com/API/docs/en-us/concepts/authorization/profiles) for more information on profiles.
6. (Optional) For **Campaign State Filter**, you may enter one or more "states" to filter the data for the Display, Product, and Brand Campaign streams. The options are:

  **enabled**: Filters for campaigns that are currently active and running.
  **paused**: Filters for campaigns that are set up but not currently running.
  **archived**: Filters for campaigns that are no longer active and have been archived for record-keeping.
  
  If this field is left blank, no filters will be applied.
7. (Optional) For **Lookback Window**, you may specify a window of time in days from the present to re-fetch data that may have been updated in the Amazon Ads API. By default, this window is set to 3 days to align with Amazon's [traffic validation process](https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/faq#how-long-does-it-take-for-sponsored-ads-reporting-data-to-become-available), during which time small changes to impression and click data may occur.
8. (Optional) For **Report Types**, you may optionally specify one or more report types you would like to query from the API. Depending on the type of Sponsored Ad, performance can be analyzed using different dimensions. Each type of Sponsored Ad supports different report types. For more information on this topic, see the [Amazon documentation](https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types). Leaving this field blank will pull all available report types.
9. Click **Set up source** and wait for the tests to complete.

### Report Timezones

All the reports are generated relative to the target profile' timezone.

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Amazon Ads](https://docs.airbyte.com/integrations/sources/amazon-ads).
