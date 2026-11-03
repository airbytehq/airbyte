# Aircall Migration Guide

## Upgrading to 1.0.0

:::danger Risk of permanent data loss
Clearing a stream deletes its data from the destination. Aircall only returns six months of calls, so a re-sync can't restore older `calls` rows. Back up the `calls` table before you clear it.
:::

Version 1.0.0 gives destinations primary keys for deduplication, removes the duplicating incremental mode from `numbers` and `teams`, and corrects declared column types to match the [Aircall API reference](https://developer.aircall.io/api-references/).

### What changed

| Stream     | Change                                                                                                                                                                                                                                                                            |
| :--------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `calls`    | New primary key `id`. `contact`, `assigned_to`, `transferred_by` and `transferred_to` change from string to object. `number.priority` changes from string to integer. `created_at` in `user`, `number`, `teams`, `comments.posted_by` and `tags.tagged_by` is declared as `date-time`. |
| `contacts` | New primary key `id`.                                                                                                                                                                                                                                                             |
| `webhooks` | Primary key changes from `id` to `webhook_id`, the UUID Aircall now uses to identify webhooks. `webhook_id` is added to the schema.                                                                                                                                               |
| `numbers`  | Full refresh only; incremental sync is removed. `priority` changes from string to integer.                                                                                                                                                                                       |
| `teams`    | Full refresh only; incremental sync is removed. `users.created_at` is declared as `date-time`. `webhook_id`, which the Teams API doesn't return, is removed from the schema.                                                                                                       |
| `users`    | `created_at` is declared as `date-time`.                                                                                                                                                                                                                                          |

`company` still has no primary key, because Aircall returns a single company object with no identifier.

Neither the `numbers` nor the `teams` endpoint filters by update time, so their incremental mode re-read every record on every sync. In `Incremental | Append` it added a duplicate of every number and team on each run.

In typed destinations, `date-time` columns become timestamp columns, and the four `calls` fields above become JSON or object columns instead of strings.

### Who needs to act

Connections that sync any of `calls`, `contacts`, `webhooks`, `numbers`, `teams` or `users` must follow the steps below. Connections that sync none of these streams need no action.

### Steps

1. Upgrade the connector to 1.0.0.
2. In the connection, open **Schema** and select **Refresh source schema**. Review and save the changes.
3. For `numbers` and `teams` configured as `Incremental`, select a full refresh sync mode: `Full Refresh | Overwrite` or `Full Refresh | Overwrite + Deduped`. Incremental is no longer offered for these streams.
4. To deduplicate `calls`, `contacts` or `webhooks`, you can now select `Incremental | Append + Deduped` for `calls`, or `Full Refresh | Overwrite + Deduped` for any of the three.
5. Clear the affected streams when Airbyte prompts you, or clear them from the connection's **Status** page. Clearing removes the streams' existing destination tables and their saved state, so the next sync rebuilds them with the new primary keys and column types.
6. Run a sync.

A clear removes every row of the cleared stream from the destination and resets its incremental state. The next sync re-reads `contacts`, `webhooks`, `numbers`, `teams` and `users` in full. `calls` restarts at 186 days before the sync, because Aircall keeps only six months of call history, so older calls cleared from the destination can't be recovered.

### Update downstream queries

- Queries that read `calls.contact`, `calls.assigned_to`, `calls.transferred_by` or `calls.transferred_to` as strings must read them as JSON objects. Aircall documents them as full Contact or User objects.
- Queries that compare `numbers.priority` or `calls.number.priority` with string values such as `'0'` or `'1'` must compare with integers.
- Models that join `webhooks` on `id` should join on `webhook_id`.
- Queries that select `teams.webhook_id` must drop it. The column was always empty.
- Models that remove duplicate `numbers` or `teams` rows from append-mode tables can drop that step after the clear.

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Connector upgrade guide

<MigrationGuide />
