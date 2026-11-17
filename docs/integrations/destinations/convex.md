# Convex

This page contains the setup guide and reference information for the [Convex](https://convex.dev) destination connector.

The connector writes records into a Convex deployment through the Convex streaming import API. You can view the imported data on the [Convex dashboard](https://dashboard.convex.dev/).

## Prerequisites

- A Convex account and a project with the deployment you want to sync to.
- A deploy key for that deployment with the `deployment:backups:import` permission. The connector uses this permission to clear tables, create indexes, and write records. For details, see [Streaming import](https://docs.convex.dev/production/integrations/streaming-import-export#streaming-import) in the Convex documentation.

Streaming import is included with all Convex plans.

## Setup guide

### Step 1: Get your deployment URL and deploy key

1. On the [Convex dashboard](https://dashboard.convex.dev/), open the project and deployment you want to sync to.
2. Go to the deployment's **Settings** page.
3. Copy the **Deployment URL**, for example `https://murky-swan-635.convex.cloud`.
4. In the **Deploy keys** section, click **Generate a deploy key**.
5. Give the key a name, enable the `deployment:backups:import` permission, and create the key. For more information, see [Deploy keys](https://docs.convex.dev/cli/deploy-key-types) in the Convex documentation.
6. Copy the generated deploy key.

### Step 2: Set up the Convex destination in Airbyte

1. In Airbyte, create a new destination and select **Convex**.
2. In the `deployment_url` field, enter the deployment URL from step 1.
3. In the `access_key` field, enter the deploy key from step 1.
4. Click **Set up destination**.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

How each mode behaves in Convex:

- **Overwrite**: At the start of each sync, the connector clears all documents from the stream's table, then writes the new records.
- **Append**: The connector inserts every record as a new document.
- **Append + Deduped**: Before writing, the connector creates a primary key index on the stream's table and waits until it's ready. Convex then replaces the existing document that matches each record's primary key, or inserts a new document if none exists. Convex keeps only the most recent version of each record; it doesn't keep a separate history table.

### Deletes from CDC sources

When a source uses [Change Data Capture (CDC)](https://docs.airbyte.com/platform/understanding-airbyte/cdc), Convex deletes the matching document for any record that has a non-null `_ab_cdc_deleted_at` value. This only happens in **Append + Deduped** mode. In the other modes, the deleted record is inserted like any other record. Convex drops all `_ab_cdc_*` fields before storing documents.

## Output schema

Each stream is written to a Convex table. If the stream has a namespace, the table name is `<namespace>_<stream_name>`. Otherwise, it's the stream name.

Convex table and field names can contain only letters, digits, and underscores, and can't start with an underscore, because Convex reserves those names for system fields. If a table or field name from the source doesn't meet these rules, Convex renames it: it converts the name to lowercase, replaces unsupported characters with underscores, and adds the prefix `source_`. For example, a source field named `_id` is stored as `source_id`.

Each record becomes a [document](https://docs.convex.dev/database/types) in the table. Convex assigns each document the system fields `_id` and `_creationTime`.

### Primary keys for Append + Deduped

Primary key field names must start with a letter and contain only letters, digits, and underscores. Convex's streaming import API doesn't support source primary keys that start with an underscore, such as `_id`. For those streams, select a different primary key or use an Append mode.

## Namespace support

This destination supports [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces). The connector adds the namespace to the start of the table name, as described in [Output schema](#output-schema).

## Performance considerations

The connector sends records to Convex in batches of up to 1,000 records. Large, frequent Full Refresh syncs can perform poorly, because each sync rewrites the whole table. For large tables, use an Incremental mode if the source supports it.

If you see performance issues, contact [Convex support](mailto:support@convex.dev) or ask on the [Convex Discord](https://convex.dev/community).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                           |
|:--------| :--------- | :------------------------------------------------------- | :---------------------------------------------------------------- |
| 0.2.20 | 2026-10-12 | [88404](https://github.com/airbytehq/airbyte/pull/88404) | Mark `access_key` as `airbyte_secret` (boolean instead of the string "true") |
| 0.2.19 | 2026-10-08 | [88204](https://github.com/airbytehq/airbyte/pull/88204) | Preserve checkpoint IDs and fix namespaced overwrite and dedup setup |
| 0.2.18 | 2025-05-10 | [59863](https://github.com/airbytehq/airbyte/pull/59863) | Update dependencies |
| 0.2.17 | 2025-05-03 | [59357](https://github.com/airbytehq/airbyte/pull/59357) | Update dependencies |
| 0.2.16 | 2025-04-26 | [58683](https://github.com/airbytehq/airbyte/pull/58683) | Update dependencies |
| 0.2.15 | 2025-04-19 | [58288](https://github.com/airbytehq/airbyte/pull/58288) | Update dependencies |
| 0.2.14 | 2025-04-12 | [57666](https://github.com/airbytehq/airbyte/pull/57666) | Update dependencies |
| 0.2.13 | 2025-04-05 | [57164](https://github.com/airbytehq/airbyte/pull/57164) | Update dependencies |
| 0.2.12 | 2025-03-29 | [56563](https://github.com/airbytehq/airbyte/pull/56563) | Update dependencies |
| 0.2.11 | 2025-03-22 | [56128](https://github.com/airbytehq/airbyte/pull/56128) | Update dependencies |
| 0.2.10 | 2025-03-08 | [43824](https://github.com/airbytehq/airbyte/pull/43824) | Update dependencies |
| 0.2.9 | 2025-03-03 | [55175](https://github.com/airbytehq/airbyte/pull/55175) | Update to CDK 6.0+ and baseImage 4.0.0 |
| 0.2.8 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.2.7 | 2024-07-31 | [42585](https://github.com/airbytehq/airbyte/pull/42585) | Improve error handling |
| 0.2.6 | 2024-07-09 | [41275](https://github.com/airbytehq/airbyte/pull/41275) | Update dependencies |
| 0.2.5 | 2024-07-06 | [40987](https://github.com/airbytehq/airbyte/pull/40987) | Update dependencies |
| 0.2.4 | 2024-06-25 | [40496](https://github.com/airbytehq/airbyte/pull/40496) | Update dependencies |
| 0.2.3 | 2024-06-22 | [40122](https://github.com/airbytehq/airbyte/pull/40122) | Update dependencies |
| 0.2.2 | 2024-06-04 | [39083](https://github.com/airbytehq/airbyte/pull/39083) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.1 | 2024-05-21 | [38527](https://github.com/airbytehq/airbyte/pull/38527) | [autopull] base image + poetry + up_to_date |
| 0.2.0 | 2023-05-15 | [26103](https://github.com/airbytehq/airbyte/pull/26103) | 🐛 Update Convex destination connector to fix overwrite sync mode |
| 0.1.0 | 2023-01-05 | [21287](https://github.com/airbytehq/airbyte/pull/21287) | 🎉 New Destination: Convex |

</details>
