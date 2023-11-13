# Google Sheets

The Google Sheets Destination is configured to push data to a single Google Sheets spreadsheet with multiple Worksheets as streams. To replicate data to multiple spreadsheets, you can create multiple instances of the Google Sheets Destination in your Airbyte instance. 

:::warning

Google Sheets imposes rate limits and hard limits on the amount of data it can receive, which results in sync failure. Only use Google Sheets as a destination for small, non-production use cases,  as it is not designed for handling large-scale data operations.

Read more about the [limitations](#limitations) of using Google Sheets below.

:::

## Prerequisites

- Google Account
- Google Spreadsheet URL

## Step 1: Set up Google Sheets

### Google Account

To create a Google account, visit [Google](https://support.google.com/accounts/answer/27441?hl=en) and create a Google Account.

### Google Sheets (Google Spreadsheets)

1. Once you are logged into your Google account, create a new Google Sheet. [Follow this guide](https://support.google.com/docs/answer/6000292?hl=en&co=GENIE.Platform%3DDesktop) to create a new sheet. You may use an existing Google Sheet.
2. You will need the link of the Google Sheet you'd like to sync. To get it, click "Share" in the top right corner of the Google Sheets interface, and then click Copy Link in the dialog that pops up.

## Step 2: Set up the Google Sheets destination connector in Airbyte

<!-- env:cloud -->
**For Airbyte Cloud:**

1. Select **Google Sheets** from the Source type dropdown and enter a name for this connector.
2. Select `Sign in with Google`.
3. Log in and Authorize to the Google account and click `Set up source`.
4. Copy the Google Sheet link to **Spreadsheet Link**
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**
 Authentication to Google Sheets is only available using OAuth for authentication. 
 
 1. Select **Google Sheets** from the Source type dropdown and enter a name for this connector.
2. Follow [Google's OAuth instructions](https://developers.google.com/identity/protocols/oauth2) to create an authentication app. You will need to grant the scopes described in the [Google Sheets API](https://developers.google.com/identity/protocols/oauth2/scopes#sheets). 
3. Copy your Client ID, Client secret, and Refresh Token from the previous step. 
4. Copy the Google Sheet link to **Spreadsheet Link**
<!-- /env:oss -->

### Output schema

Each worksheet in the selected spreadsheet will be the output as a separate source-connector stream. 

The output columns are re-ordered in alphabetical order. The output columns should **not** be reordered manually after the sync, as this could cause future syncs to fail.

All data is coerced to a `string` format in Google Sheets.
Any nested lists and objects will be formatted as a string rather than normal lists and objects. Further data processing is required if you require the data for downstream analysis.

Airbyte only supports replicating `Grid Sheets`, which means only text is replicated. Objects like charts or images cannot be synced. See the [Google Sheets API docs](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#SheetType) for more info on all available sheet types.

### Rate Limiting & Performance Considerations

The [Google API rate limit](https://developers.google.com/sheets/api/limits) is 60 requests per 60 seconds per user and 300 requests per 60 seconds per project, which will result in slow sync speeds. Airbyte batches requests to the API in order to efficiently pull data and respects these rate limits.

### <a name="limitations"></a>Limitations

Google Sheets imposes hard limits on the amount of data that can be synced. If you attempt to sync more data than is allowed, the sync will fail.

**Maximum of 10 Million Cells**

A Google Sheets document can contain a maximum of 10 million cells. These can be in a single worksheet or in multiple sheets.
If you already have reached the 10 million limit, it will not allow you to add more columns (and vice versa, i.e., if the 10 million cells limit is reached with a certain number of rows, it will not allow more rows).

**Maximum of 50,000 characters per cell**

There can be at most 50,000 characters per cell. Do not use Google Sheets if you have fields with long text in your source.

**Maximum of 18,278 Columns**

There can be at most 18,278 columns in Google Sheets in a worksheet.

**Maximum of 200 Worksheets in a Spreadsheet**

You cannot create more than 200 worksheets within single spreadsheet.

Syncs will fail if any of these limits are reached.

#### Note:

- The underlying process of record normalization is applied to avoid data corruption during the write process. This handles two scenarios:

1. UnderSetting - when record has less keys (columns) than catalog declares
2. OverSetting - when record has more keys (columns) than catalog declares

```
EXAMPLE:

- UnderSetting:
    * Catalog:
        - has 3 entities:
            [ 'id', 'key1', 'key2' ]
                        ^
    * Input record:
        - missing 1 entity, compare to catalog
            { 'id': 123,    'key2': 'value' }
                            ^
    * Result:
        - 'key1' has been added to the record, because it was declared in catalog, to keep the data structure.
            {'id': 123, 'key1': '', {'key2': 'value'} }
                            ^
- OverSetting:
    * Catalog:
        - has 3 entities:
            [ 'id', 'key1', 'key2',   ]
                                    ^
    * Input record:
        - doesn't have entity 'key1'
        - has 1 more enitity, compare to catalog 'key3'
            { 'id': 123,     ,'key2': 'value', 'key3': 'value' }
                            ^                      ^
    * Result:
        - 'key1' was added, because it expected be the part of the record, to keep the data structure
        - 'key3' was dropped, because it was not declared in catalog, to keep the data structure
            { 'id': 123, 'key1': '', 'key2': 'value',   }
                            ^                          ^
```

### Data type mapping

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| Any Type         | `string`     |

### Features & Supported sync modes

| Feature                        | Supported?\(Yes/No\) |
| :----------------------------- | :------------------- |
| Ful-Refresh Overwrite          | Yes                  |
| Ful-Refresh Append             | Yes                  |
| Incremental Append             | Yes                  |
| Incremental Append-Deduplicate | Yes                  |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                        |
|---------|------------|----------------------------------------------------------|------------------------------------------------|
| 0.2.3   | 2023-09-25 | [30748](https://github.com/airbytehq/airbyte/pull/30748) | Performance testing - include socat binary in docker image |
| 0.2.2   | 2023-07-06 | [28035](https://github.com/airbytehq/airbyte/pull/28035) | Migrate from authSpecification to advancedAuth |
| 0.2.1   | 2023-06-26 | [27782](https://github.com/airbytehq/airbyte/pull/27782) | Only allow HTTPS urls                          |
| 0.2.0   | 2023-06-26 | [27780](https://github.com/airbytehq/airbyte/pull/27780) | License Update: Elv2                           |
| 0.1.2   | 2022-10-31 | [18729](https://github.com/airbytehq/airbyte/pull/18729) | Fix empty headers list                         |
| 0.1.1   | 2022-06-15 | [14751](https://github.com/airbytehq/airbyte/pull/14751) | Yield state only when records saved            |
| 0.1.0   | 2022-04-26 | [12135](https://github.com/airbytehq/airbyte/pull/12135) | Initial Release                                |
