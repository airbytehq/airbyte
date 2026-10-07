import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Customer.io Migration Guide

## Upgrading to 1.0.0

:::danger Risk of permanent data loss
Clearing a stream empties its destination table; the next sync reloads it from Customer.io. Customer.io doesn't return deleted automations, actions or one-time sends, so their rows aren't restored, and in Incremental | Append and Full refresh | Append mode the clear also removes every earlier version of each record that previous syncs kept. Back up the affected tables before you clear them if you need that history.
:::

Version 1.0.0 changes the declared type of seven fields whose type didn't match Customer.io's API reference. The values Customer.io returns are unchanged.

<details>
<summary>Retyped fields</summary>

- `campaigns_actions` (automation actions): `from_id` and `reply_to_id` change from string to integer.
- `newsletters` (one-time sends): `sent_at` changes from array to integer, the Unix time in seconds of the last send. Typed destinations wrote it as null under the old type.
- `newsletters`: `tags` becomes an array of strings and `content_ids` an array of integers.
- `campaigns` (automations): `tags` becomes an array of strings and `trigger_segment_ids` an array of integers.

</details>

Under the old types, typed destinations already stored the right values for every field except `sent_at`: `from_id` and `reply_to_id` as text, and the arrays as JSON. SQL warehouses convert `from_id` and `reply_to_id` to integers in place and keep the same array columns. S3 Data Lake stored the arrays as strings and now stores lists, and Avro or Parquet files written after the upgrade hold lists where earlier files hold strings.

If you don't sync `campaigns`, `campaigns_actions` or `newsletters`, you don't need to take any action.

To upgrade:

1. Open the connection, go to **Schema** and click **Refresh source schema**.
2. If your destination is Snowflake or SQL Server and you sync `newsletters`, drop the `sent_at` column from its destination table before the first sync on 1.0.0. The column holds only nulls, and these destinations can't convert it to the new type, so every sync of `newsletters` fails until it's gone; the next sync adds it back as an integer column. On Snowflake, also drop any `SENT_AT_` column with a suffix that a failed sync left behind.
3. Clear only the streams that need it. When Airbyte offers to clear the streams whose schema changed, clear only these:
   - On S3 Data Lake, clear `campaigns`, `campaigns_actions` and `newsletters` if you sync them in Incremental or Full refresh | Append mode; their syncs fail until you do.
   - On other destinations, clear `newsletters` if you sync it in Incremental or Full refresh | Append mode and want `sent_at` on the rows synced before the upgrade. `campaigns` and `campaigns_actions` need no clear.
   - Streams in Full refresh | Overwrite mode are rebuilt on every sync and need no clear.

   If you moved your Start Date later after the first sync, move it back before clearing; the re-sync only reads records last updated on or after it.
4. Run a sync.

If you skip the `newsletters` clear, rows synced before the upgrade keep a null `sent_at`: in Incremental | Append + Deduped mode until the one-time send changes in Customer.io, and permanently in Incremental | Append and Full refresh | Append mode.

### Update downstream consumers

Update casts and joins on the retyped columns: `campaigns_actions.from_id` and `campaigns_actions.reply_to_id` are integers that join to `sender_identities.id`; `newsletters.sent_at` is a Unix timestamp in seconds; `campaigns.trigger_segment_ids` holds `segments.id` values and `newsletters.content_ids` holds `newsletter_variants.id` values. Queries that read the four arrays as JSON strings from S3 Data Lake or from Avro or Parquet files must read them as lists.

## Connector upgrade guide

<MigrationGuide />
