# Google Search Console

This page contains the setup guide and reference information for the google search console source connector.


## Prerequisites

* A verified property in Google Search Console
* Enable Google Search Console API for GCP project at [GCP console](https://console.cloud.google.com/apis/library/searchconsole.googleapis.com)
* Credentials to a Google Service Account \(or Google Service Account with delegated Domain Wide Authority\) or Google User Account
* Enable Google Search Console API


## Setup guide
### Step 1: Set up google search console

#### How to create the client credentials for Google Search Console, to use with Airbyte?

You can either:

* Use the existing `Service Account` for your Google Project with granted Admin Permissions
* Use your personal Google User Account with oauth. If you choose this option, your account must have permissions to view the Google Search Console project you choose.
* Create the new `Service Account` credentials for your Google Project, and grant Admin Permissions to it
* Follow the `Delegating domain-wide authority` process to obtain the necessary permissions to your google account from the administrator of Workspace

### Creating a Google service account

A service account's credentials include a generated email address that is unique and at least one public/private key pair. If domain-wide delegation is enabled, then a client ID is also part of the service account's credentials.

1. Open the [Service accounts page](https://console.developers.google.com/iam-admin/serviceaccounts)
2. If prompted, select an existing project, or create a new project.
3. Click `+ Create service account`.
4. Under Service account details, type a `name`, `ID`, and `description` for the service account, then click `Create`.
   * Optional: Under `Service account permissions`, select the `IAM roles` to grant to the service account, then click `Continue`.
   * Optional: Under `Grant users access to this service account`, add the `users` or `groups` that are allowed to use and manage the service account.
5. Go to [API Console/Credentials](https://console.cloud.google.com/apis/credentials), check the `Service Accounts` section, click on the Email address of service account you just created.
6. Open `Details` tab and find `Show domain-wide delegation`, checkmark the `Enable Google Workspace Domain-wide Delegation`.
7. On `Keys` tab click `+ Add key`, then click `Create new key`.

Your new public/private key pair should be now generated and downloaded to your machine as `<project_id>.json` you can find it in the `Downloads` folder or somewhere else if you use another default destination for downloaded files. This file serves as the only copy of the private key. You are responsible for storing it securely. If you lose this key pair, you will need to generate a new one!

### Using the existing Service Account

1. Go to [API Console/Credentials](https://console.cloud.google.com/apis/credentials), check the `Service Accounts` section, click on the Email address of service account you just created.
2. Click on `Details` tab and find `Show domain-wide delegation`, checkmark the `Enable Google Workspace Domain-wide Delegation`.
3. On `Keys` tab click `+ Add key`, then click `Create new key`.

Your new public/private key pair should be now generated and downloaded to your machine as `<project_id>.json` you can find it in the `Downloads` folder or somewhere else if you use another default destination for downloaded files. This file serves as the only copy of the private key. You are responsible for storing it securely. If you lose this key pair, you will need to generate a new one!

### Note

You can return to the [API Console/Credentials](https://console.cloud.google.com/apis/credentials) at any time to view the email address, public key fingerprints, and other information, or to generate additional public/private key pairs. For more details about service account credentials in the API Console, see [Service accounts](https://cloud.google.com/iam/docs/understanding-service-accounts) in the API Console help file.

### Create a Service Account with delegated domain-wide authority

Follow the Google Documentation for performing [Delegating domain-wide authority](https://developers.google.com/identity/protocols/oauth2/service-account#delegatingauthority) to create a Service account with delegated domain-wide authority. This account must be created by an administrator of your Google Workspace. Please make sure to grant the following `OAuth scopes` to the service user:

* `https://www.googleapis.com/auth/webmasters.readonly`

At the end of this process, you should have JSON credentials to this Google Service Account.

## Step 2: Set up the google search console connector in Airbyte

<!-- env:cloud -->
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the google search console connector and select **google search console** from the Source type dropdown.
4. Click Authenticate your account to sign in with Google and authorize your account.
5. Fill in the `site_urls` field.
6. Fill in the `start date` field.
7. Fill in the `custom reports` (optionally) in format `{"name": "<report-name>", "dimensions": ["<dimension-name>", ...]}`
8. Fill in the `data_state` (optionally) in case you want to sync fresher data use `all' value, otherwise use 'final'.
8. You should be ready to sync data.
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

The Google Search Console Source connector supports the following [ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):


* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

:::note
   The granularity for the cursor is 1 day, so Incremental Sync in Append mode may result in duplicating the data.
:::

:::note
    Parameter `data_state='all'` should not be used with Incremental Sync mode as it may cause data loss.
:::

## Supported Streams

* [Sites](https://developers.google.com/webmaster-tools/search-console-api-original/v3/sites/get)
* [Sitemaps](https://developers.google.com/webmaster-tools/search-console-api-original/v3/sitemaps/list)
* [Full Analytics report](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query) \(this stream has a long sync time because it is very detailed, use with care\)
* [Analytics report by country](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
* [Analytics report by date](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
* [Analytics report by device](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
* [Analytics report by page](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
* [Analytics report by query](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)
* Analytics report by custom dimensions


## Performance considerations

This connector attempts to back off gracefully when it hits Reports API's rate limits. To find more information about limits, see [Usage Limits](https://developers.google.com/webmaster-tools/limits) documentation.


## Data type map

| Integration Type | Airbyte Type | Notes |
|:-----------------|:-------------|:------|
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |


## Changelog

| Version  | Date       | Pull Request                                                                                                  | Subject                                                                  |
|:---------|:-----------|:--------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------|
| `1.0.2`  | 2023-06-13 | [27307](https://github.com/airbytehq/airbyte/pull/27307)                                                     | Fix `data_state` config typo |
| `1.0.1`  | 2023-05-30 | [26746](https://github.com/airbytehq/airbyte/pull/26746)                                                      | Remove `authSpecification` from connector spec in favour of advancedAuth |
| `1.0.0`  | 2023-05-24 | [26452](https://github.com/airbytehq/airbyte/pull/26452)                                                      | Add data_state parameter to specification                                |
| `0.1.22` | 2023-03-20 | [22295](https://github.com/airbytehq/airbyte/pull/22295)                                                      | Update specification examples                                            |
| `0.1.21` | 2023-02-14 | [22984](https://github.com/airbytehq/airbyte/pull/22984)                                                      | Specified date formatting in specification                               |
| `0.1.20` | 2023-02-02 | [22334](https://github.com/airbytehq/airbyte/pull/22334)                                                      | Turn on default HttpAvailabilityStrategy                                 |
| `0.1.19` | 2023-01-27 | [22007](https://github.com/airbytehq/airbyte/pull/22007)                                                      | Set `AvailabilityStrategy` for streams explicitly to `None`              |
| `0.1.18` | 2022-10-27 | [18568](https://github.com/airbytehq/airbyte/pull/18568)                                                      | Improved config validation: custom_reports.dimension                     |
| `0.1.17` | 2022-10-08 | [17751](https://github.com/airbytehq/airbyte/pull/17751)                                                      | Improved config validation: start_date, end_date, site_urls              |
| `0.1.16` | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304)                                                      | Migrate to per-stream state.                                             |
| `0.1.15` | 2022-09-16 | [16819](https://github.com/airbytehq/airbyte/pull/16819)                                                      | Check available site urls to avoid 403 error on sync                     |
| `0.1.14` | 2022-09-08 | [16433](https://github.com/airbytehq/airbyte/pull/16433)                                                      | Add custom analytics stream.                                             |
| `0.1.13` | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924)                                                      | Remove `additionalProperties` field from specs                           |
| `0.1.12` | 2022-05-04 | [12482](https://github.com/airbytehq/airbyte/pull/12482)                                                      | Update input configuration copy                                          |
| `0.1.11` | 2022-01-05 | [9186](https://github.com/airbytehq/airbyte/pull/9186) [9194](https://github.com/airbytehq/airbyte/pull/9194) | Fix incremental sync: keep all urls in state object                      |
| `0.1.10` | 2021-12-23 | [9073](https://github.com/airbytehq/airbyte/pull/9073)                                                        | Add slicing by date range                                                |
| `0.1.9`  | 2021-12-22 | [9047](https://github.com/airbytehq/airbyte/pull/9047)                                                        | Add 'order' to spec.json props                                           |
| `0.1.8`  | 2021-12-21 | [8248](https://github.com/airbytehq/airbyte/pull/8248)                                                        | Enable Sentry for performance and errors tracking                        |
| `0.1.7`  | 2021-11-26 | [7431](https://github.com/airbytehq/airbyte/pull/7431)                                                        | Add default `end_date` param value                                       |
| `0.1.6`  | 2021-09-27 | [6460](https://github.com/airbytehq/airbyte/pull/6460)                                                        | Update OAuth Spec File                                                   |
| `0.1.4`  | 2021-09-23 | [6394](https://github.com/airbytehq/airbyte/pull/6394)                                                        | Update Doc link Spec File                                                |
| `0.1.3`  | 2021-09-23 | [6405](https://github.com/airbytehq/airbyte/pull/6405)                                                        | Correct Spec File                                                        |
| `0.1.2`  | 2021-09-17 | [6222](https://github.com/airbytehq/airbyte/pull/6222)                                                        | Correct Spec File                                                        |
| `0.1.1`  | 2021-09-22 | [6315](https://github.com/airbytehq/airbyte/pull/6315)                                                        | Verify access to all sites when performing connection check              |
| `0.1.0`  | 2021-09-03 | [5350](https://github.com/airbytehq/airbyte/pull/5350)                                                        | Initial Release                                                          |
