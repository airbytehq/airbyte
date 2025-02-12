# Convex

This page contains the setup guide and reference information for the Convex source connector.

Get started with Convex at the [Convex website](https://convex.dev).
See your data on the [Convex dashboard](https://dashboard.convex.dev/).

## Overview

The Convex source connector supports Full Refresh, Incremental Append, and Incremental Dedupe with deletes.

### Output schema

This source syncs each Convex table as a separate stream.
Check out the list of your tables on the [Convex dashboard](https://dashboard.convex.dev/) in the "Data" view.

Types not directly supported by JSON are encoded as described in the
[JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html)
for the stream.

For example, the Javascript value `new Set(["a", "b"])` is encoded as `{"$set": ["a", "b"]}`, as described by the JSONSchema
`{"type": "object", "description": "Set", "properties": {"$set": {"type": "array", "items": {"type": "string"}}}}`.

Every record includes the client-defined fields for the table, for example a `"messages"` table may contain fields for `"author"` and `"body"`.
Additionally, each document has system fields:

1. `_id` uniquely identifies the document. It is not changed by `.patch` or `.replace` operations.
2. `_creationTime` records a timestamp in milliseconds when the document was initially created. It is not changed by `.patch` or `.replace` operations.
3. `_ts` records a timestamp in nanoseconds when the document was last modified. It can be used for ordering operations in Incremental Append mode, and is automatically used in Incremental Dedupe mode.
4. `_deleted` identifies whether the document was deleted. It can be used to filter deleted documents in Incremental Append mode, and is automatically used to remove documents in Incremental Dedupe mode.

### Features

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental - Append Sync     | Yes        |
| Incremental - Dedupe Sync     | Yes        |
| Replicate Incremental Deletes | Yes        |
| Change Data Capture           | Yes        |
| Namespaces                    | No         |

### Performance considerations

The Convex connector syncs all documents from the historical log.
If you see performance issues due to syncing unnecessary old versions of documents,
please reach out to [Convex support](mailto:support@convex.dev).

## Getting started

### Requirements

- Convex Account
- Convex Project
- Deploy key

### Setup guide

Airbyte integration is available to Convex teams on Professional [plans](https://www.convex.dev/plans).

On the [Convex dashboard](https://dashboard.convex.dev/), navigate to the project that you want to sync.
Note only "Production" deployments should be synced.

In the Data tab, you should see the tables and a sample of the data that will be synced.

1. Navigate to the Settings tab.
2. Copy the "Deployment URL" from the settings page to the `deployment_url` field in Airbyte.
3. Click "Generate a deploy key".
4. Copy the generated deploy key into the `access_key` field in Airbyte.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                          |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------------- |
| 0.4.29 | 2025-02-08 | [52826](https://github.com/airbytehq/airbyte/pull/52826) | Update dependencies |
| 0.4.28 | 2025-01-25 | [52355](https://github.com/airbytehq/airbyte/pull/52355) | Update dependencies |
| 0.4.27 | 2025-01-18 | [51686](https://github.com/airbytehq/airbyte/pull/51686) | Update dependencies |
| 0.4.26 | 2025-01-11 | [51094](https://github.com/airbytehq/airbyte/pull/51094) | Update dependencies |
| 0.4.25 | 2024-12-28 | [50531](https://github.com/airbytehq/airbyte/pull/50531) | Update dependencies |
| 0.4.24 | 2024-12-21 | [50013](https://github.com/airbytehq/airbyte/pull/50013) | Update dependencies |
| 0.4.23 | 2024-12-14 | [49179](https://github.com/airbytehq/airbyte/pull/49179) | Update dependencies |
| 0.4.22 | 2024-11-25 | [48680](https://github.com/airbytehq/airbyte/pull/48680) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.4.21 | 2024-10-29 | [47081](https://github.com/airbytehq/airbyte/pull/47081) | Update dependencies |
| 0.4.20 | 2024-10-12 | [46480](https://github.com/airbytehq/airbyte/pull/46480) | Update dependencies |
| 0.4.19 | 2024-09-28 | [46208](https://github.com/airbytehq/airbyte/pull/46208) | Update dependencies |
| 0.4.18 | 2024-09-21 | [45809](https://github.com/airbytehq/airbyte/pull/45809) | Update dependencies |
| 0.4.17 | 2024-09-14 | [45494](https://github.com/airbytehq/airbyte/pull/45494) | Update dependencies |
| 0.4.16 | 2024-09-07 | [45267](https://github.com/airbytehq/airbyte/pull/45267) | Update dependencies |
| 0.4.15 | 2024-08-31 | [45043](https://github.com/airbytehq/airbyte/pull/45043) | Update dependencies |
| 0.4.14 | 2024-08-24 | [44655](https://github.com/airbytehq/airbyte/pull/44655) | Update dependencies |
| 0.4.13 | 2024-08-17 | [44353](https://github.com/airbytehq/airbyte/pull/44353) | Update dependencies |
| 0.4.12 | 2024-08-10 | [43567](https://github.com/airbytehq/airbyte/pull/43567) | Update dependencies |
| 0.4.11 | 2024-08-03 | [43166](https://github.com/airbytehq/airbyte/pull/43166) | Update dependencies |
| 0.4.10 | 2024-07-27 | [42751](https://github.com/airbytehq/airbyte/pull/42751) | Update dependencies |
| 0.4.9 | 2024-07-20 | [42224](https://github.com/airbytehq/airbyte/pull/42224) | Update dependencies |
| 0.4.8 | 2024-07-13 | [41868](https://github.com/airbytehq/airbyte/pull/41868) | Update dependencies |
| 0.4.7 | 2024-07-10 | [41584](https://github.com/airbytehq/airbyte/pull/41584) | Update dependencies |
| 0.4.6 | 2024-07-09 | [41261](https://github.com/airbytehq/airbyte/pull/41261) | Update dependencies |
| 0.4.5 | 2024-07-06 | [40799](https://github.com/airbytehq/airbyte/pull/40799) | Update dependencies |
| 0.4.4 | 2024-06-25 | [40305](https://github.com/airbytehq/airbyte/pull/40305) | Update dependencies |
| 0.4.3 | 2024-06-22 | [40038](https://github.com/airbytehq/airbyte/pull/40038) | Update dependencies |
| 0.4.2 | 2024-06-06 | [39210](https://github.com/airbytehq/airbyte/pull/39210) | [autopull] Upgrade base image to v1.2.2 |
| 0.4.1 | 2024-05-21 | [38485](https://github.com/airbytehq/airbyte/pull/38485) | [autopull] base image + poetry + up_to_date |
| 0.4.0 | 2023-12-13 | [33431](https://github.com/airbytehq/airbyte/pull/33431) | 🐛 Convex source fix bug where full_refresh stops after one page |
| 0.3.0 | 2023-09-28 | [30853](https://github.com/airbytehq/airbyte/pull/30853) | 🐛 Convex source switch to clean JSON format |
| 0.2.0 | 2023-06-21 | [27226](https://github.com/airbytehq/airbyte/pull/27226) | 🐛 Convex source fix skipped records |
| 0.1.1 | 2023-03-06 | [23797](https://github.com/airbytehq/airbyte/pull/23797) | 🐛 Convex source connector error messages |
| 0.1.0 | 2022-10-24 | [18403](https://github.com/airbytehq/airbyte/pull/18403) | 🎉 New Source: Convex |

</details>
