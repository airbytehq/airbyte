## Prerequisite

- A verified property in Google Search Console
<!-- env:oss -->
- Google Search Console API enabled for your project (**Airbyte Open Source** only)
<!-- /env:oss -->

## Setup guide

1. For **Source name**, enter a name to help you identify this source.
2. For **Website URL Property**, enter the specific website property in Google Seach Console with data you want to replicate.
3. For **Start Date**, by default the `2021-01-01` is set, use the provided datepicker or enter a date in the format `YYYY-MM-DD`. Any data created on or after this date will be replicated.
4. To authenticate the connection:

   <!-- env:cloud -->
   - **For Airbyte Cloud**: Select **Oauth** from the Authentication dropdown, then click **Sign in with Google** to authorize your account. More information on authentication methods can be found in our [full Google Search Console documentation](https://docs.airbyte.io/integrations/sources/google-search-console#setup-guide).
   <!-- /env:cloud -->
   <!-- env:oss -->
   - (Recommended) To authenticate with a service account, select **Service Account Key Authorization** from the Authentication dropdown, then enter the **Admin Email** and **Service Account JSON Key**. For the key, copy and paste the JSON key you obtained during the service account setup. It should begin with `{"type": "service account", "project_id": YOUR_PROJECT_ID, "private_key_id": YOUR_PRIVATE_KEY, ...}`.
   - To authenticate with OAuth, select **Oauth** from the Authentication dropdown, then enter your **Client ID**, **Client Secret**, **Access Token** and **Refresh Token**. More information on authentication methods for Airbyte Open Source can be found in our [full Google Search Console documentation](https://docs.airbyte.io/integrations/sources/google-search-console#setup-guide).
   <!-- /env:oss -->

5. (Optional) For **End Date**, you may optionally provide a date in the format `YYYY-MM-DD`. Any data created between the defined Start Date and End Date will be replicated. Leaving this field blank will replicate all data created on or after the Start Date to the present.
6. (Optional) For **Custom Reports**, you may optionally provide an array of JSON objects representing any custom reports you wish to query the API with. Refer to the [Custom reports](https://docs.airbyte.com/integrations/sources/google-search-console#custom-reports) section in our full documentation for more information on formulating these reports.
7. (Optional) For **Data Freshness**, you may choose whether to include "fresh" data that has not been finalized by Google, and may be subject to change. Please note that if you are using Incremental sync mode, we highly recommend leaving this option to its default value of `final`. Refer to the [Data Freshness](https://docs.airbyte.com/integrations/sources/google-search-console#data-freshness) section in our full documentation for more information on this parameter.
8. Click **Set up source** and wait for the tests to complete.

For detailed information on supported sync modes, supported streams, and performance considerations, refer to the full documentation for [Google Search Console](https://docs.airbyte.com/integrations/sources/google-search-console/).
