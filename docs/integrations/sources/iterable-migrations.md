# Iterable Migration Guide

## Upgrading to 1.0.0

This version introduces a breaking change to the `users` stream schema.

### What changed

1. **Custom fields moved to `data` object**: Tenant-specific custom data fields are no longer top-level properties. They are now nested inside a generic `data` object, similar to how the `events` stream handles custom event data. The following 52 previously declared top-level properties move under `data`:

   `accepts_marketing`, `address1`, `addresses`, `admin_graphql_api_id`, `aov`, `boughtSas`, `businessLines`, `default_address`, `emailAcquiredDate`, `emailSegmentStatus`, `firstCampaign`, `firstMedium`, `firstName`, `firstOrderCards`, `firstOrderDate`, `firstPurchaseDate`, `firstSource`, `first_name`, `hasAccount`, `hasReminder`, `id`, `lastInteractionTs`, `lastName`, `last_name`, `last_order_id`, `last_order_name`, `ltr`, `mostRecentCampaign`, `mostRecentEmailList`, `mostRecentEmailSegment`, `mostRecentMedium`, `mostRecentOrderCards`, `mostRecentOrderDate`, `mostRecentSource`, `orders_count`, `secondMostRecentOrderCards`, `secondMostRecentOrderDate`, `secondOrderCards`, `secondOrderDate`, `shopify_created_at`, `shopify_updated_at`, `state`, `tax_exempt`, `thirdMostRecentOrderCards`, `thirdMostRecentOrderDate`, `thirdOrderCards`, `thirdOrderDate`, `totalOrders`, `total_spent`, `twelveMonthLtr`, `verified_email`, `zip`

   Any other custom field your Iterable project defines (previously dropped because it was not declared) now also arrives inside `data`.

2. **`itblInternal` flattened to dotted keys**: The `itblInternal` field was previously declared as a nested object. The Iterable export API actually returns Iterable-internal fields as flat dotted keys (e.g. `itblInternal.emailDomain`, `itblInternal.isUnknownUser`). The schema now declares these dotted keys directly; Iterable-internal dotted keys that are not declared in the schema are captured in the `data` object. Note that most destinations transform unsupported characters in column names, so a field like `itblInternal.emailDomain` typically lands as a column named `itblinternal_emaildomain` (exact form depends on the destination's name transformer).

3. **Timestamp values normalized to RFC3339**: the Iterable export API returns `signupDate`, `itblInternal.documentCreatedAt`, and `itblInternal.documentUpdatedAt` as space-separated timestamps (e.g. `2024-01-15 10:30:00 +00:00`), which typed destinations could not parse as `timestamp_with_timezone` and nulled into `_airbyte_meta.changes`. The connector now emits these fields in RFC3339 format (`2024-01-15T10:30:00+00:00`), matching the declared `format: date-time`. `profileUpdatedAt` already arrives in RFC3339 from the API and is unchanged in practice (it passes through the same normalization defensively).

4. **Added standard fields**: `itblUserId`, `whatsAppPhoneNumber`, `city`, and `region` - documented Iterable-managed fields - are now declared in the schema.

### Migration steps

1. Refresh the source schema for the `users` stream in your connection settings, so the new `data` object and dotted-key columns appear.
2. If you have downstream transformations that reference any of the moved top-level fields listed above, update them to read from the `data` object instead (e.g. `data.addresses`, `data.aov`, `data.firstName`).
3. If you reference `itblInternal.emailDomain` or similar fields, note that they are now top-level dotted-key fields rather than nested under an `itblInternal` object, and your destination may transform the `.` in the column name.
4. If you have transformations that parse `signupDate`, note that its values are now RFC3339 (`T` separator, no space before the offset).

### Clearing the stream is optional

The `users` stream has no primary key and syncs in append mode, so no deduplication depends on this change and a clear is not required for correctness. Without a clear, rows synced before the upgrade keep the old shape (custom fields as top-level columns) next to new rows that carry them inside `data` - your history stays intact, and only the new rows follow the new structure.

Clear the stream only if you want the whole table rebuilt in the new shape, and be aware of the trade-off: the `users` stream syncs incrementally by `profileUpdatedAt` starting from your configured start date, so a backfill after a clear only re-syncs profiles updated after that date. Profiles that have not been updated since then are not re-exported by Iterable and would be lost from the destination. Snapshot or copy the destination table before clearing if you need that history.
