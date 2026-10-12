import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Kisi Migration Guide

## Upgrading to 0.1.0

This release removes the `user_export_reporters` stream.

### What changed

Kisi removed the `GET /user_export_reporters` endpoint from its API. The endpoint now returns `HTTP 404 {"code":"000404","error":"The endpoint does not exist, please check your request."}` and it is no longer listed in the [Kisi OpenAPI specification](https://api.kisi.io/openapi/apps.yaml) (see the [Kisi API documentation](https://api.kisi.io/docs)). Kisi does not document a replacement endpoint, so the stream has been removed from the connector rather than pointed at a new URL.

### Why

Any sync that included the `user_export_reporters` stream failed with a 404 error from Kisi. Removing the stream lets the remaining 12 streams sync again.

### Who is affected

Only connections that have the `user_export_reporters` stream selected in their catalog. All other streams (`users`, `scheduled_reports`, `role_assignments`, `places`, `reports`, `organizations`, `members`, `logins`, `locks`, `groups`, `floors`, `elevators`) are unchanged, and connections that do not sync `user_export_reporters` need no action beyond upgrading.

### Steps to migrate

1. Upgrade the Kisi source connector to 0.1.0.
2. Open each affected connection, go to the **Schema** tab and click **Refresh source schema**. The `user_export_reporters` stream disappears from the catalog; accept the schema change.
3. Run a sync. Any `user_export_reporters` table already present in your destination is left as-is; drop it manually if you no longer want it.

## Connector upgrade guide

<MigrationGuide />
