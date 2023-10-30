# Klaviyo Migration Guide

## Upgrading to 2.0.0

The cursor for the `flows` stream has changed from `created` to `updated`.
Users will need to refresh the source schema and reset the `flows` stream after upgrading.

## Upgrading to 1.0.0

`event_properties/items/quantity` for `Events` stream is changed from `integer` to `number`.
For a smooth migration, data reset and schema refresh are needed.
