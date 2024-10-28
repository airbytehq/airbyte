# Klaviyo Migration Guide

## Upgrading to 2.0.0

Streams `campaigns`, `email_templates`, `events`, `flows`, `global_exclusions`, `lists`, and `metrics` are now pulling
data using latest API which has a different schema. Users will need to refresh the source schemas and reset these
streams after upgrading. See the chart below for the API version change.

| Stream            | Current API version | New API version |
|-------------------|---------------------|-----------------|
| campaigns         | v1                  | 2023-06-15      |
| email_templates   | v1                  | 2023-10-15      |
| events            | v1                  | 2023-10-15      |
| flows             | v1                  | 2023-10-15      |
| global_exclusions | v1                  | 2023-10-15      |
| lists             | v1                  | 2023-10-15      |
| metrics           | v1                  | 2023-10-15      |
| profiles          | 2023-02-22          | 2023-02-22      |

## Upgrading to 1.0.0

`event_properties/items/quantity` for `Events` stream is changed from `integer` to `number`.
For a smooth migration, data reset and schema refresh are needed.
