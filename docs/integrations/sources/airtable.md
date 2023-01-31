# Airtable

This page contains the setup guide and reference information for the Airtable source connector.
This source syncs data from the [Airtable API](https://airtable.com/api).

## Prerequisites

* An active Airtable account
* API Key (Personal Access Token)

## Setup guide
### Step 1: Set up Airtable

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Airtable connector and select **Airtable** from the Source type dropdown.
4. Enter your `API Key` obtained by following [these steps](https://airtable.com/developers/web/guides/personal-access-tokens)
5. Log in and Authorize to the Airtable account and click `Set up source`.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Airtable connector and select **Airtable** from the Source type dropdown.
4. Click **Authenticate your Airtable account**.
5. Proceed with `login` and `grant the permissions` to the target `bases` you need the access to, we recommend to use `All Workspaces and bases`.
6. Log in and Authorize to the Airtable account and click `Set up source`.


## Supported sync modes

The airtable source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |


## Supported Tables and Plans

This source allows you to pull all available tables and bases using `Metadata API` for a given authenticated user. In case you you rename or add a column to any existing table, you will need to recreate the source to update the Airbyte catalog. 

Currently, this source connector works with `standard` subscription plan only.

Standard Scopes required for the successfull authentication:
* data.records:read
* data.recordComments:read
* schema.bases:read

The `Enterprise` level accounts are not supported yet.

## Data type map

| Integration Type       | Airbyte Type                                            | Nullable |
| :--------------------- | :------------------------------------------------------ | -------- |
| `multipleAttachments`  | `string`                                                | Yes      |
| `autoNumber`           | `string`                                                | Yes      |
| `barcode`              | `string`                                                | Yes      |
| `button`               | `string`                                                | Yes      |
| `checkbox`             | `boolean`                                               | Yes      |
| `singleCollaborator`   | `string`                                                | Yes      |
| `count`                | `number`                                                | Yes      |
| `createdBy`            | `string`                                                | Yes      |
| `createdTime`          | `datetime`, `format: date-time`                         | Yes      |
| `currency`             | `number`                                                | Yes      |
| `email`                | `string`                                                | Yes      |
| `date`                 | `string`, `format: date`                                | Yes      |
| `duration`             | `number`                                                | Yes      |
| `lastModifiedBy`       | `string`                                                | Yes      |
| `lastModifiedTime`     | `datetime`, `format: date-time`                         | Yes      |
| `multipleRecordLinks`  | `array with strings`                                    | Yes      |
| `multilineText`        | `string`                                                | Yes      |
| `multipleCollaborators`| `array with strings`                                    | Yes      |
| `multipleSelects`      | `array with strings`                                    | Yes      |
| `number`               | `number`                                                | Yes      |
| `percent`              | `number`                                                | Yes      |
| `phoneNumber`          | `string`                                                | Yes      |
| `rating`               | `number`                                                | Yes      |
| `richText`             | `string`                                                | Yes      |
| `singleLineText`       | `string`                                                | Yes      |
| `externalSyncSource`   | `string`                                                | Yes      |
| `url`                  | `string`                                                | Yes      |
| `formula`              | `array with any`                                        | Yes      |
| `lookup`               | `array with any`                                        | Yes      |
| `multipleLookupValues` | `array with any`                                        | Yes      |
| `rollup`               | `array with any`                                        | Yes      |

* All the fields are `nullable` by default, meaning that the field could be empty.
* The `array with any` - represents the classic array with one of the other Airtable data types inside, such as:
    - string
    - number/integer
    - nested lists/objects
    - etc

### Performance Considerations (Airbyte Open-Source)

See information about rate limits [here](https://airtable.com/developers/web/api/rate-limits).

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------|
| 2.0.0   | 2023-01-27 | [21962](https://github.com/airbytehq/airbyte/pull/21962) | Added casting of native Airtable data types to JsonSchema types
| 1.0.2   | 2023-01-25 | [20934](https://github.com/airbytehq/airbyte/pull/20934) | Added `OAuth2.0` authentication support 
| 1.0.1   | 2023-01-10 | [21215](https://github.com/airbytehq/airbyte/pull/21215) | Fix field names                                        |
| 1.0.0   | 2022-12-22 | [20846](https://github.com/airbytehq/airbyte/pull/20846) | Migrated to Metadata API for dynamic schema generation |
| 0.1.3   | 2022-10-26 | [18491](https://github.com/airbytehq/airbyte/pull/18491) | Improve schema discovery logic                         |
| 0.1.2   | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500) | Improve input configuration copy                       |
| 0.1.1   | 2021-12-06 | [8425](https://github.com/airbytehq/airbyte/pull/8425)   | Update title, description fields in spec               |
