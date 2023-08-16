## Prerequisites

- Access to a Google spreadsheet

:::info
The Google Sheets source connector pulls data from a single Google Sheets spreadsheet. To replicate multiple spreadsheets, set up multiple Google Sheets source connectors in your Airbyte instance.
:::

## Setup guide

1. For **Source name**, enter a name to help you identify this source.
2. Select your authentication method:

<!-- env:cloud -->

#### For Airbyte Cloud

- **(Recommended)** Select **Authenticate via Google (OAuth)** from the Authentication dropdown, click **Sign in with Google** and complete the authentication workflow.

<!-- /env:cloud -->
<!-- env:oss -->

#### For Airbyte Open Source

- **(Recommended)** Select **Service Account Key Authentication** from the dropdown and enter your Google Cloud service account key in JSON format:

    ```js
    { "type": "service_account", "project_id": "YOUR_PROJECT_ID", "private_key_id": "YOUR_PRIVATE_KEY", ... }
    ```

- To authenticate your Google account via OAuth, select **Authenticate via Google (OAuth)** from the dropdown and enter your Google application's client ID, client secret, and refresh token.

For detailed instructions on how to generate a service account key or OAuth credentials, refer to the [full documentation](https://docs.airbyte.io/integrations/sources/google-sheets#setup-guide).

<!-- /env:oss -->

3. For **Spreadsheet Link**, enter the link to the Google spreadsheet. To get the link, go to the Google spreadsheet you want to sync, click **Share** in the top right corner, and click **Copy Link**.
4. (Optional) You may enable the option to **Convert Column Names to SQL-Compliant Format**. Enabling this option will allow the connector to convert column names to a standardized, SQL-friendly format. For example, a column name of `Café Earnings 2022` will be converted to `cafe_earnings_2022`. We recommend enabling this option if your target destination is SQL-based (ie Postgres, MySQL). Set to false by default.
5. (Optional) For **Row Batch Size**, you may specify the number of records you want to fetch per request to the Google API. By adjusting this value, you can balance the efficiency of the data retrieval process with [Google's request quotas](#performance-consideration). The default value of 200 should suffice for most use cases.
6. Click **Set up source** and wait for the tests to complete.

### Google Sheets format requirements

- When replicating data to a SQL-based destination (such as Postgres or MySQL), sheet names and column headers must contain **only alphanumeric characters or `_`**. For example, if your sheet or column header is named `The Data 2022`, it should be renamed to `the_data_2022`. To automatically convert column names to this format, enable the **Convert Column Names to SQL-Compliant Format** option. Please note that this option only converts column names and not sheet names. This naming restriction does not apply to non-header cell values.
- Airbyte only supports replicating [Grid](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#SheetType) sheets.

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Google Sheets](https://docs.airbyte.com/integrations/sources/google-sheets/).
