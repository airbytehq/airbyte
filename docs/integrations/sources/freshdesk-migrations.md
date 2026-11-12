import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Freshdesk Migration Guide

## Upgrading to 4.0.0

### What changed

The `sla_policies` stream now emits its primary key `id` as an integer. Since version 3.3.6, this field was emitted as a digit string, even though the stream schema declared it as an integer. Version 4.0.0 converts digit strings returned by the Freshdesk API to integers before emitting records.

### Who needs to act

Connections syncing `sla_policies` must refresh that stream. Connections that do not sync `sla_policies` need no migration steps. Other streams are unchanged.

### Steps

1. Upgrade the Freshdesk connector to version 4.0.0.
2. In the connection's **Schema** tab, select **Refresh source schema**, review the schema, and save it. The declared type of `sla_policies.id` remains integer; the emitted values now match it.
3. Check the destination's `sla_policies.id` column. If the destination widened it to a string, back up any data you need to retain, then clear the `sla_policies` stream's destination data so that the column can be rebuilt as an integer. Clearing data deletes existing destination records, including historical records no longer available in Freshdesk.
4. Refresh the `sla_policies` stream to re-sync its records, and verify that the destination stores `id` as an integer.
5. Update downstream queries or models that treat `sla_policies.id` as a string to use an integer instead.

## Connector upgrade guide

<MigrationGuide />
