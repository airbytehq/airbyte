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
| 0.4.2 | 2024-06-06 | [39210](https://github.com/airbytehq/airbyte/pull/39210) | [autopull] Upgrade base image to v1.2.2 |
| 0.4.1 | 2024-05-21 | [38485](https://github.com/airbytehq/airbyte/pull/38485) | [autopull] base image + poetry + up_to_date |
| 0.4.0 | 2023-12-13 | [33431](https://github.com/airbytehq/airbyte/pull/33431) | 🐛 Convex source fix bug where full_refresh stops after one page |
| 0.3.0 | 2023-09-28 | [30853](https://github.com/airbytehq/airbyte/pull/30853) | 🐛 Convex source switch to clean JSON format |
| 0.2.0 | 2023-06-21 | [27226](https://github.com/airbytehq/airbyte/pull/27226) | 🐛 Convex source fix skipped records |
| 0.1.1 | 2023-03-06 | [23797](https://github.com/airbytehq/airbyte/pull/23797) | 🐛 Convex source connector error messages |
| 0.1.0 | 2022-10-24 | [18403](https://github.com/airbytehq/airbyte/pull/18403) | 🎉 New Source: Convex |

</details>
