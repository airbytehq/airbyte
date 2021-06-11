# Changelog

## [0.1.3] - [#3908](https://github.com/airbytehq/airbyte/pull/3908)
- Added Parquet output.

## [0.1.2] - [#4029](https://github.com/airbytehq/airbyte/pull/4029)
- Fixed `_airbyte_emitted_at` field to be a UTC timestamp. Previously it was a local timestamp, resulting in inconsistent outputs.

## [0.1.1] - [#3973](https://github.com/airbytehq/airbyte/pull/3973)
- Added `AIRBYTE_ENTRYPOINT` in base Docker image for Kubernetes support.

## [0.1.0] - [#3672](https://github.com/airbytehq/airbyte/pull/3672)
- Initial release.
- Created S3 destination with CSV output.
