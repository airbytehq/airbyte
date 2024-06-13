# Marketo

This page contains the setup guide and reference information for the Marketo source connector.

## Prerequisites

- \(Optional\) Whitelist Airbyte's IP address if needed
- An API-only Marketo User Role
- An Airbyte Marketo API-only user
- A Marketo API Custom Service
- Marketo Client ID & Client Secret
- Marketo Base URL

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

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
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
- Incremental | Append
- Incremental | Deduped

## Supported Streams

This connector can be used to sync the following tables from Marketo:

- **Activities_X** where X is an activity type contains information about lead activities of the type X. For example, activities_send_email contains information about lead activities related to the activity type `send_email`. See the [Marketo docs](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Activities/getLeadActivitiesUsingGET) for a detailed explanation of what each column means.
- **Activity types** Contains metadata about activity types. See the [Marketo docs](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Activities/getAllActivityTypesUsingGET) for a detailed explanation of columns.
- **[Campaigns](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Campaigns/getCampaignsUsingGET)**: Contains info about your Marketo campaigns.
- **[Leads](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Leads/getLeadByIdUsingGET)**: Contains info about your Marketo leads.

:::caution

Available fields are limited by what is presented in the static schema.

:::

- **[Lists](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Static_Lists/getListByIdUsingGET)**: Contains info about your Marketo static lists.
- **[Programs](https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Programs/browseProgramsUsingGET)**: Contains info about your Marketo programs.
- **[Segmentations](https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Segments/getSegmentationUsingGET)**: Contains info about your Marketo programs.

## Performance considerations

By default, Marketo caps all accounts to 50,000 API calls per day.

By default, this connector caps itself to 40,000 API calls per day. But you can also customize the maximum number of API calls this source connector makes per day to Marketo \(which may be helpful if you have for example other applications which are also hitting the Marketo API\). If this source connector reaches the maximum number you configured, it will not replicate any data until the next day.

If the 50,000 limit is too stringent, contact Marketo support for a quota increase.

## Data type map

| Integration Type | Airbyte Type | Notes                                                                           |
| :--------------- | :----------- | :------------------------------------------------------------------------------ |
| `array`          | `array`      | primitive arrays are converted into arrays of the types described in this table |
| `int`, `long`    | `number`     |                                                                                 |
| `object`         | `object`     |                                                                                 |
| `string`         | `string`     | \`\`                                                                            |
| Namespaces       | No           |                                                                                 |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version  | Date       | Pull Request                                             | Subject                                                                                          |
| :------- | :--------- | :------------------------------------------------------- | :----------------------------------------------------------------------------------------------- |
| 1.4.2 | 2024-06-06 | [39297](https://github.com/airbytehq/airbyte/pull/39297) | [autopull] Upgrade base image to v1.2.2 |
| `1.4.1`  | 2024-05-23 | [38631](https://github.com/airbytehq/airbyte/pull/38631) | Update deprecated authenticator package                                                          |
| `1.4.0`  | 2024-04-15 | [36854](https://github.com/airbytehq/airbyte/pull/36854) | Migrate to low-code                                                                              |
| `1.3.2`  | 2024-04-19 | [36650](https://github.com/airbytehq/airbyte/pull/36650) | Updating to 0.80.0 CDK                                                                           |
| `1.3.1`  | 2024-04-12 | [36650](https://github.com/airbytehq/airbyte/pull/36650) | schema descriptions                                                                              |
| `1.3.0`  | 2024-03-19 | [36267](https://github.com/airbytehq/airbyte/pull/36267) | Pin airbyte-cdk version to `^0`                                                                  |
| `1.2.6`  | 2024-02-09 | [35078](https://github.com/airbytehq/airbyte/pull/35078) | Manage dependencies with Poetry.                                                                 |
| `1.2.5`  | 2024-01-15 | [34246](https://github.com/airbytehq/airbyte/pull/34246) | prepare for airbyte-lib                                                                          |
| `1.2.4`  | 2024-01-08 | [33999](https://github.com/airbytehq/airbyte/pull/33999) | Fix for `Export daily quota exceeded`                                                            |
| `1.2.3`  | 2023-08-02 | [28999](https://github.com/airbytehq/airbyte/pull/28999) | Fix for ` _csv.Error: line contains NUL`                                                         |
| `1.2.2`  | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image                  |
| `1.2.1`  | 2023-09-18 | [30533](https://github.com/airbytehq/airbyte/pull/30533) | Fix `json_schema` for stream `Leads`                                                             |
| `1.2.0`  | 2023-06-26 | [27726](https://github.com/airbytehq/airbyte/pull/27726) | License Update: Elv2                                                                             |
| `1.1.0`  | 2023-04-18 | [23956](https://github.com/airbytehq/airbyte/pull/23956) | Add `Segmentations` Stream                                                                       |
| `1.0.4`  | 2023-04-25 | [25481](https://github.com/airbytehq/airbyte/pull/25481) | Minor fix for bug caused by `<=` producing additional API call when there is a single date slice |
| `1.0.3`  | 2023-02-13 | [22938](https://github.com/airbytehq/airbyte/pull/22938) | Specified date formatting in specification                                                       |
| `1.0.2`  | 2023-02-01 | [22203](https://github.com/airbytehq/airbyte/pull/22203) | Handle Null cursor values                                                                        |
| `1.0.1`  | 2023-01-31 | [22015](https://github.com/airbytehq/airbyte/pull/22015) | Set `AvailabilityStrategy` for streams explicitly to `None`                                      |
| `1.0.0`  | 2023-01-25 | [21790](https://github.com/airbytehq/airbyte/pull/21790) | Fix `activities_*` stream schemas                                                                |
| `0.1.12` | 2023-01-19 | [20973](https://github.com/airbytehq/airbyte/pull/20973) | Fix encoding error (note: this change is not in version 1.0.0, but is in later versions          |
| `0.1.11` | 2022-09-30 | [17445](https://github.com/airbytehq/airbyte/pull/17445) | Do not use temporary files for memory optimization                                               |
| `0.1.10` | 2022-09-30 | [17445](https://github.com/airbytehq/airbyte/pull/17445) | Optimize memory consumption                                                                      |
| `0.1.9`  | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream sate.                                                                      |
| `0.1.7`  | 2022-08-23 | [15817](https://github.com/airbytehq/airbyte/pull/15817) | Improved unit test coverage                                                                      |
| `0.1.6`  | 2022-08-21 | [15824](https://github.com/airbytehq/airbyte/pull/15824) | Fix semi incremental streams: do not ignore start date, make one api call instead of multiple    |
| `0.1.5`  | 2022-08-16 | [15683](https://github.com/airbytehq/airbyte/pull/15683) | Retry failed creation of a job instead of skipping it                                            |
| `0.1.4`  | 2022-06-20 | [13930](https://github.com/airbytehq/airbyte/pull/13930) | Process failing creation of export jobs                                                          |
| `0.1.3`  | 2021-12-10 | [8429](https://github.com/airbytehq/airbyte/pull/8578)   | Updated titles and descriptions                                                                  |
| `0.1.2`  | 2021-12-03 | [8483](https://github.com/airbytehq/airbyte/pull/8483)   | Improve field conversion to conform schema                                                       |
| `0.1.1`  | 2021-11-29 | [0000](https://github.com/airbytehq/airbyte/pull/0000)   | Fix timestamp value format issue                                                                 |
| `0.1.0`  | 2021-09-06 | [5863](https://github.com/airbytehq/airbyte/pull/5863)   | Release Marketo CDK Connector                                                                    |

</details>
