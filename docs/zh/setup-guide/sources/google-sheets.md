# Google Sheets

This page contains the setup guide and reference information for Google Sheets.

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh - Overwrite | Yes |
| Full Refresh - Append | Yes |

## Prerequisites

* Google Cloud Console access
* A Google Cloud Platform (GCP) project
* Enable the Google Sheets API in your GCP project
* Service Account Key with access to the Spreadsheet you want to replicate

## Setup guide

### Step 1: Create a Service Account for authentication

1. Go to the [Service Accounts](https://console.developers.google.com/iam-admin/serviceaccounts) page in the Google Developers console.
![Google Service Accounts](/docs/setup-guide/assets/images/ga4-service-accounts.jpg "Google Service Accounts")

2. Select the project you want to use (or create a new one).

3. Click **+ Create Service Account** at the top of the page.
![Google Create Service Account](/docs/setup-guide/assets/images/ga4-create-service-account.jpg "Google Create Service Account")

4. Enter a name for the service account, and click **Create and Continue**.
![Google Service Account Details](/docs/setup-guide/assets/images/ga4-service-account-details.jpg "Google Service Account Details")

5. Choose the role for the service account. We recommend the **Viewer role (Read & Analyze permissions)**. Click Continue. And then click Done.
![Google Service Account Role](/docs/setup-guide/assets/images/ga4-service-account-role.jpg "Google Service Account Role")

6. Select your new service account from the list, and open the Keys tab. Click **Keys** > **Add Key**.
![Google Service Account Add Key](/docs/setup-guide/assets/images/ga4-service-account-add-key.jpg "Google Service Account Add Key")

7. Select **JSON** as the Key type. Then click Create. This will generate and download the JSON key file that you'll use for authentication.

### Step 2: Enable the Google Sheets API

1. Go to the [API Console/Librar](https://console.cloud.google.com/apis/library) page.

2. Make sure you have selected the correct project from the top.

3. Find and select the Google Sheets API.
![Google Sheets API](/docs/setup-guide/assets/images/gsheets-api.jpg "Google Sheets API")

4. Click ENABLE.
![Enable Google Sheets API](/docs/setup-guide/assets/images/gsheets-api-enable.jpg "Enable Google Sheets API")

NOTE: If your spreadsheet is viewable by anyone with its link, no further action is needed and you can proceed to **Step 4**. If not, give your Service account access to your spreadsheet by following Step 3.

### Step 3: Give your Service account access to your spreadsheet

1. Go to [Google Cloud Service accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) and find your **service account email**. Copy it.
![Google Service Account Email](/docs/setup-guide/assets/images/gsheets-email.jpg "Google Service Account Email")

2. Open the Google Sheets you want to sync, and click **Share** in the top right corner.
![Google Sheets Share](/docs/setup-guide/assets/images/gsheets-share.jpg "Google Sheets Share")

3. Enter your Service account email, give it **Viewer** access, and click Share.
![Google Sheets Viewer Access](/docs/setup-guide/assets/images/gsheets-viewer-access.jpg "Google Sheets Viewer Access")

### Step 4: Obtain Google Sheets link

1.  Go to the Google spreadsheet you want to sync, click **Share** in the top right corner, and click **Copy Link**.
![Google Sheets Link](/docs/setup-guide/assets/images/gsheets-link.jpg "Google Sheets Link")

2. You're ready to set up Google Sheets in Daspire!

### Step 5: Set up Google Sheets in Daspire

1. Select **Google Sheets** from the Source list.

2. Enter a **Source Name**.

3. In authentication method, select **Service Account Key Authentication** and enter your Google Cloud service account key you obtained in Step 1 in JSON format:

```
  {
    "type": "service_account",
    "project_id": "YOUR_PROJECT_ID",
    "private_key_id": "YOUR_PRIVATE_KEY",
    ...
  }
```

4. For **Spreadsheet Link**, enter the link to the Google spreadsheet you obtained in Step 4.

5. (Optional) You may enable the option to **Convert Column Names to SQL-Compliant Format**. Enabling this option will allow the connector to convert column names to a standardized, SQL-friendly format. For example, a column name of `Café Earnings 2022` will be converted to `cafe_earnings_2022`. We recommend enabling this option if your target destination is SQL-based (ie Postgres, MySQL). Set to false by default.

6. Click **Save & Test**.

## Output schema

Each sheet in the selected spreadsheet is synced as a separate stream. Each selected column in the sheet is synced as a string field.

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| Any type | `string` |

## Performance considerations

The Google API rate limits are:

  * 300 read requests per minute per project
  * 60 requests per minute per user per project

Daspire batches requests to the API in order to efficiently pull data and respect these rate limits. We recommend not using the same user or service account for more than 3 instances of the Google Sheets source integration to ensure high transfer speeds.

## Troubleshooting

1. If your sheet is completely empty (no header rows) or deleted, Daspire will not delete the table in the destination. If this happens, the sync logs will contain a message saying the sheet has been skipped when syncing the full spreadsheet.

2. Source setup will fail if the speadsheet is not a Google Sheets file. If the file was saved or imported as another file type the setup could fail.

3. Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
