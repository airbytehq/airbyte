# Pipedrive Migration Guide

## Upgrading to 3.0.0

Version 3.0.0 reads `deals`, `persons`, `organizations`, `activities`, `products`, `pipelines`, `stages` and `deal_products` from Pipedrive API v2, adds the `deals_archived` stream, and reads `notes`, `files`, `filters`, `users` and `leads` from their own list endpoints instead of the Recents feed. Incremental streams now backfill every record modified since your Start Date; the one-month history cap of the Recents endpoint is gone.

What changed:

- API v2 record shape: `user_id` becomes `owner_id`; `label` becomes `label_ids`; `active_flag` and `deleted` become `is_deleted`; the denormalized `*_name`, `*_count`, `next_activity_*` and `last_activity_*` fields are removed; `persons.email` and `persons.phone` become the `emails` and `phones` arrays; the `organizations.address_*` fields are removed; custom fields are nested under `custom_fields`; timestamps are RFC3339 and typed as `date-time`. Streams that stay on API v1 keep their `YYYY-MM-DD HH:MM:SS` timestamps, now typed as `date-time` without a time zone.
- `deals` returns not-archived deals and, together with the new `deals_archived` stream, includes deals deleted in the last 30 days with `is_deleted: true`.
- `deal_products` uses the API v2 shape: `discount`, `discount_type`, `is_enabled` and the `billing_*` fields replace `discount_percentage`, `enabled_flag`, `duration` and `duration_unit`.
- Sync modes: `organizations`, `notes` and `leads` are now incremental on `update_time`; `pipelines`, `stages`, `filters` and `users` are full refresh only.
- Primary keys added: `key` on `deal_fields`, `activity_fields`, `organization_fields`, `person_fields` and `product_fields`; `id` on `leads`, `lead_labels`, `activity_types`, `currencies`, `permission_sets`, `roles` and `deal_products`.

To upgrade:

1. Open the connection, go to **Schema** and click **Refresh source schema**.
2. Clear data for `deals`, `persons`, `organizations`, `activities`, `products`, `pipelines`, `stages`, `notes`, `files`, `filters`, `users`, `deal_products`, `deal_fields`, `activity_fields`, `organization_fields`, `person_fields`, `product_fields`, `lead_labels`, `leads`, `activity_types`, `currencies`, `permission_sets` and `roles`.
3. Run a sync.

Rolling back to a 2.x version afterwards requires clearing the state of `deals`, `persons`, `activities`, `products`, `notes`, `leads` and `deal_flow`: 2.x cannot read the RFC3339 cursor values that 3.0.0 saves.

## Upgrading to 2.0.0

Please update your config and reset your data (to match the new format). This version has changed the config to only require an API key.

This version also removes the `pipeline_ids` field from the `deal_fields` stream.

Starting with version 2.4.7, configurations that still use the pre-2.0.0 `authorization.api_token` shape are migrated automatically to the top-level `api_token` field the next time the connection is tested or synced. Configurations from the OAuth-era versions (0.1.6 to 0.1.14) cannot be migrated automatically. Re-enter your API token in the **API Token** field.
