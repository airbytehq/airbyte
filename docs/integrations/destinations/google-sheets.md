# Google Sheets

## Sync overview

The Google Sheets Destination is configured to push data to a single Google Sheets spreadsheet with multiple Worksheets as streams. To replicate data to multiple spreadsheets, you can create multiple instances of the Google Sheets Destination in your Airbyte instance.
Please be aware of the [Google Spreadsheet limitations](#limitations) before you configure your airbyte data replication using Destination Google Sheets

### Output schema

Each worksheet in the selected spreadsheet will be the output as a separate source-connector stream. The data is coerced to string before the output to the spreadsheet. The nested data inside of the source connector data is normalized to the `first-level-nesting` and represented as string, this produces nested lists and objects to be a string rather than normal lists and objects, the further data processing is required if you need to analyze the data.

Airbyte only supports replicating `Grid Sheets`, which means the text raw data only could be replicated to the target spreadsheet. See the [Google Sheets API docs](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#SheetType) for more info on all available sheet types.


### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| Any Type | `string` |  |

### Features

| Feature | Supported?\(Yes/No\) |
| :--- | :--- |
| Ful-Refresh Overwrite | Yes |
| Ful-Refresh Append | Yes |
| Incremental Append | Yes |
| Incremental Append-Deduplicate | Yes |

### Performance considerations

At the time of writing, the [Google API rate limit](https://developers.google.com/sheets/api/limits) is 100 requests per 100 seconds per user and 500 requests per 100 seconds per project. Airbyte batches requests to the API in order to efficiently pull data and respects these rate limits. It is recommended that you use the same service user \(see the "Creating a service user" section below for more information on how to create one\) for no more than 3 instances of the Google Sheets Destination to ensure high transfer speeds.

### <a name="limitations"></a>Google Sheets Limitations

During the upload process and from the data storage perspective there are some limitations that should be considered beforehands:
* **Maximum of 5 Million Cells**

A Google Sheets document can have a maximum of 5 million cells. These can be in a single worksheet or in multiple sheets.
In case you already have the 5 million limit reached in fewer columns, it will not allow you to add more columns (and vice versa, i.e., if 5 million cells limit is reached with a certain number of rows, it will not allow more rows).

* **Maximum of 18,278 Columns**

At max, you can have 18,278 columns in Google Sheets in a worksheet.

* **Up to 200 Worksheets in a Spreadsheet**

You cannot create more than 200 worksheets within single spreadsheet.


## Getting Started (Airbyte Cloud Only)
To configure the connector you'll need to:

* [Authorize your Google account via OAuth](#oauth)
* [The Full URL or Spreadsheet ID you'd like to sync](#sheetlink)

### <a name="oauth"></a> Authorize your Google account via OAuth
Click on the "Sign in with Google" button and authorize via your Google account.

### <a name="sheetlink"></a>Spreadsheet Link
You will need the link of the Spreadsheet you'd like to sync. To get it, click Share button in the top right corner of Google Sheets interface, and then click Copy Link in the dialog that pops up.
These two steps are highlighted in the screenshot below:

![](../../.gitbook/assets/google_spreadsheet_url.png)


#### Future improvements:
- Handle multiple spreadsheets to split big amount of data into parts, once the main spreadsheet is full and cannot be extended more, due to [limitations](#limitations).
- Support of Airbyte OSS version with Service Account, currently the Airbyte Cloud supported only.

## Changelog

| Version | Date       | Pull Request                                               | Subject                                                                       |
|---------|------------|------------------------------------------------------------|-------------------------------------------------------------------------------|
| 0.1.0  | 2022-04-26 | []()   | Initial Release                         |
