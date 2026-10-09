# Productive Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 0.1.0

### What changed

- The `project_assignments` stream is removed. Productive retired this endpoint in favor of [memberships](https://developer.productive.io/reference/resources/memberships), which the connector already supports.
- The `boards` stream now reads the [folders endpoint](https://developer.productive.io/reference/resources/folders). Its stream name, primary key, and schema remain unchanged, but the resource `type` value is now `folders` rather than `boards`.
- Requests now send the configured organization ID in the `X-Organization-Id` header, as required by Productive.

### Who is affected

Connections selecting `project_assignments` or `boards` must review this migration. The old endpoints return errors and prevent these streams from syncing.

Complete the migration by October 21, 2026. Affected connections that have not upgraded by the deadline will be disabled rather than automatically upgraded, so you can review the stream changes before resuming syncs.

### Migration steps

1. Before upgrading, preserve any historical `project_assignments` data needed by downstream consumers. Productive's memberships are a different resource; their IDs and attributes are not a drop-in replacement for project assignments.
2. Upgrade the source connector to version 0.1.0 or later and refresh the connection's source schema.
3. Accept the removal of `project_assignments`. Select `memberships` if you need project access data, then save the updated connection.
4. Update downstream queries that used `project_assignments` to use the project-related records in `memberships`. Memberships also include access to other resources, so filter using the project relationship or `attributes.target_type` as appropriate for your data.
5. If you sync `boards`, keep the stream selected and update any downstream filters that expect `type = 'boards'` to accept `type = 'folders'`.
6. Run a sync and validate the replacement data before resuming downstream jobs. No configuration or state migration is required for other streams.

## Connector upgrade guide

<MigrationGuide />
