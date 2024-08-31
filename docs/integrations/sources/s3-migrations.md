# S3 Migration Guide

## Upgrading to 4.0.4

Note: This change is only breaking if you created S3 sources using the API and did not provide `streams.*.format`.

Following 4.0.0 config change, we are removing `streams.*.file_type` field which was redundant with `streams.*.format`. This is a breaking change as `format` now needs to be required. Given that the UI would always populate `format`, only users creating actors using the API and not providing `format` are be affected. In order to fix that, simply set `streams.*.format` to `{"filetype": <file_type>}`.

## Upgrading to 4.0.0

We have revamped the implementation to use the File-Based CDK. The goal is to increase resiliency and reduce development time. Here are the breaking changes:

- [CSV] Mapping of type `array` and `object`: before, they were mapped as `large_string` and hence casted as strings. Given the new changes, if `array` or `object` is specified, the value will be casted as `array` and `object` respectively.
- [CSV] `decimal_point` option is deprecated: It is not possible anymore to use another character than `.` to separate the integer part from non-integer part. Given that the float is format with another character than this, it will be considered as a string.
- [Parquet] `columns` option is deprecated: You can use Airbyte column selection in order to have the same behavior. We don't expect it, but this could have impact on the performance as payload could be bigger.

Given that you are not affected by the above, your migration should proceed automatically once you run a sync with the new connector. To leverage this:

- Upgrade source-s3 to use v4.0.0
- Run at least one sync for all your source-s3 connectors
  - Migration will be performed and an AirbyteControlMessage will be emitted to the platform so that the migrated config is persisted

If a user tries to modify the config after source-s3 is upgraded to v4.0.0 and before there was a sync or a periodic discover check, they will have to update the already provided fields manually. To avoid this, a sync can be executed on any of the connections for this source.

Other than breaking changes, we have changed the UI from which the user configures the source:

- You can now configure multiple streams by clicking on `Add` under `Streams`.
- `Output Stream Name` has been renamed to `Name` when configuring a specific stream.
- `Pattern of files to replicate` field has been renamed `Globs` under the stream configuration.
