# Klaviyo Migration Guide

## Upgrading to 1.0.0

`event_properties/items/quantity` for `Events` stream is changed from `integer` to `number`.
For a smooth migration, data reset and schema refresh are needed.

## Upgrading to 2.0.0

Cursor field for `Flows` stream is changed from `created` to `updated`.
For a smooth migration, data reset and schema refresh are needed.
