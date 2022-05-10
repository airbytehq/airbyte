# Google Sheets

## Sync overview

The Google Sheets Source is configured to pull data from a single Google Sheets spreadsheet. To replicate multiple spreadsheets, you can create multiple instances of the Google Sheets Source in your Airbyte instance.

### Output schema

Each sheet in the selected spreadsheet will be output as a separate stream. Each selected column in the sheet is output as a string field.

Airbyte only supports replicating Grid sheets. See the [Google Sheets API docs](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#SheetType) for more info on all available sheet types.

**Note: Sheet names and column headers must contain only alphanumeric characters or `_`, as specified in the** [**Airbyte Protocol**](../../understanding-airbyte/airbyte-specification.md). If your sheet or column header is named e.g: "the data", you'll need to change it to "the\_data" for it to be synced by Airbyte. This restriction does not apply to non-header cell values: those can contain any unicode characters. This limitation is temporary and future versions of Airbyte will support more permissive naming patterns.

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| any type | `string` |  |

### Features

This section should contain a table with the following format:

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Coming soon |  |
| Namespaces | No |  |

### Performance considerations

At the time of writing, the [Google API rate limit](https://developers.google.com/sheets/api/limits) is 100 requests per 100 seconds per user and 500 requests per 100 seconds per project. Airbyte batches requests to the API in order to efficiently pull data and respects these rate limits. It is recommended that you use the same service user \(see the "Creating a service user" section below for more information on how to create one\) for no more than 3 instances of the Google Sheets Source to ensure high transfer speeds.

## Getting Started (Airbyte Cloud)
To configure the connector you'll need to:

* [Authorize your Google account via OAuth](#oauth)
* [The ID of the spreadsheet you'd like to sync](#sheetlink)

### <a name="oauth"></a> Authorize your Google account via OAuth
Click on the "Sign in with Google" button and authorize via your Google account.

### <a name="sheetlink"></a>Spreadsheet Link
You will need the link of the Spreadsheet you'd like to sync. To get it, click Share button in the top right corner of Google Sheets interface, and then click Copy Link in the dialog that pops up.
These two steps are highlighted in the screenshot below:

![](../../.gitbook/assets/google_spreadsheet_url.png)

## Getting started (Airbyte OSS)

### Requirements

To configure the Google Sheets Source for syncs, you'll need the following:

* [Enable the Google Sheets and Google Drive APIs for your personal or organization account](#enableapi)
* [Create a service account with permissions to access the Google Sheets and Drive APIs](#createserviceaccount)
* [Create a Service Account Key for the Service Account](#createserviceaccount)
* [Share the spreadsheets you'd like to sync with the Service Account created above](#sharesheet)
* [The Link to the spreadsheet you'd like to sync](#findsheetlink)

### <a name="setupguide"></a>Setup guide

#### <a name="enableapi"></a>Enable the Google Sheets and Google Drive APIs

Follow the Google documentation for [enabling and disabling APIs](https://support.google.com/googleapi/answer/6158841?hl=en) to enable the Google Sheets and Google Drive APIs. This connector only needs Drive to find the spreadsheet you ask us to replicate; it does not look at any of your other files in Drive.

The video below illustrates how to enable the APIs:

{% embed url="https://youtu.be/Fkfs6BN5HOo" caption="" %}

#### <a name="createserviceaccount"></a>Create a Service Account and Service Account Key

Follow the [Google documentation for creating a service account](https://support.google.com/googleapi/answer/6158849?hl=en&ref_topic=7013279) with permissions as Project Viewer, **following the section titled Service Accounts, NOT OAuth 2.0**. In the "Grant this service account access to project" section of the wizard, grant the service account the role of Project &gt; Viewer. The video below also illustrates how you can create a Service Account and Key:

{% embed url="https://youtu.be/-RZiNY2RHDM" caption="" %}

You'll notice that once you create the key, your browser will automatically download a JSON file. **This is the credentials JSON file that you'll input in the Airbyte UI later in this process, so keep it around.**

\*\*\*\*

#### <a name="sharesheet"></a>Share your spreadsheet with the Service Account

Once you've created the Service Account, you need to explicitly give it access to your spreadsheet. If your spreadsheet is viewable by anyone with its link, no further action is needed. If this is not the case, then in the "Credentials" tab on the left side of your Google API Dashboard, copy the email address of the Service Account you just created. Then, in the Google sheets UI, click the "share" button and share the spreadsheet with the service account. The video below illustrates this process.

{% embed url="https://youtu.be/GyomEw5a2NQ" caption="" %}

#### <a name="findsheetlink"></a>Spreadsheet Link

Finally, you'll need the Link to the Spreadsheet you'd like to sync. To get it, click Share button in the top right corner of Google Sheets interface, and then click Copy Link in the dialog that pops up. 
These two steps are highlighted in the screenshot below:

![](../../.gitbook/assets/google_spreadsheet_url.png)

### Setting up in the Airbyte UI

The Airbyte UI will ask for two things:

1. Spreadsheet Link
2. The content of the credentials JSON you created in the ["Create a Service Account and Service Account Key"](#createserviceaccount) step above. This should be as simple as opening the file and copy-pasting all its contents into this field in the Airbyte UI.

## Changelog

| Version | Date       | Pull Request                                               | Subject                                                                       |
|---------|------------|------------------------------------------------------------|-------------------------------------------------------------------------------|
| 0.2.13  | 2022-05-06 | [12685](https://github.com/airbytehq/airbyte/pull/12685)   | Update CDK to v0.1.56 to emit an `AirbyeTraceMessage` on uncaught exceptions  |
| 0.2.12  | 2022-04-20 | [12230](https://github.com/airbytehq/airbyte/pull/12230)   | Update connector to use a `spec.yaml`                                         |
| 0.2.11  | 2022-04-13 | [11977](https://github.com/airbytehq/airbyte/pull/11977)   | Replace leftover print statement with airbyte logger                          |
| 0.2.10  | 2022-03-25 | [11404](https://github.com/airbytehq/airbyte/pull/11404)   | Allow using Spreadsheet Link/URL instead of Spreadsheet ID                    |
| 0.2.9   | 2022-01-25 | [9208](https://github.com/airbytehq/airbyte/pull/9208)     | Update title and descriptions                                                 |
| 0.2.7   | 2021-09-27 | [8470](https://github.com/airbytehq/airbyte/pull/8470)     | Migrate to the CDK                                                            |
| 0.2.6   | 2021-09-27 | [6354](https://github.com/airbytehq/airbyte/pull/6354)     | Support connecting via Oauth webflow                                          |
| 0.2.5   | 2021-09-12 | [5972](https://github.com/airbytehq/airbyte/pull/5972)     | Fix full_refresh test by adding supported_sync_modes to Stream initialization |
| 0.2.4   | 2021-08-05 | [5233](https://github.com/airbytehq/airbyte/pull/5233)     | Fix error during listing sheets with diagram only                             |
| 0.2.3   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973)     | Add AIRBYTE_ENTRYPOINT for Kubernetes support                                 |
| 0.2.2   | 2021-04-20 | [2994](https://github.com/airbytehq/airbyte/pull/2994)     | Formatting spec                                                               |
| 0.2.1   | 2021-04-03 | [2726](https://github.com/airbytehq/airbyte/pull/2726)     | Fix base connector versioning                                                 |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238)     | Protocol allows future/unknown properties                                     |
| 0.1.7   | 2021-01-21 | [1762](https://github.com/airbytehq/airbyte/pull/1762)     | Fix issue large spreadsheet                                                   |
| 0.1.6   | 2021-01-27 | [1668](https://github.com/airbytehq/airbyte/pull/1668)     | Adopt connector best practices                                                |
| 0.1.5   | 2020-12-30 | [1438](https://github.com/airbytehq/airbyte/pull/1438)     | Implement backoff                                                             |
| 0.1.4   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046)     | Add connectors using an index YAML file                                       |
