## Prerequisites

- Access to a Google Sheet

:::info
The Google Sheets source connector pulls data from a single Google Sheets spreadsheet. To replicate multiple spreadsheets, set up multiple Google Sheets source connectors in your Airbyte instance.
:::

## Setup guide

1. Enter a name for the Google Sheets connector.
2. Authenticate your Google account via OAuth or Service Account Key Authentication.
    - **(Recommended)** To authenticate your Google account via OAuth, click **Sign in with Google** and complete the authentication workflow.
    - To authenticate your Google account via Service Account Key Authentication, enter your [Google Cloud service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys) in JSON format. Make sure the Service Account has the Project Viewer permission. If your spreadsheet is viewable by anyone with its link, no further action is needed. If not, [give your Service account access to your spreadsheet](https://youtu.be/GyomEw5a2NQ%22).
3. For **Spreadsheet Link**, enter the link to the Google spreadsheet. To get the link, go to the Google spreadsheet you want to sync, click **Share** in the top right corner, and click **Copy Link**.
4. For **Row Batch Size**, define the number of records you want the Google API to fetch at a time. The default value is 200.

### Google Sheets format requirements
- Sheet names and column headers must only contain alphanumeric characters or `_`, as specified in the [**Airbyte Protocol**](../../understanding-airbyte/airbyte-protocol.md). For example, if your sheet or column header is named `the data`, rename it to `the_data`. This restriction does not apply to non-header cell values.
- Airbyte only supports replicating [Grid](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#SheetType) sheets.

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Google Sheets](https://docs.airbyte.com/integrations/sources/google-sheets/).
