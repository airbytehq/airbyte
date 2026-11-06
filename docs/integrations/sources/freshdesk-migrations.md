# Freshdesk migration guide

## Upgrading to 4.0.0

:::danger Back up destination data before removing records
Clearing or rebuilding a table removes its existing data. A new sync can only restore
policies that Freshdesk still returns, not historical policies deleted upstream.
Snapshot or back up any data you need to retain before proceeding.
:::

Freshdesk can return SLA policy IDs as numeric strings. Version 4.0.0 converts these
values to integers in `sla_policies.id`, matching the existing schema and integer
ticket references. For example, `"12345678901"` is emitted as `12345678901`.
The primary-key field remains `id`. Other fields and streams are unchanged.

### Who needs to act

Connections that do not sync `sla_policies` need no action. Connections whose policy
IDs have always been integers do not need to clear data. If your destination already
contains string IDs or has widened the ID column to a string type, follow these steps:

1. Back up the affected table, including historical policies no longer available in Freshdesk.
2. Upgrade the connector and refresh the source schema. The declared ID type remains integer;
   refreshing the schema alone does not rewrite existing destination values.
3. Inspect the destination's `sla_policies.id` column and your sync mode:
   - **Full Refresh | Overwrite:** The next sync replaces the current table contents. A separate
     clear is not needed. If your destination retains the string column type or rejects the
     change, recreate the affected table with an integer ID column using the destination's
     supported procedure, then sync again.
   - **Full Refresh | Append:** New records are appended to existing rows. To obtain a clean
     current-policy table rather than mixed historical rows and duplicate IDs, recreate the
     affected table or refresh this stream with existing records removed, then sync again.
     Preserve required history separately before removing records.
4. Verify that the rebuilt table stores `sla_policies.id` as an integer. This stream has no
   incremental cursor and is not bounded by `start_date`; the sync reads the current SLA
   policies returned by the API, not deleted policy history.

### Downstream checks

Re-run SQL and dbt joins between `tickets.sla_policy_id` and `sla_policies.id`. Remove
string-conversion workarounds if they are no longer needed, and update views or exports
that explicitly expect string policy IDs. Upgrading the source does not automatically
narrow a Snowflake column that has already become `VARCHAR`.

Affected connections are disabled at the upgrade deadline rather than automatically
upgraded because destinations containing string IDs may require manual remediation.

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Connector upgrade guide

Use the sync-mode-specific remediation above for this release; a separate clear is
not required for overwrite connections or connections that already store integer IDs.

<MigrationGuide />
