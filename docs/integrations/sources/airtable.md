# Airtable

<HideInUI>

This page contains the setup guide and reference information for the [Airtable](https://airtable.com/api) source connector.

</HideInUI>

## Prerequisites

- An active Airtable account with at least read-only access to the bases you want to sync
- One of the following:
  - On Airbyte Cloud, an Airtable account you can authorize with OAuth
  - A [Personal Access Token](https://airtable.com/developers/web/guides/personal-access-tokens) with access to those bases and the following scopes:
    - `data.records:read`
    - `schema.bases:read`

## Setup guide

### Step 1: Set up Airtable

Create a Personal Access Token. Airbyte Open Source requires one. On Airbyte Cloud, skip this step if you plan to authenticate with OAuth.

1. Go to https://airtable.com/create/tokens and click **Create new token**. Give the token a name.
   ![Generate new Token](/.gitbook/assets/source/airtable/generate_new_token.png)
2. Add the following scopes:

   - `data.records:read`
   - `schema.bases:read`

   ![Add Scopes](/.gitbook/assets/source/airtable/add_scopes.png)

3. Select the bases you want to sync or allow access to all available bases, then click **Create token**.
   ![Add Bases](/.gitbook/assets/source/airtable/add_bases.png)
4. Copy the token from the popup window and store it securely. Airtable only shows it once.

### Step 2: Set up Airtable connector in Airbyte

<!-- env:cloud -->

#### For Airbyte Cloud

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the **Set up the source** page, select **Airtable** from the **Source type** dropdown.
4. Enter a name for the Airtable connector.
5. You can use OAuth or a Personal Access Token to authenticate your Airtable account. We recommend using OAuth for Airbyte Cloud.

   - To authenticate using OAuth, select **OAuth2.0** from the **Authentication** dropdown and click **Authenticate your Airtable account**. Sign in with Airtable, grant access to the bases or workspaces you want to sync, and authorize your account.
   - To authenticate using a Personal Access Token, select **Personal Access Token** from the **Authentication** dropdown and enter the token you created in Step 1.

   :::info
   When using OAuth, you may see a `400` or `401` error causing a failed sync. If this occurs, re-authenticate your Airtable connector by clicking **Authenticate your Airtable account** again in the connector settings.
   :::

6. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source

1. Navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Airtable connector and select **Airtable** from the Source type dropdown.
4. Select **Personal Access Token** from the Authentication dropdown and enter the Access Token for your Airtable account.
5. Click **Set up source**.
<!-- /env:oss -->

### Configuration options

The Airtable connector provides the following optional configuration settings:

- **Number of Concurrent Threads**: Controls the number of concurrent threads used for syncing (default: 5, minimum: 2, maximum: 40). Higher values can improve sync performance when there is I/O wait time, but don't bypass Airtable's rate limits. The connector uses request throttling and retries, but other integrations sharing the same base or account can still cause rate limit errors.
- **Add Base ID to Stream Name**: When enabled, includes the Airtable base ID in table stream names to ensure uniqueness (default: disabled). This is useful if you have cloned Airtable bases with tables that share the same name. Enabling this option changes table stream names and requires a full refresh of those streams. It doesn't change the name of `base_collaborators`.

### Note on changed table names and deleted tables

Stream names include the table name. If you rename a table in Airtable after you start syncing it, the connector stops syncing the old stream. Refresh the source schema and select the stream with the new name to resume syncing that table to a destination table with the new name. Similarly, if you delete a table that was previously syncing, the connector stops syncing it.

## Supported sync modes

All streams support the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/):

- [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)

Table streams also support:

- [Incremental - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) (select `_airtable_id` as the primary key; table streams don't have a source-defined primary key)

### Incremental sync

Incremental sync is available for all table streams, but not for `base_collaborators`. The first incremental sync reads all records with non-empty fields. Later syncs request records whose [`LAST_MODIFIED_TIME()`](https://support.airtable.com/docs/formula-field-reference) is after the saved cursor, minus a 15-minute lookback. For records that were never edited, Airtable leaves `LAST_MODIFIED_TIME()` blank, so the connector compares `CREATED_TIME()` instead.

Keep the following behavior in mind:

- **Cursor field**: The connector adds `_airtable_extracted_at` as the cursor. It contains the end time of the sync window, not the time the record changed. All records emitted in one incremental sync share the same value.
- **Duplicates**: The 15-minute lookback re-reads recently changed records, so Incremental - Append can emit the same record more than once. Use Incremental - Append + Deduped with `_airtable_id` as the primary key to keep one row per record.
- **Computed fields**: `LAST_MODIFIED_TIME()` only tracks changes to non-computed fields. If only a formula, rollup, lookup, or count value changes, the record isn't re-synced.
- **Deleted records**: Incremental syncs don't capture deleted records. To remove deleted records from the destination, use Full Refresh - Overwrite.

## Supported Streams

### Table streams

This source discovers tables from the bases you authorize using Airtable's Metadata API and reads their records using the Web API. Each table is a separate stream named `{base_name}/{table_name}/{table_id}`. If you enable **Add Base ID to Stream Name**, the format is `{base_name}/{base_id}/{table_name}/{table_id}`. Base and table names in stream names are lowercased, with spaces replaced by underscores. Field names are normalized the same way.

In addition to the table's fields, each record includes the following fields:

- `_airtable_id`: The Airtable record ID
- `_airtable_created_time`: The time the record was created
- `_airtable_table_name`: The name of the table
- `_airtable_extracted_at`: The incremental sync cursor. See [Incremental sync](#incremental-sync).

The connector skips records that have no field values. If you rename or add a column to an existing table, refresh the source schema in Airbyte to update the catalog.

### Base collaborators

The `base_collaborators` stream lists the people added directly to each base, one record per person per base, with `base_id`, `base_name`, `userId`, `email`, `permissionLevel`, `createdTime`, and `grantedByUserId`. It reads Airtable's [Get base collaborators](https://airtable.com/developers/web/api/get-base-collaborators) endpoint with the `schema.bases:read` scope the connector already uses. Workspace members who weren't added to the base directly, and groups, aren't included. Records contain collaborator email addresses.

This stream is available starting in version 4.8.0 and supports Full Refresh only. Its source-defined primary key is the combination of `base_id` and `userId`. Use Full Refresh - Overwrite to reflect removed collaborators and current permission levels; Full Refresh - Append retains earlier snapshots.

If you're upgrading an existing connection, refresh the source schema and select `base_collaborators` to start syncing it.

### Performance considerations

Airtable enforces the following [rate limits](https://airtable.com/developers/web/api/rate-limits):

- 5 requests per second per base
- 50 requests per second across all traffic using Personal Access Tokens from a given user or service account

If either limit is exceeded, the API returns a `429` status code and requests must wait 30 seconds before retrying. The connector handles this automatically with built-in backoff and retry logic.

Airtable also applies [monthly API call limits](https://support.airtable.com/docs/managing-api-call-limits-in-airtable) to Free and Team workspaces. Retries don't bypass these quotas. If a sync fails with `PUBLIC_API_BILLING_LIMIT_EXCEEDED`, check your workspace's API usage and wait for the allowance to reset or upgrade your Airtable plan.

## Data type map

| Integration Type        | Airbyte Type                           | Nullable |
| :---------------------- | :------------------------------------- | -------- |
| `multipleAttachments`   | `string`                               | Yes      |
| `autoNumber`            | `number`                               | Yes      |
| `barcode`               | `string`                               | Yes      |
| `button`                | `string`                               | Yes      |
| `checkbox`              | `boolean`                              | Yes      |
| `singleCollaborator`    | `string`                               | Yes      |
| `count`                 | `number`                               | Yes      |
| `createdBy`             | `string`                               | Yes      |
| `aiText`                | `string`                               | Yes      |
| `createdTime`           | `datetime` or `date`                   | Yes      |
| `currency`              | `number`                               | Yes      |
| `email`                 | `string`                               | Yes      |
| `date`                  | `string`, `format: date`               | Yes      |
| `duration`              | `number`                               | Yes      |
| `lastModifiedBy`        | `string`                               | Yes      |
| `dateTime`              | `datetime`, `format: date-time`        | Yes      |
| `lastModifiedTime`      | `datetime`, `date`, or `string`        | Yes      |
| `multipleRecordLinks`   | `array with strings`                   | Yes      |
| `multilineText`         | `string`                               | Yes      |
| `multipleCollaborators` | `array with strings`                   | Yes      |
| `multipleSelects`       | `array with strings`                   | Yes      |
| `number`                | `number`                               | Yes      |
| `percent`               | `number`                               | Yes      |
| `phoneNumber`           | `string`                               | Yes      |
| `rating`                | `number`                               | Yes      |
| `richText`              | `string`                               | Yes      |
| `singleLineText`        | `string`                               | Yes      |
| `singleSelect`          | `string`                               | Yes      |
| `simpleText`            | `string`                               | Yes      |
| `manualSort`            | `string`                               | Yes      |
| `externalSyncSource`    | `string`                               | Yes      |
| `url`                   | `string`                               | Yes      |
| `formula`               | `string`, `number`, or `array`         | Yes      |
| `lookup`                | `array` (typed by result field)        | Yes      |
| `multipleLookupValues`  | `array` (typed by result field)        | Yes      |
| `rollup`                | `array` (typed by result field)        | Yes      |

- All fields are nullable, meaning any field value could be empty.
- `createdTime` and `lastModifiedTime` emit `datetime` or `date` depending on the field's display configuration in Airtable. If no result type is configured for `lastModifiedTime`, it emits `string`.
- `formula` emits `number` when the result type is numeric (number, currency, percent, duration), `array` for array-producing formulas (ARRAYCOMPACT, ARRAYFLATTEN, ARRAYUNIQUE, ARRAYSLICE), and `string` otherwise.
- `lookup`, `multipleLookupValues`, and `rollup` emit typed arrays matching the referenced field's type (e.g., array of numbers for numeric fields, array of strings for text fields).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version    | Date       | Pull Request                                             | Subject                                                                                 |
|:-----------|:-----------|:---------------------------------------------------------|:----------------------------------------------------------------------------------------|
| 4.8.0 | 2026-11-05 | [90312](https://github.com/airbytehq/airbyte/pull/90312) | Add base_collaborators stream |
| 4.7.0 | 2026-11-03 | [89000](https://github.com/airbytehq/airbyte/pull/89000) | Add incremental sync support for table streams |
| 4.6.43 | 2026-10-13 | [88520](https://github.com/airbytehq/airbyte/pull/88520) | Update dependencies |
| 4.6.42 | 2026-10-06 | [87744](https://github.com/airbytehq/airbyte/pull/87744) | Update dependencies |
| 4.6.41 | 2026-09-29 | [87090](https://github.com/airbytehq/airbyte/pull/87090) | Update dependencies |
| 4.6.40 | 2026-09-22 | [86538](https://github.com/airbytehq/airbyte/pull/86538) | Update dependencies |
| 4.6.39 | 2026-09-15 | [85936](https://github.com/airbytehq/airbyte/pull/85936) | Update dependencies |
| 4.6.38 | 2026-09-08 | [85385](https://github.com/airbytehq/airbyte/pull/85385) | Update dependencies |
| 4.6.37 | 2026-08-18 | [84475](https://github.com/airbytehq/airbyte/pull/84475) | Update dependencies |
| 4.6.36 | 2026-08-11 | [83837](https://github.com/airbytehq/airbyte/pull/83837) | Update dependencies |
| 4.6.35 | 2026-08-04 | [83351](https://github.com/airbytehq/airbyte/pull/83351) | Update dependencies |
| 4.6.34 | 2026-07-28 | [82799](https://github.com/airbytehq/airbyte/pull/82799) | Update dependencies |
| 4.6.33 | 2026-07-21 | [82303](https://github.com/airbytehq/airbyte/pull/82303) | Update dependencies |
| 4.6.32 | 2026-07-14 | [81711](https://github.com/airbytehq/airbyte/pull/81711) | Update dependencies |
| 4.6.31 | 2026-07-07 | [80955](https://github.com/airbytehq/airbyte/pull/80955) | Update dependencies |
| 4.6.30 | 2026-06-24 | [80771](https://github.com/airbytehq/airbyte/pull/80771) | Upgrade CDK to 7.23.3 |
| 4.6.29 | 2026-06-23 | [80374](https://github.com/airbytehq/airbyte/pull/80374) | Update dependencies |
| 4.6.28 | 2026-06-16 | [79749](https://github.com/airbytehq/airbyte/pull/79749) | Update dependencies |
| 4.6.27 | 2026-06-09 | [79201](https://github.com/airbytehq/airbyte/pull/79201) | Update dependencies |
| 4.6.26 | 2026-06-02 | [76518](https://github.com/airbytehq/airbyte/pull/76518) | Update dependencies |
| 4.6.25 | 2026-04-13 | [76276](https://github.com/airbytehq/airbyte/pull/76276) | Rename "concurrent workers" to "concurrent threads" in connector spec |
| 4.6.24 | 2026-03-10 | [74540](https://github.com/airbytehq/airbyte/pull/74540) | Update dependencies |
| 4.6.23 | 2026-02-24 | [73755](https://github.com/airbytehq/airbyte/pull/73755) | Update dependencies |
| 4.6.22 | 2026-02-17 | [73390](https://github.com/airbytehq/airbyte/pull/73390) | Update dependencies |
| 4.6.21 | 2026-02-10 | [72993](https://github.com/airbytehq/airbyte/pull/72993) | Update dependencies |
| 4.6.20 | 2026-02-03 | [72632](https://github.com/airbytehq/airbyte/pull/72632) | Update dependencies |
| 4.6.19 | 2026-01-20 | [71999](https://github.com/airbytehq/airbyte/pull/71999) | Update dependencies |
| 4.6.18 | 2026-01-14 | [71506](https://github.com/airbytehq/airbyte/pull/71506) | Update dependencies |
| 4.6.17 | 2026-01-08 | [70856](https://github.com/airbytehq/airbyte/pull/70856) | Add configurable option to include base_id in stream names for uniqueness |
| 4.6.16 | 2026-01-08 | [71229](https://github.com/airbytehq/airbyte/pull/71229) | Promoting release candidate 4.6.16-rc.1 to a main version. |
| 4.6.16-rc.1 | 2025-12-10 | [69778](https://github.com/airbytehq/airbyte/pull/69778) | Add HTTPAPIBudget and concurrency_level for improved sync performance |
| 4.6.15 | 2025-12-02 | [70296](https://github.com/airbytehq/airbyte/pull/70296) | Bump memory for discover to 3GB and check to 1.5GB |
| 4.6.14 | 2025-11-25 | [69916](https://github.com/airbytehq/airbyte/pull/69916) | Update dependencies |
| 4.6.13 | 2025-10-29 | [69029](https://github.com/airbytehq/airbyte/pull/69029) | Update dependencies |
| 4.6.12 | 2025-10-14 | [65633](https://github.com/airbytehq/airbyte/pull/65633) | Update dependencies |
| 4.6.11 | 2025-09-09 | [65991](https://github.com/airbytehq/airbyte/pull/65991) | Update to CDK v7.0.0 |
| 4.6.10 | 2025-08-23 | [65352](https://github.com/airbytehq/airbyte/pull/65352) | Update dependencies |
| 4.6.9 | 2025-08-09 | [64651](https://github.com/airbytehq/airbyte/pull/64651) | Update dependencies |
| 4.6.8 | 2025-08-02 | [64436](https://github.com/airbytehq/airbyte/pull/64436) | Update dependencies |
| 4.6.7 | 2025-07-21 | [63281](https://github.com/airbytehq/airbyte/pull/63281) | Bump default Memory on DISCOVER to 2.5GB |
| 4.6.6 | 2025-07-15 | [63309](https://github.com/airbytehq/airbyte/pull/63309) | Adds `type` property to `config_normalization_rules` in manifest |
| 4.6.5 | 2025-07-12 | [43886](https://github.com/airbytehq/airbyte/pull/43886) | Update dependencies |
| 4.6.4 | 2025-07-10 | [62894](https://github.com/airbytehq/airbyte/pull/62894) | Bump default Memory on DISCOVER to 2GB |
| 4.6.3 | 2025-07-03 | [62118](https://github.com/airbytehq/airbyte/pull/62118) | Bump default Memory on DISCOVER to 1.5 GB |
| 4.6.2 | 2025-06-17 | [61643](https://github.com/airbytehq/airbyte/pull/61643) | Bump default Memory on DISCOVER to 1GB |
| 4.6.1 | 2025-06-05 | [61394](https://github.com/airbytehq/airbyte/pull/61394) | Fix schema issue related to migration |
| 4.6.0 | 2025-06-04 | [60875](https://github.com/airbytehq/airbyte/pull/60875) | Migrate to manifest-only |
| 4.5.1 | 2025-02-13 | [53672](https://github.com/airbytehq/airbyte/pull/53672) | Add type for aiText and lastModifiedTime, when result type is null |
| 4.5.0 | 2025-02-12 | [53657](https://github.com/airbytehq/airbyte/pull/53657) | Promoting release candidate 4.5.0-rc.4 to a main version. |
| 4.5.0-rc.4 | 2025-02-04 | [53156](https://github.com/airbytehq/airbyte/pull/53156) | Add default type for `rollup`, `lookuo` and `multiplelookup`, add new type `manualSort` |
| 4.5.0-rc.3 | 2025-01-29 | [52624](https://github.com/airbytehq/airbyte/pull/52624) | Fix type for multipleLookupValues fields |
| 4.5.0-rc.2 | 2025-01-28 | [52595](https://github.com/airbytehq/airbyte/pull/52595) | Fix type for datetime fields |
| 4.5.0-rc.1 | 2025-01-27 | [49813](https://github.com/airbytehq/airbyte/pull/49813) | Update to low-code |
| 4.4.0 | 2024-07-16 | [41160](https://github.com/airbytehq/airbyte/pull/41160) | Update CDK version to v3.5.2 |
| 4.3.1 | 2024-07-16 | [41536](https://github.com/airbytehq/airbyte/pull/41536) | Update dependencies |
| 4.3.0 | 2024-07-16 | [41072](https://github.com/airbytehq/airbyte/pull/41072) | Update CDK version to v2.4.0 |
| 4.2.6 | 2024-07-09 | [41080](https://github.com/airbytehq/airbyte/pull/41080) | Update dependencies |
| 4.2.5 | 2024-07-06 | [40789](https://github.com/airbytehq/airbyte/pull/40789) | Update dependencies |
| 4.2.4 | 2024-06-25 | [40290](https://github.com/airbytehq/airbyte/pull/40290) | Update dependencies |
| 4.2.3 | 2024-06-22 | [40085](https://github.com/airbytehq/airbyte/pull/40085) | Update dependencies |
| 4.2.2 | 2024-06-04 | [39089](https://github.com/airbytehq/airbyte/pull/39089) | [autopull] Upgrade base image to v1.2.1 |
| 4.2.1 | 2024-05-29 | [38765](https://github.com/airbytehq/airbyte/pull/38765) | Fix next_page_token() to correctly adhere to HttpStream interface |
| 4.2.0 | 2024-03-19 | [36267](https://github.com/airbytehq/airbyte/pull/36267) | Pin airbyte-cdk version to `^0` |
| 4.1.6 | 2024-02-12 | [35149](https://github.com/airbytehq/airbyte/pull/35149) | Manage dependencies with Poetry. |
| 4.1.5 | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 4.1.4 | 2023-10-19 | [31360](https://github.com/airbytehq/airbyte/pull/31360) | Update docstings |
| 4.1.3 | 2023-10-13 | [31360](https://github.com/airbytehq/airbyte/pull/31360) | Update error message for invalid permissions |
| 4.1.2 | 2023-10-10 | [31215](https://github.com/airbytehq/airbyte/pull/31215) | Exclude bases without permission |
| 4.1.1 | 2023-10-10 | [31119](https://github.com/airbytehq/airbyte/pull/31119) | Add user-friendly error message when refresh token has expired |
| 4.1.0 | 2023-10-10 | [31044](https://github.com/airbytehq/airbyte/pull/31044) | Add source table name to output records |
| 4.0.0 | 2023-10-09 | [31181](https://github.com/airbytehq/airbyte/pull/31181) | Additional schema processing for the FORMULA schema type: Convert to simple data types |
| 3.0.1 | 2023-05-10 | [25946](https://github.com/airbytehq/airbyte/pull/25946) | Skip stream if it does not appear in catalog |
| 3.0.0 | 2023-03-20 | [22704](https://github.com/airbytehq/airbyte/pull/22704) | Fix for stream name uniqueness |
| 2.0.4 | 2023-03-15 | [24093](https://github.com/airbytehq/airbyte/pull/24093) | Update spec and doc |
| 2.0.3 | 2023-02-02 | [22311](https://github.com/airbytehq/airbyte/pull/22311) | Fix for `singleSelect` types when discovering the schema |
| 2.0.2 | 2023-02-01 | [22245](https://github.com/airbytehq/airbyte/pull/22245) | Fix for empty `result` object when discovering the schema |
| 2.0.1 | 2023-02-01 | [22224](https://github.com/airbytehq/airbyte/pull/22224) | Fixed broken `API Key` authentication |
| 2.0.0 | 2023-01-27 | [21962](https://github.com/airbytehq/airbyte/pull/21962) | Added casting of native Airtable data types to JsonSchema types |
| 1.0.2 | 2023-01-25 | [20934](https://github.com/airbytehq/airbyte/pull/20934) | Added `OAuth2.0` authentication support |
| 1.0.1 | 2023-01-10 | [21215](https://github.com/airbytehq/airbyte/pull/21215) | Fix field names |
| 1.0.0 | 2022-12-22 | [20846](https://github.com/airbytehq/airbyte/pull/20846) | Migrated to Metadata API for dynamic schema generation |
| 0.1.3 | 2022-10-26 | [18491](https://github.com/airbytehq/airbyte/pull/18491) | Improve schema discovery logic |
| 0.1.2 | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500) | Improve input configuration copy |
| 0.1.1 | 2021-12-06 | [8425](https://github.com/airbytehq/airbyte/pull/8425) | Update title, description fields in spec |

</details>
