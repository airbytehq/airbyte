# Iterable Migration Guide

## Upgrading to 1.0.0

This version introduces a breaking change to the `users` stream schema.

### What changed

1. **Custom fields moved to `data` object**: Tenant-specific custom data fields are no longer top-level properties. They are now nested inside a generic `data` object, similar to how the `events` stream handles custom event data. The following 52 previously declared top-level properties move under `data`:

   `accepts_marketing`, `address1`, `addresses`, `admin_graphql_api_id`, `aov`, `boughtSas`, `businessLines`, `default_address`, `emailAcquiredDate`, `emailSegmentStatus`, `firstCampaign`, `firstMedium`, `firstName`, `firstOrderCards`, `firstOrderDate`, `firstPurchaseDate`, `firstSource`, `first_name`, `hasAccount`, `hasReminder`, `id`, `lastInteractionTs`, `lastName`, `last_name`, `last_order_id`, `last_order_name`, `ltr`, `mostRecentCampaign`, `mostRecentEmailList`, `mostRecentEmailSegment`, `mostRecentMedium`, `mostRecentOrderCards`, `mostRecentOrderDate`, `mostRecentSource`, `orders_count`, `secondMostRecentOrderCards`, `secondMostRecentOrderDate`, `secondOrderCards`, `secondOrderDate`, `shopify_created_at`, `shopify_updated_at`, `state`, `tax_exempt`, `thirdMostRecentOrderCards`, `thirdMostRecentOrderDate`, `thirdOrderCards`, `thirdOrderDate`, `totalOrders`, `total_spent`, `twelveMonthLtr`, `verified_email`, `zip`

   Any other custom field your Iterable project defines (previously dropped because it was not declared) now also arrives inside `data`.

2. **`itblInternal` flattened to dotted keys**: The `itblInternal` field was previously declared as a nested object. The Iterable export API actually returns Iterable-internal fields as flat dotted keys (e.g. `itblInternal.emailDomain`, `itblInternal.isUnknownUser`). The schema now declares these dotted keys directly; Iterable-internal dotted keys that are not declared in the schema are captured in the `data` object. Note that most destinations transform unsupported characters in column names, so a field like `itblInternal.emailDomain` typically lands as a column named `itblinternal_emaildomain` (exact form depends on the destination's name transformer).

3. **Timestamp values normalized to RFC3339**: the Iterable export API returns `signupDate` as a space-separated timestamp (e.g. `2024-01-15 10:30:00 +00:00`), which typed destinations could not parse as `timestamp_with_timezone` and nulled into `_airbyte_meta.changes`. The connector now emits `signupDate` and `profileUpdatedAt` in RFC3339 format (`2024-01-15T10:30:00+00:00`), matching the declared `format: date-time`.

4. **Added standard fields**: `itblUserId`, `whatsAppPhoneNumber`, `city`, and `region` - documented Iterable-managed fields - are now declared in the schema.

### Migration steps

1. Refresh the source schema for the `users` stream in your connection settings.
2. Clear the data for the `users` stream (full reset) to ensure downstream tables reflect the new structure.
3. If you have downstream transformations that reference any of the moved top-level fields listed above, update them to read from the `data` object instead (e.g. `data.addresses`, `data.aov`, `data.firstName`).
4. If you reference `itblInternal.emailDomain` or similar fields, note that they are now top-level dotted-key fields rather than nested under an `itblInternal` object, and your destination may transform the `.` in the column name.
5. If you have transformations that parse `signupDate`, note that its values are now RFC3339 (`T` separator, no space before the offset).
