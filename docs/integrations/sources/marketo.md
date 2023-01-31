# Marketo

This page contains the setup guide and reference information for the Marketo source connector.

## Prerequisites

* \(Optional\) Whitelist Airbyte's IP address if needed
* An API-only Marketo User Role
* An Airbyte Marketo API-only user
* A Marketo API Custom Service
* Marketo Client ID & Client Secret
* Marketo Base URL

## Setup guide
### Step 1: Set up Marketo

#### Step 1.1: \(Optional\) whitelist Airbyte's IP address

If you don't have IP Restriction enabled in Marketo, skip this step.

If you have IP Restriction enabled in Marketo, you'll need to whitelist the IP address of the machine running your Airbyte instance. To obtain your IP address, run `curl ifconfig.io` from the node running Airbyte. You might need to enlist an engineer to help with this. Copy the IP address returned and keep it on hand.

Once you have the IP address, whitelist it by following the Marketo documentation for [allowlisting IP addresses](https://docs.marketo.com/display/public/DOCS/Create+an+Allowlist+for+IP-Based+API+Access) for API based access.

#### Step 1.2: Create an API-only Marketo User Role

Follow the [Marketo documentation for creating an API-only Marketo User Role](https://docs.marketo.com/display/public/DOCS/Create+an+API+Only+User+Role).

#### Step 1.3: Create an Airbyte Marketo API-only user

Follow the [Marketo documentation to create an API only user](https://docs.marketo.com/display/public/DOCS/Create+an+API+Only+User)

#### Step 1.4: Create a Marketo API custom service

Follow the [Marketo documentation for creating a custom service for use with a REST API](https://docs.marketo.com/display/public/DOCS/Create+a+Custom+Service+for+Use+with+ReST+API).

Make sure to follow the "**Credentials for API Access"** section in the Marketo docs to generate a **Client ID** and **Client Secret.** Once generated, copy those credentials and keep them handy for use in the Airbyte UI later.

#### Step 1.5: Obtain your Endpoint and Identity URLs provided by Marketo

Follow the [Marketo documentation for obtaining your base URL](https://developers.marketo.com/rest-api/base-url/). Specifically, copy your **Endpoint** without "/rest" and keep them handy for use in the Airbyte UI.

We're almost there! Armed with your Endpoint & Identity URLs and your Client ID and Secret, head over to the Airbyte UI to setup Marketo as a source.

## Step 2: Set up the Marketo connector in Airbyte

<!-- env:cloud -->
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click Sources. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Marketo connector and select **Marketo** from the Source type dropdown.
4. Enter the start date, domain URL, client ID and secret
5. Submit the form
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard
2. Set the name for your source
3. Enter the start date
4. Enter the domain URL
5. Enter client ID and secret
6. Click **Set up source**
<!-- /env:oss -->

## Supported sync modes

The Marketo source connector supports the following[ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
 - Full Refresh | Overwrite
 - Full Refresh | Append
 - Incremental  | Append
 - Incremental  | Deduped

## Supported Streams

This connector can be used to sync the following tables from Marketo:

* **activities\_X** where X is an activity type contains information about lead activities of the type X. For example, activities\_send\_email contains information about lead activities related to the activity type `send_email`. See the [Marketo docs](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Activities/getLeadActivitiesUsingGET) for a detailed explanation of what each column means.
* **activity\_types.** Contains metadata about activity types. See the [Marketo docs](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Activities/getAllActivityTypesUsingGET) for a detailed explanation of columns.
* **campaigns.** Contains info about your Marketo campaigns. [Marketo docs](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Campaigns/getCampaignsUsingGET).
* **leads.** Contains info about your Marketo leads. [Marketo docs](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Leads/getLeadByIdUsingGET).
* **lists.** Contains info about your Marketo static lists. [Marketo docs](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Static_Lists/getListByIdUsingGET).
* **programs.** Contains info about your Marketo programs. [Marketo docs](https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Programs/browseProgramsUsingGET).

## Performance considerations

By default, Marketo caps all accounts to 50,000 API calls per day.

By default, this connector caps itself to 40,000 API calls per day. But you can also customize the maximum number of API calls this source connector makes per day to Marketo \(which may be helpful if you have for example other applications which are also hitting the Marketo API\). If this source connector reaches the maximum number you configured, it will not replicate any data until the next day.

If the 50,000 limit is too stringent, contact Marketo support for a quota increase.

## Data type map

| Integration Type | Airbyte Type | Notes                                                                           |
|:-----------------|:-------------|:--------------------------------------------------------------------------------|
| `array`          | `array`      | primitive arrays are converted into arrays of the types described in this table |
| `int`, `long`    | `number`     |                                                                                 |
| `object`         | `object`     |                                                                                 |
| `string`         | `string`     | \`\`                                                                            |
| Namespaces       | No           |                                                                                 |

## Changelog

| Version  | Date       | Pull Request                                             | Subject                                                                                       |
|:---------|:-----------|:---------------------------------------------------------|:----------------------------------------------------------------------------------------------|
| `1.0.0`  | 2023-01-25 | [21790](https://github.com/airbytehq/airbyte/pull/21790) | Fix `activities_*` stream schemas                                                             |
| `0.1.11` | 2022-09-30 | [17445](https://github.com/airbytehq/airbyte/pull/17445) | Do not use temporary files for memory optimization                                            |
| `0.1.10` | 2022-09-30 | [17445](https://github.com/airbytehq/airbyte/pull/17445) | Optimize memory consumption                                                                   |
| `0.1.9`  | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream sate.                                                                   |
| `0.1.7`  | 2022-08-23 | [15817](https://github.com/airbytehq/airbyte/pull/15817) | Improved unit test coverage                                                                   |
| `0.1.6`  | 2022-08-21 | [15824](https://github.com/airbytehq/airbyte/pull/15824) | Fix semi incremental streams: do not ignore start date, make one api call instead of multiple |
| `0.1.5`  | 2022-08-16 | [15683](https://github.com/airbytehq/airbyte/pull/15683) | Retry failed creation of a job instead of skipping it                                         |
| `0.1.4`  | 2022-06-20 | [13930](https://github.com/airbytehq/airbyte/pull/13930) | Process failing creation of export jobs                                                       |
| `0.1.3`  | 2021-12-10 | [8429](https://github.com/airbytehq/airbyte/pull/8578)   | Updated titles and descriptions                                                               |
| `0.1.2`  | 2021-12-03 | [8483](https://github.com/airbytehq/airbyte/pull/8483)   | Improve field conversion to conform schema                                                    |
| `0.1.1`  | 2021-11-29 | [0000](https://github.com/airbytehq/airbyte/pull/0000)   | Fix timestamp value format issue                                                              |
| `0.1.0`  | 2021-09-06 | [5863](https://github.com/airbytehq/airbyte/pull/5863)   | Release Marketo CDK Connector                                                                 |
