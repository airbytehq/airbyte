# Smartsheets

### Table of Contents

* [Sync Details](smartsheets.md#sync-details)
  * [Column datatype mapping](smartsheets.md#column-datatype-mapping)
  * [Features](smartsheets.md#Features)
  * [Additional Metadata Options](smartsheets.md#additional-metadata-options)
  * [Connection Debugging Log Options](smartsheets.md#connection-debugging-log-options)
  * [Performance Considerations](smartsheets.md#performance-considerations)
* [Getting Started](smartsheets.md#getting-started)
  * [Requirements](smartsheets.md#requirements)
  * [Setup Guide](smartsheets.md#setup-guide)
  * [Configuring the source in the Airbyte UI](smartsheets.md#configuring-the-source-in-the-airbyte-ui)

## Sync Details

The Smartsheet Source is written to pull data from a single Smartsheet spreadsheet. Unlike Google Sheets, Smartsheets only allows one sheet per Smartsheet - so a given Airbyte connector instance can sync only one sheet at a time.

To replicate multiple spreadsheets, you can create multiple instances of the Smartsheet Source in Airbyte, reusing the API token for all your sheets that you need to sync.

**Note: Column headers must contain only alphanumeric characters or `_` , as specified in the** [**Airbyte Protocol**](../../understanding-airbyte/airbyte-specification.md).

### Column datatype mapping

The data type mapping adopted by this connector is based on the Smartsheet [documentation](https://smartsheet.redoc.ly/tag/columnsRelated#section/Column-Types).

**NOTE**: For any column datatypes interpreted by Smartsheets beside `DATE` and `DATETIME`, this connector's source schema generation assumes a `string` type, in which case the `format` field is not required by Airbyte.

| Smartsheets Column Type | SS API Column Type | Airbyte Type | Airbyte Format |
| :--- | :--- | :--- | :--- |
| Text/Number |`TEXT_NUMBER` | `string` |  |
| Date |`DATE` | `string` | `format: date` |
| Date/Time |`DATETIME` | `string` | `format: date-time` |
| Checkbox |`CHECKBOX` | `string` |  |
| Symbols... |`PICKLIST` | `string` |  |
| Contact List (Single) |`CONTACT_LIST` | `string` |  |
| Contact List (Multi) |`MULTI_CONTACT_LIST` | `string` | |
| Dropdown (Single Select) |`PICKLIST` | `string` | |
| Dropdown (Multi Select) |`MULTI_PICKLIST` | `string` | |
| Auto-Number |`TEXT_NUMBER` | `string` | |
| Modified (Date) / Created (Date)| `DATETIME` | `string` | `format: date-time` |
| Modified By / Created By |`TEXT_NUMBER` | `string` | |
| Predecessor | `TEXT_NUMBER` | `string` | |

Any column types not listed here are supported as `string` representations.

### Features

This source connector currently only supports Full Refresh Sync. Since Smartsheets only allows a max of 20,000 rows or 500,000 cells per sheet, it's likely that the Full Refresh Sync Mode will suit the majority of use-cases.

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Namespaces | No |

### Additonal Metadata Options

There are additional Sheet and Row metadata values can be added to each record outputted from Smartsheets.  Here are the options in the "Connection" Settings panel.

`Note: It will be necessary to "Update latest source schema" in the connection settings after any option changes, before these fields will populate in the destination`
| Option | Description |
| :--- | :--- |
| Include Internal Row ID | This adds the unique row ID value `_ss_row_id`.  Note that it this is not the same as the row number or any configured Auto-Number field.  Row ID's are internal to each sheet and do not change once a row is created.  Row numbers change with sort order, while auto-number columns are user configurable. |
| Include Extended Row Metadata | Adds several timestamps, the row number, and the parent/sibling row ID's.  `_ss_row_created_at`, `_ss_row_modified_at`,`_ss_row_number`,`_ss_row_parent_id`,`_ss_row_sibling_id` |
| Include Row Permalink | Adds the direct ROW-level permalink URL in the field `_ss_row_permalink` |
| Include Sheet ID and Name | Adds the smartsheet sheet ID and the Sheet Name to each row: `_ss_sheet_id`, `_ss_sheet_name`.  This is handy for destinations that may combine data from multiple sheets (outside of Airbyte) |
| Include Extended Sheet Metadata | Adds several sheet-level extended metadata items to each output record:  `_ss_sheet_version`,`_ss_sheet_permalink`,`_sheet_created_at`,`_sheet_modified_at`.
| Include Workspace ID and Name | This includes the workspace information that the sheet is located in, with each record: `_ss_workspace_id`,`_ss_workspace_name`.  If this option is on and the sheet is not in a workspace, it will return an empty string for the name and a null integer (none). |

### Connection Debugging Log Options

Two additional settings are available for the connection, that will log information directly to the run logs to help with diagnosis of source-destination issues.

| Option | Description |
| :--- | :--- |
| Enable Row Data Logging | This option will output the "raw" json data for each row, to a line in the connector run log, as well as a line containing the configured JSON schema and type maps. See sample below of each.
| Maxium number of Row Data Entries to record in logger | This will set the maximum number of rows for which data will be logged in the run log.  The default is 10.  It is recommended to keep this number low to minimize log depth, as most issues can be diagnosed with a subset of the total sheet.  This option requires the `Enable Row Data Logging` option (above) to be `TRUE`/enabled.


Example of JSON Schema log entry:

`2022-02-09 17:56:07 source > DEBUG: Configured JSON schema {'Date': {'type': 'string', 'format': 'date'}, 'CreateBy': {'type': 'string'}, 'CreateDate': {'type': 'string', 'format': 'date-time'}, '_ss_row_id': {'type': 'integer'}, 'ContactList': {'type': 'string'}, '_ss_sheet_id': {'type': 'integer'}, 'MultiPickTest': {'type': 'string'}, 'SinglePickTest': {'type': 'string'}, '_ss_row_number': {'type': 'string'}, '_ss_sheet_name': {'type': 'string'}, 'MultiContactList': {'type': 'string'}, '_ss_workspace_id': {'type': 'integer'}, '_ss_row_parent_id': {'type': 'integer'}, '_ss_row_permalink': {'type': 'string'}`

Example of Row Data Log entry:

`2022-02-09 17:56:07 source > SOURCE SETTINGS DEBUG: Airbyte Row # 1, SS Row ID: 5514951936370564 - Row Data: {'primary': 'primary1', 'Column2': 2.0, 'Column3': 3.0, 'Column4': 4.0, 'Column5': 5.0, 'Column6': 6.0, 'SinglePickTest': 'Test1'}`


### Performance considerations

At the time of writing, the [Smartsheets API rate limit](https://developers.smartsheet.com/blog/smartsheet-api-best-practices#:~:text=The%20Smartsheet%20API%20currently%20imposes,per%20minute%20per%20Access%20Token.) is 300 requests per minute per API access token. This connector makes 6 API calls per sync operation.

## Getting started

### Requirements

To configure the Smartsheet Source for syncs, you'll need the following:

* A Smartsheets API access token - generated by a Smartsheets user with at least **read** access
* The ID of the spreadsheet you'd like to sync

### Setup guide

#### Obtain a Smartsheets API access token

You can generate an API key for your account from a session of your Smartsheet webapp by clicking:

* Account \(top-right icon\)
* Apps & Integrations
* API Access
* Generate new access token

For questions on advanced authorization flows, refer to [this](https://www.smartsheet.com/content-center/best-practices/tips-tricks/api-getting-started).

#### The spreadsheet ID of your Smartsheet

You'll also need the ID of the Spreadsheet you'd like to sync. Unlike Google Sheets, this ID is not found in the URL. You can find the required spreadsheet ID from your Smartsheet app session by going to:

* File
* Properties

### Configuring the source in the Airbyte UI

To setup your new Smartsheets source, Airbyte will need:

1. Your API access token
2. The spreadsheet ID

## Changelog

| Version | Date       | Pull Request | Subject             |
|:--------|:-----------| :--- |:--------------------|
| 0.1.8   | 2022-02-04 | [9792](https://github.com/airbytehq/airbyte/pull/9792) | Added oauth support |
| 0.1.9   | 2022-02-09 | [10222](https://github.com/airbytehq/airbyte/pull/10222) | Fixes [#8099](https://github.com/airbytehq/airbyte/issues/8099)|
| 0.2.0   | 2022-02-09 | [ ]() | Adds extended metadata schema options and debug logging support to source settings |


