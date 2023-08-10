# Google Search Console

This page contains the setup guide and reference information for the Google Search Console source connector.

## Prerequisites

- Access to your Google Search Console sites with your role as either Full User or Owner.

## Setup guide

The Google Search Console connector supports two authentication methods:

- You can use OAuth
- Service Account JSON Key

For **Airbyte Cloud** users, we recommend using OAuth authentication, as it simplifies the setup process and allows you to authenticate directly from the Airbyte UI.

For **Airbyte Open Source** users, we recommend setting up a Service Account and creating an associated JSON Key file.

### Step 1: Set up google search console

#### How to create the client credentials for Google Search Console, to use with Airbyte?

You can either:

- Use an existing Service Account for your Google Project with granted Admin Permissions, or create a new one and grant Admin permissions to it.
- Use your personal Google User Account with oauth. If you choose this option, your account must have permissions to view the Google Search Console project you choose.
- Follow the `Delegating domain-wide authority` process to obtain the necessary permissions to your google account from the administrator of Workspace

### Create a Google service account and JSON credentials

A service account's credentials include a generated email address that is unique and at least one public/private key pair. If domain-wide delegation is enabled, then a client ID is also part of the service account's credentials.

1. Open the [Service Accounts page](https://console.developers.google.com/iam-admin/serviceaccounts).
2. Select an existing project, or create a new project.
3. At the top of the page, click **+ Create service account**.
4. Enter a name and description for the service account, then click **Create and Continue** .
5. Under **Service account permissions**, select the roles to grant to the service account, then click **Continue**. We recommend the **Viewer** role.
   - Optional: Under `Grant users access to this service account`, add the `users` or `groups` that are allowed to use and manage the service account.
6. Go to the [API Console/Credentials](https://console.cloud.google.com/apis/credentials) and click on the email address of the service account you just created.
7. In the **Details** tab, select **Advanced settings** and find `Show domain-wide delegation`, checkmark the `Enable Google Workspace Domain-wide Delegation`.
8. In the **Keys** tab, click **+ Add key**, then click **Create new key**.
9. Select **JSON** as the Key type. This will generate and download the JSON key file that you'll use for authentication. Click **Continue**.

:::caution
This file serves as the only copy of your JSON service key, and you will not be able to re-download it. Be sure to store it in a secure location.
:::

### Using the existing Service Account

1. Go to [API Console/Credentials](https://console.cloud.google.com/apis/credentials), check the `Service Accounts` section, click on the Email address of service account you just created.
2. Click on `Details` tab and find `Show domain-wide delegation`, checkmark the `Enable Google Workspace Domain-wide Delegation`.
3. On `Keys` tab click `+ Add key`, then click `Create new key`.

Your new public/private key pair should be now generated and downloaded to your machine as `<project_id>.json` you can find it in the `Downloads` folder or somewhere else if you use another default destination for downloaded files. This file serves as the only copy of the private key. You are responsible for storing it securely. If you lose this key pair, you will need to generate a new one!

### Note

You can return to the [API Console/Credentials](https://console.cloud.google.com/apis/credentials) at any time to view the email address, public key fingerprints, and other information, or to generate additional public/private key pairs. For more details about service account credentials in the API Console, see [Service accounts](https://cloud.google.com/iam/docs/understanding-service-accounts) in the API Console help file.

### Create a Service Account with delegated domain-wide authority

Follow the Google Documentation for performing [Delegating domain-wide authority](https://developers.google.com/identity/protocols/oauth2/service-account#delegatingauthority) to create a Service account with delegated domain-wide authority. This account must be created by an administrator of your Google Workspace. Please make sure to grant the following `OAuth scopes` to the service user:

- `https://www.googleapis.com/auth/webmasters.readonly`

At the end of this process, you should have JSON credentials to this Google Service Account.

### Step 2: Set up the google search console connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Google Search Console** from the list of available sources.
4. For **Website URL Property**, enter the URL(s) of any properties with data you want to replicate.
5. For **Start Date**, use the provided datepicker or enter a date in the format `YYYY-MM-DD`. Any data created on or after this date will be replicated.
6. Click Authenticate your account to sign in with Google and authorize your account.
7. (Optional) For **End Date**, you may optionally provide a date in the format `YYYY-MM-DD`. Any data created between the defined Start Date and End Date will be replicated. Leaving this field blank will replicate all data created on or after the Start Date to the present.
8. (Optional) For **Custom Reports**, you may optionally provide an array of JSON objects representing any custom reports you wish to query the API with. Refer to the [Custom reports](#custom-reports) section below for more information on formulating these reports.
9. (Optional) For **Data State**, you may choose whether to only include "fresh" data that has not been finalized. Refer to the [Data State](#data-state) section below for more information on. Please note that if you are using Incremental sync mode, we highly recommend leaving this option to its default value of `final`, as selecting `all` could result in data loss.
10. Click **Set up source** and wait for the tests to complete.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Fill in the `service_account_info` and `email` fields for authentication.
2. Fill in the `site_urls` field.
3. Fill in the `start date` field.
4. Fill in the `custom reports` (optionally) in format `{"name": "<report-name>", "dimensions": ["<dimension-name>", ...]}`
5. Fill in the `data_state` (optionally) in case you want to sync fresher data use `all' value, otherwise use 'final'.
6. You should be ready to sync data.
<!-- /env:oss -->

## Supported sync modes

The Google Search Console Source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

:::note
The granularity for the cursor is 1 day, so Incremental Sync in Append mode may result in duplicating the data.
:::

:::note
When using Incremental Sync mode, we recommend setting the **Data State** option to `final`, as the `all` option may cause data loss.
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

### Data State

The **Data State** parameter deals with the "freshness", or finality of the data that is being queried.

- `final`: The query will include only finalized, stable data. This is data that has been processed, verified, and is unlikely to change. When you select this option, you're asking for the definitive statistics and information that Google has analyzed and confirmed.
- `all`: The query will return both finalized data and what Google terms "fresh" data. Fresh data includes more recent data that hasn't gone through the full processing and verification that finalized data has. This option can give you more up-to-the-minute insights, but it may be subject to change as Google continues to process and analyze it.

:::caution
When using Incremental Sync mode, we highly recommend leaving this parameter to `final`, as the `all` option may result in data loss.
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
