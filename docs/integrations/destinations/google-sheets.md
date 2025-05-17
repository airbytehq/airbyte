# Google Sheets

The Google Sheets Destination is configured to push data to a single Google Sheets spreadsheet with multiple Worksheets as streams. To replicate data to multiple spreadsheets, you can create multiple instances of the Google Sheets Destination in your Airbyte instance.

:::warning

Google Sheets imposes rate limits and hard limits on the amount of data it can receive, which results in sync failure. Only use Google Sheets as a destination for small, non-production use cases, as it is not designed for handling large-scale data operations.

Read more about the [limitations](#limitations) of using Google Sheets below.

:::

## Prerequisites

- Google Account or GCP Service Account for authentication
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

Authentication to Google Sheets is available using OAuth or GCP Service Account token.

**Using OAuth**

1. Create a new [Google Cloud project](https://console.cloud.google.com/projectcreate).
2. Enable the [Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com).
3. Create a new [OAuth client ID](https://console.cloud.google.com/apis/credentials/oauthclient). Select `Web application` as the Application type, give it a `name` and add `https://developers.google.com/oauthplayground` as an Authorized redirect URI.
4. Add a `Client Secret` (Add secret), and take note of both the `Client Secret` and `Client ID`.
5. Go to [Google OAuth Playground](https://developers.google.com/oauthplayground/)
6. Click the cog in the top-right corner, select `Use your own OAuth credentials` and enter the `OAuth Client ID` and `OAuth Client secret` from the previous step.
7. In the left sidebar, find and select `Google Sheets API v4`, then choose the `https://www.googleapis.com/auth/spreadsheets` scope. Click `Authorize APIs`.
8. In **step 2**, click `Exchange authorization code for tokens`. Take note of the `Refresh token`.
9. Set up a new destination in Airbyte, select `Google Sheets` and enter the `Client ID`, `Client Secret`, `Refresh Token` and `Spreadsheet Link` from the previous steps.

**Using GCP Service Account:**

1. In the Google Cloud console, go to the Service accounts page.
2. Select a project.
3. Click the email address of the service account that you want to create a key for.
4. Click the Keys tab.
5. Click the Add key drop-down menu, then select Create new key.
6. Select JSON as the Key type and click Create.
Clicking Create downloads a service account key file. After you download the key file, you cannot download it again.

The key should look like:

```json
{
  "type": "service_account",
  "project_id": "PROJECT_ID",
  "private_key_id": "KEY_ID",
  "private_key": "-----BEGIN PRIVATE KEY-----\nPRIVATE_KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "SERVICE_ACCOUNT_EMAIL",
  "client_id": "CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/SERVICE_ACCOUNT_EMAIL"
}
```

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

Google Sheets imposes hard limits on the amount of data that can be synced. If you attempt to sync more data than is allowed, the sync may fail or, in some cases, data will be truncated to comply with limits.

**Maximum of 10 Million Cells**

A Google Sheets document can contain a maximum of 10 million cells. These can be in a single worksheet or in multiple sheets.
If you already have reached the 10 million limit, it will not allow you to add more columns (and vice versa, i.e., if the 10 million cells limit is reached with a certain number of rows, it will not allow more rows).

**Maximum of 50,000 characters per cell**

There can be at most 50,000 characters in a single cell. Airbyte will automatically truncate any value exceeding this limit, appending `...[TRUNCATED]` to the end of the value. Do not use Google Sheets if you have fields with long text in your source.

**Maximum of 18,278 Columns**

There can be at most 18,278 columns in Google Sheets in a worksheet.

**Maximum of 200 Worksheets in a Spreadsheet**

You cannot create more than 200 worksheets within single spreadsheet.

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

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                    |
|---------| ---------- | -------------------------------------------------------- | ---------------------------------------------------------- |
| 0.3.6 | 2025-05-17 | [59350](https://github.com/airbytehq/airbyte/pull/59350) | Update dependencies |
| 0.3.5 | 2025-04-30 | [59647](https://github.com/airbytehq/airbyte/pull/59647) | Truncate cell values exceeding 50,000 characters with warning |
| 0.3.4 | 2025-04-26 | [58280](https://github.com/airbytehq/airbyte/pull/58280) | Update dependencies |
| 0.3.3 | 2025-04-12 | [57636](https://github.com/airbytehq/airbyte/pull/57636) | Update dependencies |
| 0.3.2 | 2025-04-05 | [57166](https://github.com/airbytehq/airbyte/pull/57166) | Update dependencies |
| 0.3.1 | 2025-03-29 | [56600](https://github.com/airbytehq/airbyte/pull/56600) | Update dependencies |
| 0.3.0 | 2025-02-27 | [54689](https://github.com/airbytehq/airbyte/pull/54689) | Support service account authentication |
| 0.2.42 | 2025-03-22 | [56149](https://github.com/airbytehq/airbyte/pull/56149) | Update dependencies |
| 0.2.41 | 2025-03-08 | [55374](https://github.com/airbytehq/airbyte/pull/55374) | Update dependencies |
| 0.2.40 | 2025-03-01 | [54847](https://github.com/airbytehq/airbyte/pull/54847) | Update dependencies |
| 0.2.39 | 2025-02-22 | [54248](https://github.com/airbytehq/airbyte/pull/54248) | Update dependencies |
| 0.2.38 | 2025-02-15 | [53892](https://github.com/airbytehq/airbyte/pull/53892) | Update dependencies |
| 0.2.37 | 2025-02-01 | [52194](https://github.com/airbytehq/airbyte/pull/52194) | Update dependencies |
| 0.2.36 | 2025-01-18 | [51748](https://github.com/airbytehq/airbyte/pull/51748) | Update dependencies |
| 0.2.35 | 2025-01-11 | [51262](https://github.com/airbytehq/airbyte/pull/51262) | Update dependencies |
| 0.2.34 | 2025-01-04 | [50912](https://github.com/airbytehq/airbyte/pull/50912) | Update dependencies |
| 0.2.33 | 2024-12-28 | [50492](https://github.com/airbytehq/airbyte/pull/50492) | Update dependencies |
| 0.2.32 | 2024-12-21 | [50168](https://github.com/airbytehq/airbyte/pull/50168) | Update dependencies |
| 0.2.31 | 2024-12-14 | [48915](https://github.com/airbytehq/airbyte/pull/48915) | Update dependencies |
| 0.2.30 | 2024-11-25 | [48678](https://github.com/airbytehq/airbyte/pull/48678) | Update dependencies |
| 0.2.29 | 2024-11-04 | [48281](https://github.com/airbytehq/airbyte/pull/48281) | Update dependencies |
| 0.2.28 | 2024-10-28 | [47042](https://github.com/airbytehq/airbyte/pull/47042) | Update dependencies |
| 0.2.27 | 2024-10-12 | [46772](https://github.com/airbytehq/airbyte/pull/46772) | Update dependencies |
| 0.2.26 | 2024-10-05 | [46464](https://github.com/airbytehq/airbyte/pull/46464) | Update dependencies |
| 0.2.25 | 2024-09-28 | [46204](https://github.com/airbytehq/airbyte/pull/46204) | Update dependencies |
| 0.2.24 | 2024-09-21 | [45772](https://github.com/airbytehq/airbyte/pull/45772) | Update dependencies |
| 0.2.23 | 2024-09-14 | [45577](https://github.com/airbytehq/airbyte/pull/45577) | Update dependencies |
| 0.2.22 | 2024-09-07 | [45325](https://github.com/airbytehq/airbyte/pull/45325) | Update dependencies |
| 0.2.21 | 2024-08-31 | [44989](https://github.com/airbytehq/airbyte/pull/44989) | Update dependencies |
| 0.2.20 | 2024-08-24 | [44736](https://github.com/airbytehq/airbyte/pull/44736) | Update dependencies |
| 0.2.19 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.2.18 | 2024-08-17 | [44259](https://github.com/airbytehq/airbyte/pull/44259) | Update dependencies |
| 0.2.17 | 2024-08-10 | [43603](https://github.com/airbytehq/airbyte/pull/43603) | Update dependencies |
| 0.2.16 | 2024-08-03 | [43066](https://github.com/airbytehq/airbyte/pull/43066) | Update dependencies |
| 0.2.15 | 2024-07-27 | [42819](https://github.com/airbytehq/airbyte/pull/42819) | Update dependencies |
| 0.2.14 | 2024-07-20 | [42368](https://github.com/airbytehq/airbyte/pull/42368) | Update dependencies |
| 0.2.13 | 2024-07-13 | [41721](https://github.com/airbytehq/airbyte/pull/41721) | Update dependencies |
| 0.2.12 | 2024-07-10 | [41520](https://github.com/airbytehq/airbyte/pull/41520) | Update dependencies |
| 0.2.11 | 2024-07-09 | [41076](https://github.com/airbytehq/airbyte/pull/41076) | Update dependencies |
| 0.2.10 | 2024-07-06 | [40999](https://github.com/airbytehq/airbyte/pull/40999) | Update dependencies |
| 0.2.9 | 2024-06-26 | [40529](https://github.com/airbytehq/airbyte/pull/40529) | Update dependencies |
| 0.2.8 | 2024-06-25 | [40353](https://github.com/airbytehq/airbyte/pull/40353) | Update dependencies |
| 0.2.7 | 2024-06-22 | [40172](https://github.com/airbytehq/airbyte/pull/40172) | Update dependencies |
| 0.2.6 | 2024-06-04 | [39011](https://github.com/airbytehq/airbyte/pull/39011) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.5 | 2024-05-22 | [38516](https://github.com/airbytehq/airbyte/pull/38516) | [autopull] base image + poetry + up_to_date |
| 0.2.4 | 2024-05-21 | [38516](https://github.com/airbytehq/airbyte/pull/38516) | [autopull] base image + poetry + up_to_date |
| 0.2.3 | 2023-09-25 | [30748](https://github.com/airbytehq/airbyte/pull/30748) | Performance testing - include socat binary in docker image |
| 0.2.2 | 2023-07-06 | [28035](https://github.com/airbytehq/airbyte/pull/28035) | Migrate from authSpecification to advancedAuth |
| 0.2.1 | 2023-06-26 | [27782](https://github.com/airbytehq/airbyte/pull/27782) | Only allow HTTPS urls |
| 0.2.0 | 2023-06-26 | [27780](https://github.com/airbytehq/airbyte/pull/27780) | License Update: Elv2 |
| 0.1.2 | 2022-10-31 | [18729](https://github.com/airbytehq/airbyte/pull/18729) | Fix empty headers list |
| 0.1.1 | 2022-06-15 | [14751](https://github.com/airbytehq/airbyte/pull/14751) | Yield state only when records saved |
| 0.1.0 | 2022-04-26 | [12135](https://github.com/airbytehq/airbyte/pull/12135) | Initial Release |

</details>

