# Waiteraid Migration Guide

## Upgrading to 1.0.0

The `booking` stream now emits one record per item in the API's `bookings` array instead of emitting the entire response envelope as a single record. Booking fields such as `id`, `date`, `amount`, and `guest` are now populated. An empty bookings array emits no records.

The nested envelope field `bookings` is no longer emitted. The `status` field now contains each booking's status, not the API response status. The declared booking schema, configuration, and full-refresh sync mode are unchanged.

Connections that have not upgraded by the upgrade deadline will be disabled rather than automatically switched to the new record shape.

1. Upgrade the connector to version `1.0.0`.
2. Refresh the connection's source schema.
3. Clear existing data for the `booking` stream to remove old response-envelope rows, then run a full-refresh sync to repopulate the destination.
4. Update downstream queries that unpacked the `bookings` array to read individual booking rows, and replace any reliance on the response-level `status` with booking-level status handling.
