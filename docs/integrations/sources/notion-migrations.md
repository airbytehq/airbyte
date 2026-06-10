import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Notion Migration Guide

## Upgrading to 4.0.0

Version 4.0.0 migrates the connector from Notion API version `2022-06-28` to `2025-09-03`. This is a major update driven by Notion's introduction of [multi-source databases](https://developers.notion.com/guides/get-started/upgrade-guide-2025-09-03), where the concept of a "database" has been split into "databases" (containers) and "data sources" (individual schemas/property sets). A "data source" now represents what was previously called a "database" — the table containing pages and properties.

### Breaking Changes

1. **`databases` stream replaced by `data_sources`**: The `databases` stream has been removed and replaced with a new `data_sources` stream. The new stream returns objects with `"object": "data_source"` instead of `"object": "database"`, along with a different parent structure (`database_id` parent and `database_parent` grandparent fields).

2. **`pages` stream parent field updated**: Pages that belong to a database now report `parent.type: "data_source_id"` with a `parent.data_source_id` field instead of `parent.type: "database_id"` with a `parent.database_id` field.

3. **`blocks` stream schema additions**: New `in_trash` boolean field added and `data_source_id` parent type added.

### Migration Steps

A full schema refresh and data reset are required for the **Data Sources** (formerly Databases), **Pages**, and **Blocks** streams.

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Click **Refresh source schema** to pick up the new `data_sources` stream and updated `pages` schema.
   2. Enable the new **Data Sources** stream if you were previously syncing the **Databases** stream.
3. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the **Pages** stream and select **Clear data**.
   2. Do the same for the **Blocks** stream if you are syncing it.
4. Trigger a new sync by clicking **Sync Now**.

For more information on clearing your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Upgrading to 3.0.0

Version 3.0.0 migrates the connector from the Python CDK to the low-code CDK. This migration changes how state is managed for incremental streams nested within a parent stream, which is a breaking change for users syncing the `Comments` stream.

If you are not syncing the `Comments` stream, no action is required.

### Migration Steps

Clear the data for the `Comments` stream:

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the **Comments** stream and select **Clear data**.
3. After the clear succeeds, click **Sync Now**.

For more information on clearing your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Upgrading to 2.0.0

Version 2.0.0 updates the JSON schemas of the Blocks, Databases, and Pages streams to reflect changes in the Notion API:

- The `rich_text` property in Pages changed from an object to an array of `rich_text` objects.
- The `phone_number` property in Pages changed from a string to an object.
- The deprecated `text` property in content blocks was renamed to `rich_text` across the Blocks, Databases, and Pages streams.

### Migration Steps

A full schema refresh and data reset are required.

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Click **Refresh source schema** to pick up the updated schemas.
3. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of each affected stream (**Blocks**, **Databases**, **Pages**) and select **Clear data**.
4. Click **Sync Now**.

For more information on clearing your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Connector upgrade guide

<MigrationGuide />
