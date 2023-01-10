# Convex

This page contains the setup guide and reference information for the Convex destination connector.

Get started with Convex at the [Convex website](https://convex.dev).
See your data on the [Convex dashboard](https://dashboard.convex.dev/).

## Overview

The Convex destination connector supports Full Refresh Overwrite, Full Refresh Append, Incremental Append, and Incremental Append Dedup.

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

Take care to use the appropriate sync method and frequency for the quantity of data streaming from the source. Performance may suffer with large, frequent syncs with Full Refresh. Prefer Incremental modes when possible.
If you see performance issues,please reach via email to [Convex support](mailto:support@convex.dev) or on [Discord](https://convex.dev/community).

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

| Version | Date       | Pull Request          | Subject                    |
| :------ | :--------- | :-------------------- | :------------------------- |
| 0.1.0   | 2023-01-05 | TODO: link to PR here | 🎉 New Destination: Convex |
