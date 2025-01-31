# Google Sheets

<HideInUI>

This page contains the setup guide and reference information for the [Google Sheets](https://developers.google.com/sheets) source connector.

</HideInUI>

:::info
The Google Sheets source connector pulls data from a single Google Sheets spreadsheet. Each sheet within a spreadsheet can be synced. To sync multiple spreadsheets, use our Google Drive connector or set up multiple Google Sheets source connectors in your Airbyte instance. No other files in your Google Drive are accessed.
:::

### Prerequisites

- **Spreadsheet Link** - The link to the Google spreadsheet you want to sync.
<!-- env:cloud -->
- **For Airbyte Cloud** A Google Workspace user with access to the spreadsheet
<!-- /env:cloud -->
  <!-- env:oss -->
- **For Airbyte Open Source:**
- A GCP project
- Enable the Google Sheets API in your GCP project
- Service Account Key with access to the Spreadsheet you want to replicate
<!-- /env:oss -->

## Setup guide

The Google Sheets source connector supports authentication via either OAuth or Service Account Key Authentication.

### Step 1: Set up Google Sheets

<!-- env:cloud -->

**For Airbyte Cloud:**

We highly recommend using OAuth, as it significantly simplifies the setup process and allows you to authenticate [directly from the Airbyte UI](#set-up-the-google-sheets-source-connector-in-airbyte).

<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

We recommend using Service Account Key Authentication. Follow the steps below to create a service account, generate a key, and enable the Google Sheets API.

:::note
If you prefer to use OAuth for authentication with **Airbyte Open Source**, you can follow [Google's OAuth instructions](https://developers.google.com/identity/protocols/oauth2) to create an authentication app. Be sure to set the scopes to `https://www.googleapis.com/auth/spreadsheets.readonly`. You will need to obtain your client ID, client secret, and refresh token for the connector setup.
:::

### Set up the service account key

#### Create a service account

1. Open the [Service Accounts page](https://console.cloud.google.com/projectselector2/iam-admin/serviceaccounts) in your Google Cloud console.
2. Select an existing project, or create a new project.
3. At the top of the page, click **+ Create service account**.
4. Enter a name and description for the service account, then click **Create and Continue**.
5. Under **Service account permissions**, select the roles to grant to the service account, then click **Continue**. We recommend the **Viewer** role.

#### Generate a key

1. Go to the [API Console/Credentials](https://console.cloud.google.com/apis/credentials) page and click on the email address of the service account you just created.
2. In the **Keys** tab, click **+ Add key**, then click **Create new key**.
3. Select **JSON** as the Key type. This will generate and download the JSON key file that you'll use for authentication. Click **Continue**.

#### Enable the Google Sheets API

1. Go to the [API Console/Library](https://console.cloud.google.com/apis/library) page.
2. Make sure you have selected the correct project from the top.
3. Find and select the **Google Sheets API**.
4. Click **ENABLE**.

If your spreadsheet is viewable by anyone with its link, no further action is needed. If not, [give your Service account access to your spreadsheet](https://youtu.be/GyomEw5a2NQ%22).

<!-- /env:oss -->

### Set up the Google Sheets connector in Airbyte

<!-- env:cloud -->
#### For Airbyte Cloud: 

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Google Sheets from the Source type dropdown.
4. Enter a name for the Google Sheets connector.
<!-- /env:cloud -->
<!-- env:oss -->
### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Google Sheets from the Source type dropdown.
4. Enter a name for the Google Sheets connector.
<!-- /env:oss -->
5. Select your authentication method:
<!-- env:cloud -->
- **For Airbyte Cloud: (Recommended)** Select **Authenticate via Google (OAuth)** from the Authentication dropdown, click **Sign in with Google** and complete the authentication workflow.
  <!-- /env:cloud -->
  <!-- env:oss -->
- **For Airbyte Open Source: (Recommended)** Select **Service Account Key Authentication** from the dropdown and enter your Google Cloud service account key in JSON format:

```json
  {
    "type": "service_account",
    "project_id": "YOUR_PROJECT_ID",
    "private_key_id": "YOUR_PRIVATE_KEY",
    ...
  }
```

- To authenticate your Google account via OAuth, select **Authenticate via Google (OAuth)** from the dropdown and enter your Google application's client ID, client secret, and refresh token.
<!-- /env:oss -->
<FieldAnchor field="spreadsheet_id">
6. For **Spreadsheet Link**, enter the link to the Google spreadsheet. To get the link, go to the Google spreadsheet you want to sync, click **Share** in the top right corner, and click **Copy Link**.
</FieldAnchor>
<FieldAnchor field="batch_size">
7. For **Batch Size**, enter an integer which represents batch size when processing a Google Sheet. Default value is 1000000.
   Batch size is an integer representing row batch size for each sent request to Google Sheets API.
   Row batch size means how many rows are processed from the google sheet, for example default value 1000000
   would process rows 2-1000002, then 1000003-2000003 and so on.
   Based on [Google Sheets API limits documentation](https://developers.google.com/sheets/api/limits),
   it is possible to send up to 300 requests per minute, but each individual request has to be processed under 180 seconds,
   otherwise the request returns a timeout error. In regards to this information, consider network speed and
   number of columns of the google sheet when deciding a batch_size value.
</FieldAnchor>
<FieldAnchor field="names_conversion">
8. (Optional) You may enable the option to **Convert Column Names to SQL-Compliant Format**. Enabling this option will allow the connector to convert column names to a standardized, SQL-friendly format. For example, a column name of `Café Earnings 2022` will be converted to `cafe_earnings_2022`. We recommend enabling this option if your target destination is SQL-based (ie Postgres, MySQL). Set to false by default.
9. Click **Set up source** and wait for the tests to complete.
</FieldAnchor>
<HideInUI>

## Supported sync modes

The Google Sheets source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

### Supported Streams

Each sheet in the selected spreadsheet is synced as a separate stream. Each selected column in the sheet is synced as a string field.

Airbyte only supports replicating [Grid](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#SheetType) sheets.

## Data type map

Each sheet in the selected spreadsheet is synced as a separate stream. Each selected column in the sheet is synced as a string field.

Airbyte only supports replicating [Grid](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#SheetType) sheets.

| Integration Type | Airbyte Type | Notes |
|:-----------------|:-------------|:------|
| any type         | `string`     |       |

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Google Sheets connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

The [Google API rate limits](https://developers.google.com/sheets/api/limits) are:

- 300 read requests per minute per project
- 60 requests per minute per user per project

Airbyte batches requests to the API in order to efficiently pull data and respect these rate limits. We recommend not using the same user or service account for more than 3 instances of the Google Sheets source connector to ensure high transfer speeds.

### Troubleshooting

- If your sheet is completely empty (no header rows) or deleted, Airbyte will not delete the table in the destination. If this happens, the sync logs will contain a message saying the sheet has been skipped when syncing the full spreadsheet.
- Connector setup will fail if the spreadsheet is not a Google Sheets file. If the file was saved or imported as another file type the setup could fail.
- Check out common troubleshooting issues for the Google Sheets source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

</HideInUI>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version    | Date       | Pull Request                                             | Subject                                                                                                                                                                |
|------------|------------|----------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.9.0-rc.2 | 2025-01-31 | [52671](https://github.com/airbytehq/airbyte/pull/52671) | Fix sheet id encoding                                                                                                                                                  |
| 0.9.0-rc.1 | 2025-01-30 | [50843](https://github.com/airbytehq/airbyte/pull/50843) | Migrate to low-code                                                                                                                                                    |
| 0.8.5      | 2025-01-11 | [44270](https://github.com/airbytehq/airbyte/pull/44270) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.8.4      | 2024-12-09 | [48835](https://github.com/airbytehq/airbyte/pull/48835) | Implementing integration tests                                                                                                                                         |
| 0.7.4      | 2024-09-09 | [45108](https://github.com/airbytehq/airbyte/pull/45108) | Google Sheets API errors now cause syncs to fail                                                                                                                       |
| 0.7.3      | 2024-08-12 | [43921](https://github.com/airbytehq/airbyte/pull/43921) | Update dependencies                                                                                                                                                    |
| 0.7.2      | 2024-08-10 | [43544](https://github.com/airbytehq/airbyte/pull/43544) | Update dependencies                                                                                                                                                    |
| 0.7.1      | 2024-08-03 | [43290](https://github.com/airbytehq/airbyte/pull/43290) | Update dependencies                                                                                                                                                    |
| 0.7.0      | 2024-08-02 | [42975](https://github.com/airbytehq/airbyte/pull/42975) | Migrate to CDK v4.3.0                                                                                                                                                  |
| 0.6.3      | 2024-07-27 | [42826](https://github.com/airbytehq/airbyte/pull/42826) | Update dependencies                                                                                                                                                    |
| 0.6.2      | 2024-07-22 | [41993](https://github.com/airbytehq/airbyte/pull/41993) | Avoid syncs with rate limits being considered successful                                                                                                               |
| 0.6.1      | 2024-07-20 | [42376](https://github.com/airbytehq/airbyte/pull/42376) | Update dependencies                                                                                                                                                    |
| 0.6.0      | 2024-07-17 | [42071](https://github.com/airbytehq/airbyte/pull/42071) | Migrate to CDK v3.9.0                                                                                                                                                  |
| 0.5.11     | 2024-07-13 | [41527](https://github.com/airbytehq/airbyte/pull/41527) | Update dependencies                                                                                                                                                    |
| 0.5.10     | 2024-07-09 | [41273](https://github.com/airbytehq/airbyte/pull/41273) | Update dependencies                                                                                                                                                    |
| 0.5.9      | 2024-07-06 | [41005](https://github.com/airbytehq/airbyte/pull/41005) | Update dependencies                                                                                                                                                    |
| 0.5.8      | 2024-06-28 | [40587](https://github.com/airbytehq/airbyte/pull/40587) | Replaced deprecated AirbyteLogger with logging.Logger                                                                                                                  |
| 0.5.7      | 2024-06-25 | [40560](https://github.com/airbytehq/airbyte/pull/40560) | Catch an auth error during discover and raise a config error                                                                                                           |
| 0.5.6      | 2024-06-26 | [40533](https://github.com/airbytehq/airbyte/pull/40533) | Update dependencies                                                                                                                                                    |
| 0.5.5      | 2024-06-25 | [40505](https://github.com/airbytehq/airbyte/pull/40505) | Update dependencies                                                                                                                                                    |
| 0.5.4      | 2024-06-22 | [40129](https://github.com/airbytehq/airbyte/pull/40129) | Update dependencies                                                                                                                                                    |
| 0.5.3      | 2024-06-06 | [39225](https://github.com/airbytehq/airbyte/pull/39225) | [autopull] Upgrade base image to v1.2.2                                                                                                                                |
| 0.5.2      | 2024-06-02 | [38851](https://github.com/airbytehq/airbyte/pull/38851) | Emit state message at least once per stream                                                                                                                            |
| 0.5.1      | 2024-04-11 | [35404](https://github.com/airbytehq/airbyte/pull/35404) | Add `row_batch_size` parameter more granular control read records                                                                                                      |
| 0.5.0      | 2024-03-26 | [36515](https://github.com/airbytehq/airbyte/pull/36515) | Resolve poetry dependency conflict, add record counts to state messages                                                                                                |
| 0.4.0      | 2024-03-19 | [36267](https://github.com/airbytehq/airbyte/pull/36267) | Pin airbyte-cdk version to `^0`                                                                                                                                        |
| 0.3.17     | 2024-02-29 | [35722](https://github.com/airbytehq/airbyte/pull/35722) | Add logic to emit stream statuses                                                                                                                                      |
| 0.3.16     | 2024-02-12 | [35136](https://github.com/airbytehq/airbyte/pull/35136) | Fix license in `pyproject.toml`.                                                                                                                                       |
| 0.3.15     | 2024-02-07 | [34944](https://github.com/airbytehq/airbyte/pull/34944) | Manage dependencies with Poetry.                                                                                                                                       |
| 0.3.14     | 2024-01-23 | [34437](https://github.com/airbytehq/airbyte/pull/34437) | Fix header cells filtering                                                                                                                                             |
| 0.3.13     | 2024-01-19 | [34376](https://github.com/airbytehq/airbyte/pull/34376) | Fix names conversion                                                                                                                                                   |
| 0.3.12     | 2023-12-14 | [33414](https://github.com/airbytehq/airbyte/pull/33414) | Prepare for airbyte-lib                                                                                                                                                |
| 0.3.11     | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image                                                                                        |
| 0.3.10     | 2023-09-27 | [30487](https://github.com/airbytehq/airbyte/pull/30487) | Fix bug causing rows to be skipped when batch size increased due to rate limits.                                                                                       |
| 0.3.9      | 2023-09-25 | [30749](https://github.com/airbytehq/airbyte/pull/30749) | Performance testing - include socat binary in docker image                                                                                                             |
| 0.3.8      | 2023-09-25 | [30747](https://github.com/airbytehq/airbyte/pull/30747) | Performance testing - include socat binary in docker image                                                                                                             |
| 0.3.7      | 2023-08-25 | [29826](https://github.com/airbytehq/airbyte/pull/29826) | Remove row batch size from spec, add auto increase this value when rate limits                                                                                         |
| 0.3.6      | 2023-08-16 | [29491](https://github.com/airbytehq/airbyte/pull/29491) | Update to latest CDK                                                                                                                                                   |
| 0.3.5      | 2023-08-16 | [29427](https://github.com/airbytehq/airbyte/pull/29427) | Add stop reading in case of 429 error                                                                                                                                  |
| 0.3.4      | 2023-05-15 | [29453](https://github.com/airbytehq/airbyte/pull/29453) | Update spec descriptions                                                                                                                                               |
| 0.3.3      | 2023-08-10 | [29327](https://github.com/airbytehq/airbyte/pull/29327) | Add user-friendly error message for 404 and 403 error while discover                                                                                                   |
| 0.3.2      | 2023-08-09 | [29246](https://github.com/airbytehq/airbyte/pull/29246) | Add checking while reading to skip modified sheets                                                                                                                     |
| 0.3.1      | 2023-07-06 | [28033](https://github.com/airbytehq/airbyte/pull/28033) | Fixed several reported vulnerabilities (25 total), CVE-2022-37434, CVE-2022-42898                                                                                      |
| 0.3.0      | 2023-06-26 | [27738](https://github.com/airbytehq/airbyte/pull/27738) | License Update: Elv2                                                                                                                                                   |
| 0.2.39     | 2023-05-31 | [26833](https://github.com/airbytehq/airbyte/pull/26833) | Remove authSpecification in favour of advancedAuth in specification                                                                                                    |
| 0.2.38     | 2023-05-16 | [26097](https://github.com/airbytehq/airbyte/pull/26097) | Refactor config error                                                                                                                                                  |
| 0.2.37     | 2023-02-21 | [23292](https://github.com/airbytehq/airbyte/pull/23292) | Skip non grid sheets.                                                                                                                                                  |
| 0.2.36     | 2023-02-21 | [23272](https://github.com/airbytehq/airbyte/pull/23272) | Handle empty sheets gracefully.                                                                                                                                        |
| 0.2.35     | 2023-02-23 | [23057](https://github.com/airbytehq/airbyte/pull/23057) | Slugify column names                                                                                                                                                   |
| 0.2.34     | 2023-02-15 | [23071](https://github.com/airbytehq/airbyte/pull/23071) | Change min spreadsheet id size to 20 symbols                                                                                                                           |
| 0.2.33     | 2023-02-13 | [23278](https://github.com/airbytehq/airbyte/pull/23278) | Handle authentication errors                                                                                                                                           |
| 0.2.32     | 2023-02-13 | [22884](https://github.com/airbytehq/airbyte/pull/22884) | Do not consume http spreadsheets.                                                                                                                                      |
| 0.2.31     | 2022-10-09 | [19574](https://github.com/airbytehq/airbyte/pull/19574) | Revert 'Add row_id to rows and use as primary key'                                                                                                                     |
| 0.2.30     | 2022-10-09 | [19215](https://github.com/airbytehq/airbyte/pull/19215) | Add row_id to rows and use as primary key                                                                                                                              |
| 0.2.21     | 2022-10-04 | [15591](https://github.com/airbytehq/airbyte/pull/15591) | Clean instantiation of AirbyteStream                                                                                                                                   |
| 0.2.20     | 2022-10-10 | [17766](https://github.com/airbytehq/airbyte/pull/17766) | Fix null pointer exception when parsing the spreadsheet id.                                                                                                            |
| 0.2.19     | 2022-09-29 | [17410](https://github.com/airbytehq/airbyte/pull/17410) | Use latest CDK.                                                                                                                                                        |
| 0.2.18     | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states.                                                                                                                                          |
| 0.2.17     | 2022-08-03 | [15107](https://github.com/airbytehq/airbyte/pull/15107) | Expose Row Batch Size in Connector Specification                                                                                                                       |
| 0.2.16     | 2022-07-07 | [13729](https://github.com/airbytehq/airbyte/pull/13729) | Improve configuration field description                                                                                                                                |
| 0.2.15     | 2022-06-02 | [13446](https://github.com/airbytehq/airbyte/pull/13446) | Retry requests resulting in a server error                                                                                                                             |
| 0.2.13     | 2022-05-06 | [12685](https://github.com/airbytehq/airbyte/pull/12685) | Update CDK to v0.1.56 to emit an `AirbyeTraceMessage` on uncaught exceptions                                                                                           |
| 0.2.12     | 2022-04-20 | [12230](https://github.com/airbytehq/airbyte/pull/12230) | Update connector to use a `spec.yaml`                                                                                                                                  |
| 0.2.11     | 2022-04-13 | [11977](https://github.com/airbytehq/airbyte/pull/11977) | Replace leftover print statement with airbyte logger                                                                                                                   |
| 0.2.10     | 2022-03-25 | [11404](https://github.com/airbytehq/airbyte/pull/11404) | Allow using Spreadsheet Link/URL instead of Spreadsheet ID                                                                                                             |
| 0.2.9      | 2022-01-25 | [9208](https://github.com/airbytehq/airbyte/pull/9208)   | Update title and descriptions                                                                                                                                          |
| 0.2.7      | 2021-09-27 | [8470](https://github.com/airbytehq/airbyte/pull/8470)   | Migrate to the CDK                                                                                                                                                     |
| 0.2.6      | 2021-09-27 | [6354](https://github.com/airbytehq/airbyte/pull/6354)   | Support connecting via Oauth webflow                                                                                                                                   |
| 0.2.5      | 2021-09-12 | [5972](https://github.com/airbytehq/airbyte/pull/5972)   | Fix full_refresh test by adding supported_sync_modes to Stream initialization                                                                                          |
| 0.2.4      | 2021-08-05 | [5233](https://github.com/airbytehq/airbyte/pull/5233)   | Fix error during listing sheets with diagram only                                                                                                                      |
| 0.2.3      | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Add AIRBYTE_ENTRYPOINT for Kubernetes support                                                                                                                          |
| 0.2.2      | 2021-04-20 | [2994](https://github.com/airbytehq/airbyte/pull/2994)   | Formatting spec                                                                                                                                                        |
| 0.2.1      | 2021-04-03 | [2726](https://github.com/airbytehq/airbyte/pull/2726)   | Fix base connector versioning                                                                                                                                          |
| 0.2.0      | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238)   | Protocol allows future/unknown properties                                                                                                                              |
| 0.1.7      | 2021-01-21 | [1762](https://github.com/airbytehq/airbyte/pull/1762)   | Fix issue large spreadsheet                                                                                                                                            |
| 0.1.6      | 2021-01-27 | [1668](https://github.com/airbytehq/airbyte/pull/1668)   | Adopt connector best practices                                                                                                                                         |
| 0.1.5      | 2020-12-30 | [1438](https://github.com/airbytehq/airbyte/pull/1438)   | Implement backoff                                                                                                                                                      |
| 0.1.4      | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046)   | Add connectors using an index YAML file                                                                                                                                |

</details>
