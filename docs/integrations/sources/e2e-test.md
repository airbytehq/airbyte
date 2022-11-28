# End-to-End Testing Source

## Overview

This is a mock source for testing the Airbyte pipeline. It can generate arbitrary data streams.

## Mode

### Continuous Feed

**This is the only mode available starting from `2.0.0`.**

This mode allows users to specify a single-stream or multi-stream catalog with arbitrary schema. The schema should be compliant with Json schema [draft-07](https://json-schema.org/draft-07/json-schema-release-notes.html).

The single-stream catalog config exists just for convenient, since in many testing cases, one stream is enough. If only one stream is specified in the multi-stream catalog config, it is equivalent to a single-stream catalog config.

Here is its configuration:

| Mock Catalog Type | Parameters          | Type    | Required | Default             | Notes                                                                                                                                                   |
| ----------------- | ------------------- | ------- | -------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Single-stream     | stream name         | string  | yes      |                     | Name of the stream in the catalog.                                                                                                                      |
|                   | stream schema       | json    | yes      |                     | Json schema of the stream in the catalog. It must be a valid Json schema.                                                                               |
|                   | stream duplication  | integer | no       | 1                   | Duplicate the stream N times to quickly create a multi-stream catalog.                                                                                  |
| Multi-stream      | streams and schemas | json    | yes      |                     | A Json object specifying multiple data streams and their schemas. Each key in this object is one stream name. Each value is the schema for that stream. |
| Both              | max records         | integer | yes      | 100                 | The number of record messages to emit from this connector. Min 1. Max 100 billion.                                                                      |
|                   | random seed         | integer | no       | current time millis | The seed is used in random Json object generation. Min 0. Max 1 million.                                                                                |
|                   | message interval    | integer | no       | 0                   | The time interval between messages in millisecond. Min 0 ms. Max 60000 ms (1 minute).                                                                   |

### Legacy Infinite Feed

This is a legacy mode used in Airbyte integration tests. It has been removed since `2.0.0`. It has a simple catalog with one `data` stream that has the following schema:

```json
{
  "type": "object",
  "properties":
    {
      "column1": { "type": "string" }
    }
}
```

The value of `column1` will be an increasing number starting from `1`.

This mode can generate infinite number of records, which can be dangerous. That's why it is excluded from the Cloud variant of this connector. Usually this mode should not be used.

There are two configurable parameters:

| Parameters       | Type    | Required | Default | Notes                                                                                                              |
| ---------------- | ------- | -------- | ------- | ------------------------------------------------------------------------------------------------------------------ |
| max records      | integer | no       | `null`  | Number of message records to emit. When it is left empty, the connector will generate infinite number of messages. |
| message interval | integer | no       | `null`  | Time interval between messages in millisecond.                                                                     |

### Exception after N

This is a legacy mode used in Airbyte integration tests. It has been removed since `2.0.0`. It throws an `IllegalStateException` after certain number of messages. The number of messages to emit before exception is the only parameter for this mode.

This mode is also excluded from the Cloud variant of this connector.

## Changelog

The OSS and Cloud variants have the same version number. The Cloud variant was initially released at version `1.0.0`.

| Version | Date       | Pull request                                                                                                      | Notes                                                                                                 |
| ------- | ---------- | ----------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| 2.1.3   | 2022-08-25 | [15591](https://github.com/airbytehq/airbyte/pull/15591)                                                          | Declare supported sync modes in catalogs                                                              |
| 2.1.1   | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864)                                                          | Updated stacktrace format for any trace message errors                                                |
| 2.1.0   | 2021-02-12 | [\#10298](https://github.com/airbytehq/airbyte/pull/10298)                                                        | Support stream duplication to quickly create a multi-stream catalog.                                  |
| 2.0.0   | 2021-02-01 | [\#9954](https://github.com/airbytehq/airbyte/pull/9954)                                                          | Remove legacy modes. Use more efficient Json generator.                                               |
| 1.0.1   | 2021-01-29 | [\#9745](https://github.com/airbytehq/airbyte/pull/9745)                                                          | Integrate with Sentry.                                                                                |
| 1.0.0   | 2021-01-23 | [\#9720](https://github.com/airbytehq/airbyte/pull/9720)                                                          | Add new continuous feed mode that supports arbitrary catalog specification. Initial release to cloud. |
| 0.1.2   | 2022-10-18 | [\#18100](https://github.com/airbytehq/airbyte/pull/18100)                                                        | Set supported sync mode on streams                                                                    |
| 0.1.1   | 2021-12-16 | [\#8217](https://github.com/airbytehq/airbyte/pull/8217)                                                          | Fix sleep time in infinite feed mode.                                                                 |
| 0.1.0   | 2021-07-23 | [\#3290](https://github.com/airbytehq/airbyte/pull/3290) [\#4939](https://github.com/airbytehq/airbyte/pull/4939) | Initial release.                                                                                      |
