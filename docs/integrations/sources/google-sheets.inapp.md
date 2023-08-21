## Prerequisites
- Spreadsheet Link - The link to the Google spreadsheet you want to sync.
- A Google Workspace user with access to the spreadsheet

:::info
The Google Sheets source connector pulls data from a single Google Sheets spreadsheet. To replicate multiple spreadsheets, set up multiple Google Sheets source connectors in your Airbyte instance.
:::

## Setup guide

1. Enter a name for the Google Sheets connector.
2. Authenticate your Google account via OAuth or Service Account Key Authentication.
    - **(Recommended)** To authenticate your Google account via OAuth, click **Sign in with Google** and complete the authentication workflow.
    - To authenticate your Google account via Service Account Key Authentication, enter your [Google Cloud service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys) in JSON format. Make sure the Service Account has the Project Viewer permission. If your spreadsheet is viewable by anyone with its link, no further action is needed. If not, [give your Service account access to your spreadsheet](https://youtu.be/GyomEw5a2NQ%22).
3. For **Spreadsheet Link**, enter the link to the Google spreadsheet. To get the link, go to the Google spreadsheet you want to sync, click **Share** in the top right corner, and click **Copy Link**.
4. For **Row Batch Size**, define the number of records you want the Google API to fetch at a time. The default value is 200. You can increase this value according to your needs to avoid rate limits if your data is particularly wide.
5. For **Convert Column Names to SQL-Compliant Format**, enable to use the conversion of column names to a standardized, SQL-compliant format. For example, 'My Name' -> 'my_name'. Enable this option if your destination is SQL-based.

### Google Sheets format requirements
- Airbyte only supports replicating [Grid](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#SheetType) sheets.

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Google Sheets](https://docs.airbyte.com/integrations/sources/google-sheets/).
