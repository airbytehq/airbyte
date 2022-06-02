# Google Sheets

This page guides you through the process of setting up the Google Sheets source connector.

:::info
The Google Sheets source connector pulls data from a single Google Sheets spreadsheet. To replicate multiple spreadsheets, set up multiple Google Sheets source connectors in your Airbyte instance.
:::

## Set up Google Sheets as a source in Airbyte 

### For Airbyte Cloud

To set up Google Sheets as a source in Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Google Sheets** from the Source type dropdown. 
4. For Name, enter a name for the Google Sheets connector. 
5. Authenticate your Google account via OAuth or Service Account Key Authentication. 
    - **(Recommended)** To authenticate your Google account via OAuth, click **Sign in with Google** and complete the authentication workflow.
    - To authenticate your Google account via Service Account Key Authentication, enter your [Google Cloud service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys) in JSON format. Make sure the Service Account has the Project Viewer permission.
6. For Spreadsheet Link, enter the link to the Google spreadsheet. To get the link, go to the Google spreadsheet you want to sync, click **Share** in the top right corner, and click **Copy Link**. 

### For Airbyte OSS

To set up Google Sheets as a source in Airbyte OSS:

1. [Enable the Google Cloud Platform APIs for your personal or organization account](https://support.google.com/googleapi/answer/6158841?hl=en).

    :::info
    The connector only finds the spreadsheet you want to replicate; it does not access any of your other files in Google Drive.
    :::

2. Go to the Airbyte UI and in the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Google Sheets** from the Source type dropdown. 
4. For Name, enter a name for the Google Sheets connector. 
5. Authenticate your Google account via OAuth or Service Account Key Authentication:
    - To authenticate your Google account via OAuth, enter your Google application's [client ID, client secret, and refresh token](https://developers.google.com/identity/protocols/oauth2).
    - To authenticate your Google account via Service Account Key Authentication, enter your [Google Cloud service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys) in JSON format. Make sure the Service Account has the Project Viewer permission.
6. For Spreadsheet Link, enter the link to the Google spreadsheet. To get the link, go to the Google spreadsheet you want to sync, click **Share** in the top right corner, and click **Copy Link**.     
    
--------------------
    3̶.̶ 


    T̶o̶ a̶u̶t̶h̶e̶n̶t̶i̶c̶a̶t̶e̶ y̶o̶u̶r̶ G̶o̶o̶g̶l̶e̶ a̶c̶c̶o̶u̶n̶t̶ v̶i̶a̶ S̶e̶r̶v̶i̶c̶e̶ A̶c̶c̶o̶u̶n̶t̶ K̶e̶y̶ A̶u̶t̶h̶e̶n̶t̶i̶c̶a̶t̶i̶o̶n̶:̶
    1̶.̶ C̶r̶e̶a̶t̶e̶ a̶ s̶e̶r̶v̶i̶c̶e̶ a̶c̶c̶o̶u̶n̶t̶ a̶n̶d̶ k̶e̶y̶ t̶o̶ a̶c̶c̶e̶s̶s̶ t̶h̶e̶ G̶o̶o̶g̶l̶e̶ S̶h̶e̶e̶t̶s̶ A̶P̶I̶s̶:̶ b̶y̶ f̶o̶l̶l̶o̶w̶i̶n̶g̶ t̶h̶e̶ i̶n̶s̶t̶r̶u̶c̶t̶i̶o̶n̶s̶ i̶n̶ [̶S̶e̶r̶v̶i̶c̶e̶ a̶c̶c̶o̶u̶n̶t̶s̶,̶ w̶e̶b̶ a̶p̶p̶l̶i̶c̶a̶t̶i̶o̶n̶s̶,̶ a̶n̶d̶ n̶a̶t̶i̶v̶e̶ a̶p̶p̶l̶i̶c̶a̶t̶i̶o̶n̶s̶]̶(̶h̶t̶t̶p̶s̶:̶/̶/̶s̶u̶p̶p̶o̶r̶t̶.̶g̶o̶o̶g̶l̶e̶.̶c̶o̶m̶/̶g̶o̶o̶g̶l̶e̶a̶p̶i̶/̶a̶n̶s̶w̶e̶r̶/̶6̶1̶5̶8̶8̶4̶9̶?̶h̶l̶=̶e̶n̶&̶r̶e̶f̶_̶t̶o̶p̶i̶c̶=̶7̶0̶1̶3̶2̶7̶9̶#̶z̶)̶
        1̶.̶ G̶o̶ t̶o̶ t̶h̶e̶ [̶A̶P̶I̶ C̶o̶n̶s̶o̶l̶e̶ C̶r̶e̶d̶e̶n̶t̶i̶a̶l̶s̶ p̶a̶g̶e̶]̶(̶h̶t̶t̶p̶s̶:̶/̶/̶c̶o̶n̶s̶o̶l̶e̶.̶d̶e̶v̶e̶l̶o̶p̶e̶r̶s̶.̶g̶o̶o̶g̶l̶e̶.̶c̶o̶m̶/̶a̶p̶i̶s̶/̶c̶r̶e̶d̶e̶n̶t̶i̶a̶l̶s̶)̶.̶
        2̶.̶ S̶e̶l̶e̶c̶t̶ t̶h̶e̶ p̶r̶o̶j̶e̶c̶t̶ t̶h̶a̶t̶ y̶o̶u̶'̶r̶e̶ c̶r̶e̶a̶t̶i̶n̶g̶ c̶r̶e̶d̶e̶n̶t̶i̶a̶l̶s̶ f̶o̶r̶.̶
        3̶.̶ T̶o̶ s̶e̶t̶ u̶p̶ a̶ n̶e̶w̶ s̶e̶r̶v̶i̶c̶e̶ a̶c̶c̶o̶u̶n̶t̶,̶ c̶l̶i̶c̶k̶ *̶*̶C̶r̶e̶a̶t̶e̶ C̶r̶e̶d̶e̶n̶t̶i̶a̶l̶s̶*̶*̶ a̶n̶d̶ s̶e̶l̶e̶c̶t̶ *̶*̶S̶e̶r̶v̶i̶c̶e̶ a̶c̶c̶o̶u̶n̶t̶*̶*̶.̶
        4̶.̶ S̶e̶l̶e̶c̶t̶ t̶h̶e̶ s̶e̶r̶v̶i̶c̶e̶ a̶c̶c̶o̶u̶n̶t̶ t̶o̶ u̶s̶e̶ f̶o̶r̶ t̶h̶e̶ k̶e̶y̶.̶
        5̶.̶ G̶r̶a̶n̶t̶ t̶h̶e̶ s̶e̶r̶v̶i̶c̶e̶ a̶c̶c̶o̶u̶n̶t̶ t̶h̶e̶ r̶o̶l̶e̶ o̶f̶ P̶r̶o̶j̶e̶c̶t̶ V̶i̶e̶w̶e̶r̶.̶
        6̶.̶ D̶o̶w̶n̶l̶o̶a̶d̶ t̶h̶e̶ s̶e̶r̶v̶i̶c̶e̶ a̶c̶c̶o̶u̶n̶t̶'̶s̶ p̶u̶b̶l̶i̶c̶/̶p̶r̶i̶v̶a̶t̶e̶ k̶e̶y̶ a̶s̶ a̶ J̶S̶O̶N̶ f̶i̶l̶e̶.̶
    2̶.̶ G̶i̶v̶e̶ t̶h̶e̶ s̶e̶r̶v̶i̶c̶e̶ a̶c̶c̶o̶u̶n̶t̶ a̶c̶c̶e̶s̶s̶ t̶o̶ t̶h̶e̶ s̶p̶r̶e̶a̶d̶s̶h̶e̶e̶t̶ y̶o̶u̶ w̶a̶n̶t̶ t̶o̶ s̶y̶n̶c̶.̶ I̶f̶ y̶o̶u̶r̶ s̶p̶r̶e̶a̶d̶s̶h̶e̶e̶t̶ i̶s̶ v̶i̶e̶w̶a̶b̶l̶e̶ b̶y̶ a̶n̶y̶o̶n̶e̶,̶ n̶o̶ f̶u̶r̶t̶h̶e̶r̶ a̶c̶t̶i̶o̶n̶ i̶s̶ r̶e̶q̶u̶i̶r̶e̶d̶.̶ I̶f̶ n̶o̶t̶,̶ t̶h̶e̶n̶ d̶o̶ t̶h̶e̶ f̶o̶l̶l̶o̶w̶i̶n̶g̶:̶
        1̶.̶ G̶o̶ t̶o̶ t̶h̶e̶ G̶o̶o̶g̶l̶e̶ A̶P̶I̶ D̶a̶s̶h̶b̶o̶a̶r̶d̶.̶ I̶n̶ t̶h̶e̶ *̶*̶C̶r̶e̶d̶e̶n̶t̶i̶a̶l̶s̶*̶*̶ t̶a̶b̶,̶ c̶o̶p̶y̶ t̶h̶e̶ e̶m̶a̶i̶l̶ a̶d̶d̶r̶e̶s̶s̶ o̶f̶ t̶h̶e̶ s̶e̶r̶v̶i̶c̶e̶ a̶c̶c̶o̶u̶n̶t̶ y̶o̶u̶ c̶r̶e̶a̶t̶e̶d̶ i̶n̶ S̶t̶e̶p̶ 2̶.̶ 
        3̶.̶ G̶o̶ t̶o̶ t̶h̶e̶ G̶o̶o̶g̶l̶e̶ s̶p̶r̶e̶a̶d̶s̶h̶e̶e̶t̶ y̶o̶u̶ w̶a̶n̶t̶ t̶o̶ s̶y̶n̶c̶,̶ c̶l̶i̶c̶k̶ *̶*̶S̶h̶a̶r̶e̶*̶*̶,̶ a̶n̶d̶ s̶h̶a̶r̶e̶ t̶h̶e̶ s̶p̶r̶e̶a̶d̶s̶h̶e̶e̶t̶ w̶i̶t̶h̶ t̶h̶e̶ s̶e̶r̶v̶i̶c̶e̶ a̶c̶c̶o̶u̶n̶t̶.̶
    3̶.̶ G̶o̶ t̶o̶ t̶h̶e̶ A̶i̶r̶b̶y̶t̶e̶ C̶l̶o̶u̶d̶ U̶I̶ a̶n̶d̶ e̶n̶t̶e̶r̶ t̶h̶e̶ S̶e̶r̶v̶i̶c̶e̶ A̶c̶c̶o̶u̶n̶t̶ J̶S̶O̶N̶ k̶e̶y̶.̶

--------------------

### Output schema

Each sheet in the selected spreadsheet is synced as a separate stream. Each selected column in the sheet is synced as a string field.

**Note: Sheet names and column headers must contain only alphanumeric characters or `_`, as specified in the** [**Airbyte Protocol**](../../understanding-airbyte/airbyte-specification.md). For example, if your sheet or column header is named `the data`, rename it to `the_data`. This restriction does not apply to non-header cell values. 

Airbyte only supports replicating [Grid](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#SheetType) sheets. 

## Supported sync modes

The Google Sheets source connector supports the following sync modes:

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/glossary#full-refresh-sync)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

## Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| any type | `string` |  |


## Performance consideration

The [Google API rate limit](https://developers.google.com/sheets/api/limits) is 100 requests per 100 seconds per user and 500 requests per 100 seconds per project. Airbyte batches requests to the API in order to efficiently pull data and respects these rate limits. We recommended not using the same service user for more than 3 instances of the Google Sheets source connector to ensure high transfer speeds.


## Changelog

| Version | Date       | Pull Request                                               | Subject                                                                       |
|---------|------------|------------------------------------------------------------|-------------------------------------------------------------------------------|
| 0.2.15  | 2022-06-02 | [13446](https://github.com/airbytehq/airbyte/pull/13446)   | Retry requests resulting in a server error                                    |
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
