# Google Sheets

## Sync overview

The Google Sheets Source is configured to pull data from a single Google Sheets spreadsheet. To replicate multiple spreadsheets, you can create multiple instances of the Google Sheets Source in your Airbyte instance.

### Output schema

Each sheet in the selected spreadsheet will be output as a separate stream. Each selected column in the sheet is output as a string field.

Airbyte only supports replicating Grid sheets. See the [Google Sheets API docs](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#SheetType) for more info on all available sheet types.

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| any type | `string` |  |

### Features

This section should contain a table with the following format:

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

At the time of writing, the [Google API rate limit](https://developers.google.com/sheets/api/limits) is 100 requests per 100 seconds per user and 500 requests per 100 seconds per project. Airbyte batches requests to the API in order to efficiently pull data and respects these rate limits. It is recommended that you use the same service user \(see the "Creating a service user" section below for more information on how to create one\) for no more than 3 instances of the Google Sheets Source to ensure high transfer speeds.

## Getting started

### Requirements

To configure the Google Sheets Source for syncs, you'll need the following:

* Enable the Google Sheets API for your personal or organization account
* Enable the Google Drive API for your personal or organization account
* Create a service account with permissions to access the Google Sheets and Drive APIs
* Create a Service Account Key for the Service Account 
* Share the spreadsheets you'd like to sync with the Service Account created above
* The ID of the spreadsheet you'd like to sync

### Setup guide

#### Enable the Google Sheets and Google Drive APIs

Follow the Google documentation for [enabling and disabling APIs](https://support.google.com/googleapi/answer/6158841?hl=en) to enable the Google Sheets and Google Drive APIs. This connector only needs Drive to find the spreadsheet you ask us to replicate; it does not look at any of your other files in Drive.

The video below illustrates how to enable the APIs:

{% embed url="https://youtu.be/Fkfs6BN5HOo" caption="" %}

#### Create a Service Account and Service Account Key

Follow the [Google documentation for creating a service account](https://support.google.com/googleapi/answer/6158849?hl=en&ref_topic=7013279) with permissions as Project Viewer, **following the section titled Service Accounts, NOT OAuth 2.0**. The video below also illustrates how you can create a Service Account and Key:

{% embed url="https://youtu.be/-RZiNY2RHDM" caption="" %}

You'll notice that once you create the key, your browser will automatically download a JSON file. **This is the credentials JSON file that you'll input in the Airbyte UI later in this process, so keep it around.**

\*\*\*\*

#### Share your spreadsheet with the Service Account

Once you've created the Service Account, you need to explicitly give it access to your spreadsheet. If your spreadsheet is viewable by anyone with its link, no further action is needed. If this is not the case, then in the "Credentials" tab on the left side of your Google API Dashboard, copy the email address of the Service Account you just created. Then, in the Google sheets UI, click the "share" button and share the spreadsheet with the service account. The video below illustrates this process.

{% embed url="https://youtu.be/GyomEw5a2NQ" caption="" %}

#### The spreadsheet ID of your Google Sheet

Finally, you'll need the ID of the Spreadsheet you'd like to sync. To get it, navigate to the spreadsheet in your browser, then copy the portion of the URL which comes after "/d" and before "/edit" or "/view". This is the highlighted portion of the screenshot below:

![](../../.gitbook/assets/screen-shot-2020-10-30-at-2.44.55-pm%20%281%29%20%281%29%20%281%29%20%281%29.png)

### Setting up in the Airbyte UI

The Airbyte UI will ask for two things:

1. The spreadsheet ID
2. The content of the credentials JSON you created in the "Create a Service Account and Service Account Key" step above. This should be as simple as opening the file and copy-pasting all its contents into this field in the Airbyte UI. 

