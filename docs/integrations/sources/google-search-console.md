# Google Search Console

This page contains the setup guide and reference information for the Google Search Console source connector.

## Prerequisites

- A verified property in Google Search Console
<!-- env:oss -->
- Google Search Console API enabled for your project (**Airbyte Open Source** only)
<!-- /env:oss -->

## Setup guide

### Step 1: Set up Google Search Console authentication

To authenticate the Google Search Console connector, you will need to use one of the following methods:

#### I: OAuth (Recommended for Airbyte Cloud)

<!-- env:cloud -->
You can authenticate using your Google Account with OAuth if you are the owner of the Google Search Console property or have view permissions. Follow [Google's instructions](https://support.google.com/webmasters/answer/7687615?sjid=11103698321670173176-NA) to ensure that your account has the necessary permissions (**Owner** or **Full User**) to view the Google Search Console property. This option is recommended for **Airbyte Cloud** users, as it significantly simplifies the setup process and allows you to authenticate the connection [directly from the Airbyte UI](#step-2-set-up-the-google-search-console-connector-in-airbyte).
<!-- /env:cloud -->

<!-- env:oss -->
To authenticate with OAuth in **Airbyte Open Source**, you will need to create an authentication app and obtain the following credentials and tokens:

- Client ID
- Client Secret
- Refresh Token
- Access Token

More information on the steps to create an OAuth app to access Google APIs and obtain these credentials can be found [in Google's documentation](https://developers.google.com/identity/protocols/oauth2).

#### II: Google service account with JSON key file (Recommended for Airbyte Open Source)

You can authenticate the connection using a JSON key file associated with a Google service account. This option is recommended for **Airbyte Open Source** users. Follow the steps below to create a service account and generate the JSON key file:

1. Open the [Service Accounts page](https://console.developers.google.com/iam-admin/serviceaccounts).
2. Select an existing project, or create a new project.
3. At the top of the page, click **+ Create service account**.
4. Enter a name and description for the service account, then click **Create and Continue**.
5. Under **Service account permissions**, select the roles to grant to the service account, then click **Continue**. We recommend the **Viewer** role.
   - Optional: Under **Grant users access to this service account**, you may specify the users or groups that are allowed to use and manage the service account.
6. Go to the [API Console/Credentials](https://console.cloud.google.com/apis/credentials) and click on the email address of the service account you just created.
7. In the **Keys** tab, click **+ Add key**, then click **Create new key**.
8. Select **JSON** as the Key type. This will generate and download the JSON key file that you'll use for authentication. Click **Continue**.

:::caution
This file serves as the only copy of your JSON service key, and you will not be able to re-download it. Be sure to store it in a secure location.
:::

:::note
You can return to the [API Console/Credentials](https://console.cloud.google.com/apis/credentials) at any time to manage your service account or generate additional JSON keys. For more details about service account credentials, see [Google's IAM documentation](https://cloud.google.com/iam/docs/understanding-service-accounts).
:::

#### Note on delegating domain-wide authority to the service account

Domain-wide delegation is a powerful feature that allows service accounts to access users' data across an organization's Google Workspace environment through 'impersonation'. This authority is necessary in certain use cases, such as when a service account needs broad access across multiple users and services within a domain.

:::note
Only the super admin of your Google Workspace domain can enable domain-wide delegation of authority to a service account.
:::

To enable delegated domain-wide authority, follow the steps listed in the [Google documentation](https://developers.google.com/identity/protocols/oauth2/service-account#delegatingauthority). Please make sure to grant the following OAuth scopes to the service account:

- `https://www.googleapis.com/auth/webmasters.readonly`

For more information on this topic, please refer to [this Google article](https://support.google.com/a/answer/162106?hl=en).
<!-- /env:oss -->

### Step 2: Set up the Google Search Console connector in Airbyte

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Google Search Console** from the list of available sources.
4. For **Source name**, enter a name to help you identify this source.
5. For **Website URL Property**, enter the specific website property in Google Seach Console with data you want to replicate.
6. For **Start Date**, use the provided datepicker or enter a date in the format `YYYY-MM-DD`. Any data created on or after this date will be replicated.
7. To authenticate the connection:

   <!-- env:cloud -->
   - **For Airbyte Cloud**: Select **Oauth** from the Authentication dropdown, then click **Sign in with Google** to authorize your account.
   <!-- /env:cloud -->
   <!-- env:oss -->
   - **For Airbyte Open Source**:
      - (Recommended) Select **Service Account Key Authorization** from the Authentication dropdown, then enter the **Admin Email** and **Service Account JSON Key**. For the key, copy and paste the JSON key you obtained during the service account setup. It should begin with `{"type": "service account", "project_id": YOUR_PROJECT_ID, "private_key_id": YOUR_PRIVATE_KEY, ...}`
      - Select **Oauth** from the Authentication dropdown, then enter your **Client ID**, **Client Secret**, **Access Token** and **Refresh Token**.
   <!-- /env:oss -->

8. (Optional) For **End Date**, you may optionally provide a date in the format `YYYY-MM-DD`. Any data created between the defined Start Date and End Date will be replicated. Leaving this field blank will replicate all data created on or after the Start Date to the present.
9. (Optional) For **Custom Reports**, you may optionally provide an array of JSON objects representing any custom reports you wish to query the API with. Refer to the [Custom reports](#custom-reports) section below for more information on formulating these reports.
10. (Optional) For **Data Freshness**, you may choose whether to include "fresh" data that has not been finalized by Google, and may be subject to change. Please note that if you are using Incremental sync mode, we highly recommend leaving this option to its default value of `final`. Refer to the [Data Freshness](#data-freshness) section below for more information on this parameter.
11. Click **Set up source** and wait for the tests to complete.

## Supported sync modes

The Google Search Console Source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

:::note
The granularity for the cursor is 1 day, so Incremental Sync in Append mode may result in duplicating the data.
:::

## Supported streams

- [Sites](https://developers.google.com/webmaster-tools/search-console-api-original/v3/sites/get)
- [Sitemaps](https://developers.google.com/webmaster-tools/search-console-api-original/v3/sitemaps/list)
- [Full Analytics report](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query) \(this stream has a long sync time because it is very detailed, use with care\)
- [Analytics report by country](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
- [Analytics report by date](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
- [Analytics report by device](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
- [Analytics report by page](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
- [Analytics report by query](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
- [Analytics keyword report](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
- [Analytics keyword report by page](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
- [Analytics page report](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
- [Analytics site report by page](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
- [Analytics site report by site](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
- Analytics report by custom dimensions

## Connector-specific configurations

### Custom reports

Custom reports allow you to query the API with a custom set of dimensions to group results by. Results are grouped in the order that you supply these dimensions. Each custom report should be constructed as a JSON object in the following format:

```json
{
   "name": "<report-name>",
   "dimensions": ["<dimension-name>", "<dimension-name>", ...]
   }
```

The available dimensions are:

- `country`
- `date`
- `device`
- `page`
- `query`
- `searchAppearance`

For example, to query the API for a report that groups results by country, then by date, you could enter the following custom report:

```json
[
   {
      "name": "country_date",
      "dimensions": ["country", "date"]
   }
]
```

You can use the [Google APIS Explorer](https://developers.google.com/webmaster-tools/v1/searchanalytics/query) to build and test the reports you want to use.

### Data Freshness

The **Data Freshness** parameter deals with the "freshness", or finality of the data that is being queried.

- `final`: The query will include only finalized, stable data. This is data that has been processed, verified, and is unlikely to change. When you select this option, you are querying for the definitive statistics and information that Google has analyzed and confirmed.
- `all`: The query will return both finalized data and what Google terms "fresh" data. Fresh data includes more recent data that hasn't gone through the full processing and verification that finalized data has. This option can give you more up-to-the-minute insights, but it may be subject to change as Google continues to process and analyze it.

:::caution
When using Incremental Sync mode, we recommend leaving this parameter to its default state of `final`, as the `all` option may cause discrepancies between the data in your destination table and the finalized data in Google Search Console.
:::

## Performance considerations

This connector attempts to back off gracefully when it hits Reports API's rate limits. To find more information about limits, see [Usage Limits](https://developers.google.com/webmaster-tools/limits) documentation.

## Data type map

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

## Changelog

| Version  | Date       | Pull Request                                                                                                  | Subject                                                                                                                        |
| :------- | :--------- | :------------------------------------------------------------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------- |
| `1.2.1`  | 2023-07-04 | [27952](https://github.com/airbytehq/airbyte/pull/27952)                                                      | Removed deprecated `searchType`, added `discover`(Discover results) and `googleNews`(Results from news.google.com, etc.) types |
| `1.2.0`  | 2023-06-29 | [27831](https://github.com/airbytehq/airbyte/pull/27831)                                                      | Add new streams                                                                                                                |
| `1.1.0`  | 2023-06-26 | [27738](https://github.com/airbytehq/airbyte/pull/27738)                                                      | License Update: Elv2                                                                                                           |
| `1.0.2`  | 2023-06-13 | [27307](https://github.com/airbytehq/airbyte/pull/27307)                                                      | Fix `data_state` config typo                                                                                                   |
| `1.0.1`  | 2023-05-30 | [26746](https://github.com/airbytehq/airbyte/pull/26746)                                                      | Remove `authSpecification` from connector spec in favour of advancedAuth                                                       |
| `1.0.0`  | 2023-05-24 | [26452](https://github.com/airbytehq/airbyte/pull/26452)                                                      | Add data_state parameter to specification                                                                                      |
| `0.1.22` | 2023-03-20 | [22295](https://github.com/airbytehq/airbyte/pull/22295)                                                      | Update specification examples                                                                                                  |
| `0.1.21` | 2023-02-14 | [22984](https://github.com/airbytehq/airbyte/pull/22984)                                                      | Specified date formatting in specification                                                                                     |
| `0.1.20` | 2023-02-02 | [22334](https://github.com/airbytehq/airbyte/pull/22334)                                                      | Turn on default HttpAvailabilityStrategy                                                                                       |
| `0.1.19` | 2023-01-27 | [22007](https://github.com/airbytehq/airbyte/pull/22007)                                                      | Set `AvailabilityStrategy` for streams explicitly to `None`                                                                    |
| `0.1.18` | 2022-10-27 | [18568](https://github.com/airbytehq/airbyte/pull/18568)                                                      | Improved config validation: custom_reports.dimension                                                                           |
| `0.1.17` | 2022-10-08 | [17751](https://github.com/airbytehq/airbyte/pull/17751)                                                      | Improved config validation: start_date, end_date, site_urls                                                                    |
| `0.1.16` | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304)                                                      | Migrate to per-stream state.                                                                                                   |
| `0.1.15` | 2022-09-16 | [16819](https://github.com/airbytehq/airbyte/pull/16819)                                                      | Check available site urls to avoid 403 error on sync                                                                           |
| `0.1.14` | 2022-09-08 | [16433](https://github.com/airbytehq/airbyte/pull/16433)                                                      | Add custom analytics stream.                                                                                                   |
| `0.1.13` | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924)                                                      | Remove `additionalProperties` field from specs                                                                                 |
| `0.1.12` | 2022-05-04 | [12482](https://github.com/airbytehq/airbyte/pull/12482)                                                      | Update input configuration copy                                                                                                |
| `0.1.11` | 2022-01-05 | [9186](https://github.com/airbytehq/airbyte/pull/9186) [9194](https://github.com/airbytehq/airbyte/pull/9194) | Fix incremental sync: keep all urls in state object                                                                            |
| `0.1.10` | 2021-12-23 | [9073](https://github.com/airbytehq/airbyte/pull/9073)                                                        | Add slicing by date range                                                                                                      |
| `0.1.9`  | 2021-12-22 | [9047](https://github.com/airbytehq/airbyte/pull/9047)                                                        | Add 'order' to spec.json props                                                                                                 |
| `0.1.8`  | 2021-12-21 | [8248](https://github.com/airbytehq/airbyte/pull/8248)                                                        | Enable Sentry for performance and errors tracking                                                                              |
| `0.1.7`  | 2021-11-26 | [7431](https://github.com/airbytehq/airbyte/pull/7431)                                                        | Add default `end_date` param value                                                                                             |
| `0.1.6`  | 2021-09-27 | [6460](https://github.com/airbytehq/airbyte/pull/6460)                                                        | Update OAuth Spec File                                                                                                         |
| `0.1.4`  | 2021-09-23 | [6394](https://github.com/airbytehq/airbyte/pull/6394)                                                        | Update Doc link Spec File                                                                                                      |
| `0.1.3`  | 2021-09-23 | [6405](https://github.com/airbytehq/airbyte/pull/6405)                                                        | Correct Spec File                                                                                                              |
| `0.1.2`  | 2021-09-17 | [6222](https://github.com/airbytehq/airbyte/pull/6222)                                                        | Correct Spec File                                                                                                              |
| `0.1.1`  | 2021-09-22 | [6315](https://github.com/airbytehq/airbyte/pull/6315)                                                        | Verify access to all sites when performing connection check                                                                    |
| `0.1.0`  | 2021-09-03 | [5350](https://github.com/airbytehq/airbyte/pull/5350)                                                        | Initial Release                                                                                                                |
