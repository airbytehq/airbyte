# End-to-End Testing Source for Cloud

## Overview

This is a mock source for testing the Airbyte pipeline. It can generate arbitrary data streams. It is a subset of what is in [End-to-End Testing Source](e2e-test.md) in Open Source to avoid Airbyte Cloud users accidentally in curring a huge bill.

## Mode

### Continuous Feed

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

## Changelog

<details>
  <summary>Expand to review</summary>
  
The OSS and Cloud variants have the same version number. The Cloud variant was initially released at version `1.0.0`.

| Version | Date       | Pull request                                             | Subject                                             |
| ------- | ---------- | -------------------------------------------------------- | --------------------------------------------------- |
| 2.2.1   | 2024-02-13 | [35231](https://github.com/airbytehq/airbyte/pull/35231) | Adopt JDK 0.20.4.                                   |
| 2.1.5   | 2023-10-06 | [31092](https://github.com/airbytehq/airbyte/pull/31092) | Bring in changes from oss                           |
| 2.1.4   | 2023-03-01 | [23656](https://github.com/airbytehq/airbyte/pull/23656) | Fix inheritance between e2e-test and e2e-test-cloud |
| 0.1.0   | 2021-07-23 | [9720](https://github.com/airbytehq/airbyte/pull/9720)   | Initial release.                                    |

</details>