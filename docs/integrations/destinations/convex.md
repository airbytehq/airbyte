# Convex

This page contains the setup guide and reference information for the Convex destination connector.

Get started with Convex at the [Convex website](https://convex.dev).
See your data on the [Convex dashboard](https://dashboard.convex.dev/).

## Overview

The Convex destination connector supports Full Refresh Overwrite, Full Refresh Append, Incremental Append, and Incremental Dedup. Note that for Incremental Dedup, Convex does not store a history table like some other destinations that use DBT, but Convex does store a deduped snapshot.

### Output schema

Each stream will be output into a table in Convex. Convex's table naming rules apply - table names can only contain letters, digits, and underscores and may not start with an underscore.

Each record is a [document](https://docs.convex.dev/using/types) in Convex and is assigned `_id` and `_creationTime` fields during sync.

### Features

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental - Append Sync     | Yes        |
| Incremental - Dedupe Sync     | Yes        |
| Replicate Incremental Deletes | Yes        |
| Change Data Capture           | Yes        |
| Namespaces                    | Yes        |

### Performance considerations

Take care to use the appropriate sync method and frequency for the quantity of data streaming from the source. Performance may suffer with large, frequent syncs with Full Refresh. Prefer Incremental modes when they are supported and especially for large tables.
If you see performance issues, please reach via email to [Convex support](mailto:support@convex.dev) or on [Discord](https://convex.dev/community).

## Getting started

### Requirements

- Convex Account
- Convex Project
- Deploy key

### Setup guide

Airbyte integration is available to all Convex developers.

On the [Convex dashboard](https://dashboard.convex.dev/), navigate to the project and deployment that you want to sync.

1. Navigate to the Settings tab.
2. Copy the "Deployment URL" from the settings page to the `deployment_url` field in Airbyte.
3. Click "Generate a deploy key".
4. Copy the generated deploy key into the `access_key` field in Airbyte.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                           |
|:--------| :--------- | :------------------------------------------------------- | :---------------------------------------------------------------- |
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
