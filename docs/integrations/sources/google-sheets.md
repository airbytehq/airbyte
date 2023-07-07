# Google Sheets

This page guides you through the process of setting up the Google Sheets source connector.

:::info
The Google Sheets source connector pulls data from a single Google Sheets spreadsheet. To replicate multiple spreadsheets, set up multiple Google Sheets source connectors in your Airbyte instance.
:::

## Setup guide

<!-- env:cloud -->

**For Airbyte Cloud:**

To set up Google Sheets as a source in Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Google Sheets** from the **Source type** dropdown.
4. Enter a name for the Google Sheets connector.
5. Authenticate your Google account via OAuth or Service Account Key Authentication.
   - **(Recommended)** To authenticate your Google account via OAuth, click **Sign in with Google** and complete the authentication workflow.
   - To authenticate your Google account via Service Account Key Authentication, enter your [Google Cloud service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys) in JSON format. Make sure the Service Account has the Project Viewer permission. If your spreadsheet is viewable by anyone with its link, no further action is needed. If not, [give your Service account access to your spreadsheet](https://youtu.be/GyomEw5a2NQ%22).
6. For **Spreadsheet Link**, enter the link to the Google spreadsheet. To get the link, go to the Google spreadsheet you want to sync, click **Share** in the top right corner, and click **Copy Link**.
7. For **Row Batch Size**, define the number of records you want the Google API to fetch at a time. The default value is 200.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

To set up Google Sheets as a source in Airbyte Open Source:

1. [Enable the Google Cloud Platform APIs for your personal or organization account](https://support.google.com/googleapi/answer/6158841?hl=en).

   :::info
   The connector only finds the spreadsheet you want to replicate; it does not access any of your other files in Google Drive.
   :::

2. Go to the Airbyte UI and in the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Google Sheets** from the Source type dropdown.
4. Enter a name for the Google Sheets connector.
5. Authenticate your Google account via OAuth or Service Account Key Authentication:
   - To authenticate your Google account via OAuth, enter your Google application's [client ID, client secret, and refresh token](https://developers.google.com/identity/protocols/oauth2).
   - To authenticate your Google account via Service Account Key Authentication, enter your [Google Cloud service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys) in JSON format. Make sure the Service Account has the Project Viewer permission. If your spreadsheet is viewable by anyone with its link, no further action is needed. If not, [give your Service account access to your spreadsheet](https://youtu.be/GyomEw5a2NQ%22).
6. For **Spreadsheet Link**, enter the link to the Google spreadsheet. To get the link, go to the Google spreadsheet you want to sync, click **Share** in the top right corner, and click **Copy Link**.

### Output schema

Each sheet in the selected spreadsheet is synced as a separate stream. Each selected column in the sheet is synced as a string field.

**Note: Sheet names and column headers must contain only alphanumeric characters or `_`, as specified in the** [**Airbyte Protocol**](../../understanding-airbyte/airbyte-protocol.md). For example, if your sheet or column header is named `the data`, rename it to `the_data`. This restriction does not apply to non-header cell values.

Airbyte only supports replicating [Grid](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#SheetType) sheets.

<!-- env:oss -->

## Supported sync modes

The Google Sheets source connector supports the following sync modes:

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

## Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| any type         | `string`     |       |

## Performance consideration

The [Google API rate limit](https://developers.google.com/sheets/api/limits) is 100 requests per 100 seconds per user and 500 requests per 100 seconds per project. Airbyte batches requests to the API in order to efficiently pull data and respects these rate limits. We recommended not using the same service user for more than 3 instances of the Google Sheets source connector to ensure high transfer speeds.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                       |
| ------- | ---------- | -------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 0.3.0   | 2023-06-26 | [27738](https://github.com/airbytehq/airbyte/pull/27738) | License Update: Elv2                                                          |
| 0.2.39  | 2023-05-31 | [26833](https://github.com/airbytehq/airbyte/pull/26833) | Remove authSpecification in favour of advancedAuth in specification           |
| 0.2.38  | 2023-05-16 | [26097](https://github.com/airbytehq/airbyte/pull/26097) | Refactor config error                                                         |
| 0.2.37  | 2023-02-21 | [23292](https://github.com/airbytehq/airbyte/pull/23292) | Skip non grid sheets.                                                         |
| 0.2.36  | 2023-02-21 | [23272](https://github.com/airbytehq/airbyte/pull/23272) | Handle empty sheets gracefully.                                               |
| 0.2.35  | 2023-02-23 | [23057](https://github.com/airbytehq/airbyte/pull/23057) | Slugify column names                                                          |
| 0.2.34  | 2023-02-15 | [23071](https://github.com/airbytehq/airbyte/pull/23071) | Change min spreadsheet id size to 20 symbols                                  |
| 0.2.33  | 2023-02-13 | [23278](https://github.com/airbytehq/airbyte/pull/23278) | Handle authentication errors                                                  |
| 0.2.32  | 2023-02-13 | [22884](https://github.com/airbytehq/airbyte/pull/22884) | Do not consume http spreadsheets.                                             |
| 0.2.31  | 2022-10-09 | [19574](https://github.com/airbytehq/airbyte/pull/19574) | Revert 'Add row_id to rows and use as primary key'                            |
| 0.2.30  | 2022-10-09 | [19215](https://github.com/airbytehq/airbyte/pull/19215) | Add row_id to rows and use as primary key                                     |
| 0.2.21  | 2022-10-04 | [15591](https://github.com/airbytehq/airbyte/pull/15591) | Clean instantiation of AirbyteStream                                          |
| 0.2.20  | 2022-10-10 | [17766](https://github.com/airbytehq/airbyte/pull/17766) | Fix null pointer exception when parsing the spreadsheet id.                   |
| 0.2.19  | 2022-09-29 | [17410](https://github.com/airbytehq/airbyte/pull/17410) | Use latest CDK.                                                               |
| 0.2.18  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states.                                                 |
| 0.2.17  | 2022-08-03 | [15107](https://github.com/airbytehq/airbyte/pull/15107) | Expose Row Batch Size in Connector Specification                              |
| 0.2.16  | 2022-07-07 | [13729](https://github.com/airbytehq/airbyte/pull/13729) | Improve configuration field description                                       |
| 0.2.15  | 2022-06-02 | [13446](https://github.com/airbytehq/airbyte/pull/13446) | Retry requests resulting in a server error                                    |
| 0.2.13  | 2022-05-06 | [12685](https://github.com/airbytehq/airbyte/pull/12685) | Update CDK to v0.1.56 to emit an `AirbyeTraceMessage` on uncaught exceptions  |
| 0.2.12  | 2022-04-20 | [12230](https://github.com/airbytehq/airbyte/pull/12230) | Update connector to use a `spec.yaml`                                         |
| 0.2.11  | 2022-04-13 | [11977](https://github.com/airbytehq/airbyte/pull/11977) | Replace leftover print statement with airbyte logger                          |
| 0.2.10  | 2022-03-25 | [11404](https://github.com/airbytehq/airbyte/pull/11404) | Allow using Spreadsheet Link/URL instead of Spreadsheet ID                    |
| 0.2.9   | 2022-01-25 | [9208](https://github.com/airbytehq/airbyte/pull/9208)   | Update title and descriptions                                                 |
| 0.2.7   | 2021-09-27 | [8470](https://github.com/airbytehq/airbyte/pull/8470)   | Migrate to the CDK                                                            |
| 0.2.6   | 2021-09-27 | [6354](https://github.com/airbytehq/airbyte/pull/6354)   | Support connecting via Oauth webflow                                          |
| 0.2.5   | 2021-09-12 | [5972](https://github.com/airbytehq/airbyte/pull/5972)   | Fix full_refresh test by adding supported_sync_modes to Stream initialization |
| 0.2.4   | 2021-08-05 | [5233](https://github.com/airbytehq/airbyte/pull/5233)   | Fix error during listing sheets with diagram only                             |
| 0.2.3   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Add AIRBYTE_ENTRYPOINT for Kubernetes support                                 |
| 0.2.2   | 2021-04-20 | [2994](https://github.com/airbytehq/airbyte/pull/2994)   | Formatting spec                                                               |
| 0.2.1   | 2021-04-03 | [2726](https://github.com/airbytehq/airbyte/pull/2726)   | Fix base connector versioning                                                 |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238)   | Protocol allows future/unknown properties                                     |
| 0.1.7   | 2021-01-21 | [1762](https://github.com/airbytehq/airbyte/pull/1762)   | Fix issue large spreadsheet                                                   |
| 0.1.6   | 2021-01-27 | [1668](https://github.com/airbytehq/airbyte/pull/1668)   | Adopt connector best practices                                                |
| 0.1.5   | 2020-12-30 | [1438](https://github.com/airbytehq/airbyte/pull/1438)   | Implement backoff                                                             |
| 0.1.4   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046)   | Add connectors using an index YAML file                                       |

<!-- /env:oss -->
