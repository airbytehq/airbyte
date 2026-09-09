# Pipedrive Migration Guide

## Upgrading to 2.0.0

Please update your config and reset your data (to match the new format). This version has changed the config to only require an API key.

Configurations that still use the pre-2.0.0 `authorization.api_token` shape are migrated automatically to the top-level `api_token` field on the next sync. Configurations from the OAuth-era versions (0.1.6 to 0.1.14) cannot be migrated automatically. Re-enter your API token in the **API Token** field.

This version also removes the `pipeline_ids` field from the `deal_fields` stream.
