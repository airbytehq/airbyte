# Iterable Source Migration Guide

## Upgrading to 1.0.0

This version introduces a breaking change to the `users` stream schema.

### What changed

1. **Custom fields moved to `data` object**: Tenant-specific custom data fields (e.g. Shopify fields like `addresses`, `default_address`, `aov`, `totalOrders`, `shopify_created_at`, `admin_graphql_api_id`) are no longer top-level properties. They are now nested inside a generic `data` object, similar to how the `events` stream handles custom event data.

2. **`itblInternal` flattened to dotted keys**: The `itblInternal` field was previously declared as a nested object with sub-fields like `emailDomain`, `documentCreatedAt`, and `documentUpdatedAt`. The Iterable export API actually returns these as flat dotted keys (e.g. `itblInternal.emailDomain`, `itblInternal.documentCreatedAt`). The schema now correctly reflects this structure, and additionally includes `itblInternal.isUnknownUser`.

3. **Removed `format: date-time`** from `signupDate` and `profileUpdatedAt`: The Iterable API returns these fields as space-separated timestamps (e.g. `2024-01-15 10:30:00 +0000`) which are not RFC 3339 compliant. The schema now declares them as plain strings.

4. **Added `itblUserId`**: Iterable's internal numeric user ID is now included in the schema.

### Migration steps

1. Refresh the source schema for the `users` stream in your connection settings.
2. Clear the data for the `users` stream (full reset) to ensure downstream tables reflect the new structure.
3. If you have downstream transformations that reference removed top-level fields (e.g. `addresses`, `aov`, `totalOrders`), update them to read from the `data` object instead (e.g. `data.addresses`, `data.aov`).
4. If you reference `itblInternal.emailDomain` or similar fields, note that they are now top-level dotted-key fields rather than nested under an `itblInternal` object.
