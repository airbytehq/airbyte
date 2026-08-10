# Iterable Migration Guide

## Upgrading to 1.0.0

This version introduces a breaking change to the `users` stream schema.

### What changed

1. **Custom fields moved to `data` object**: Tenant-specific custom data fields (e.g. Shopify fields like `addresses`, `default_address`, `aov`, `totalOrders`, `shopify_created_at`, `admin_graphql_api_id`) are no longer top-level properties. They are now nested inside a generic `data` object, similar to how the `events` stream handles custom event data.

2. **`itblInternal` flattened to dotted keys**: The `itblInternal` field was previously declared as a nested object. The Iterable export API actually returns Iterable-internal fields as flat dotted keys (e.g. `itblInternal.emailDomain`, `itblInternal.isUnknownUser`). The schema now declares these dotted keys directly; Iterable-internal dotted keys that are not declared in the schema are captured in the `data` object.

3. **Date fields updated**: `signupDate` and `profileUpdatedAt` now use `format: date-time` with `airbyte_type: timestamp_with_timezone` for proper downstream typing. The Iterable API returns these as space-separated timestamps (e.g. `2024-01-15 10:30:00 +00:00`).

4. **Added standard fields**: `itblUserId`, `whatsAppPhoneNumber`, `city`, and `region` - documented Iterable-managed fields - are now declared in the schema.

### Migration steps

1. Refresh the source schema for the `users` stream in your connection settings.
2. Clear the data for the `users` stream (full reset) to ensure downstream tables reflect the new structure.
3. If you have downstream transformations that reference removed top-level fields (e.g. `addresses`, `aov`, `totalOrders`), update them to read from the `data` object instead (e.g. `data.addresses`, `data.aov`).
4. If you reference `itblInternal.emailDomain` or similar fields, note that they are now top-level dotted-key fields rather than nested under an `itblInternal` object.
