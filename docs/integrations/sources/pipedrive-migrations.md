# Pipedrive Migration Guide

## Upgrading to 3.0.0

Version 3.0.0 moves the core entity streams to Pipedrive API v2 and moves notes, files, filters, and users off the Recents endpoint. Record shapes changed: `user_id` is now `owner_id`, denormalized `*_name`, `*_count`, and `next_activity_*` fields are removed, and custom fields are nested under `custom_fields`. API v2 timestamps are RFC3339. Pipelines, stages, filters, and users are full refresh, and primary keys are defined for the affected streams.

Refresh source schemas, clear data for the affected streams, and re-run the sync.


## Upgrading to 2.0.0
Starting with version 2.4.7, configurations that still use the pre-2.0.0 `authorization.api_token` shape are migrated automatically to the top-level `api_token` field the next time the connection is tested or synced. Configurations from the OAuth-era versions (0.1.6 to 0.1.14) cannot be migrated automatically. Re-enter your API token in the **API Token** field.


Please update your config and reset your data (to match the new format). This version has changed the config to only require an API key.

This version also removes the `pipeline_ids` field from the `deal_fields` stream.
