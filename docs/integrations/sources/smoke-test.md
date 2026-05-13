# Smoke Test

The Smoke Test source generates synthetic data for destination regression testing. It produces records across predefined scenarios that cover common destination failure patterns: type variations, null handling, naming edge cases, schema variations, and batch sizes.

This connector is a thin wrapper around [PyAirbyte's smoke test module](https://github.com/airbytehq/PyAirbyte). All business logic lives in the `airbyte.cli.smoke_test_source` module.

:::note
This connector is intended for internal testing and development. It does not connect to any external API.
:::

## Prerequisites

None. This connector generates data locally and requires no external services or credentials.

## Setup guide

No authentication or external setup is required. Add the connector and optionally adjust the configuration options described below.

## Configuration

All configuration fields are optional. With default settings, the connector emits all 14 fast scenarios and excludes the slow `large_batch_stream` scenario.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| **All Fast Streams** | boolean | `true` | Include all fast, non-high-volume predefined streams. |
| **All Slow Streams** | boolean | `false` | Include high-volume streams such as `large_batch_stream`. Excluded by default to keep syncs fast. |
| **Scenario Filter** | array of strings | `[]` | Specific scenario names to include. Combined with the streams enabled by the boolean flags. If empty, only the boolean flags control selection. |
| **Large Batch Record Count** | integer | `1000` | Number of records to generate for the `large_batch_stream` scenario. Set to `0` to emit no records for this stream. |
| **Custom Test Scenarios** | array of objects | `[]` | Additional test scenarios to inject at runtime. Each scenario requires a `name` and `json_schema`. You can optionally include `records`, `primary_key`, and `description`. |

## Supported streams

All streams support full refresh sync only. Incremental sync is not supported.

### Fast scenarios (included by default)

| Stream | Description | Records |
| :--- | :--- | :--- |
| `basic_types` | String, integer, number, boolean columns | 3 |
| `timestamp_types` | Date, datetime, and epoch values | 3 |
| `large_decimals_and_numbers` | High-precision decimals, large integers, boundary values | 3 |
| `nested_json_objects` | Nested objects, arrays, and deep nesting | 2 |
| `null_handling` | Null values across all types, including always-null columns | 3 |
| `column_naming_edge_cases` | CamelCase, dashes, dots, spaces, and SQL reserved words in column names | 1 |
| `table_naming_edge_cases` | Special characters in the stream name | 1 |
| `CamelCaseStreamName` | CamelCase stream name handling | 1 |
| `wide_table_50_columns` | 50-column table with nullable strings | 2 |
| `empty_stream` | Zero records, testing empty dataset handling | 0 |
| `single_record_stream` | Exactly one record | 1 |
| `unicode_and_special_strings` | Emoji, CJK, Cyrillic, and escape sequences | 4 |
| `schema_with_no_primary_key` | No primary key, testing append-only behavior | 3 |
| `long_column_names` | Column names exceeding typical database limits | 1 |

### Slow scenarios (excluded by default)

| Stream | Description | Records |
| :--- | :--- | :--- |
| `large_batch_stream` | Configurable record count for batch and flush testing | 1,000 |

To enable slow streams, set **All Slow Streams** to `true`, or include `large_batch_stream` in the **Scenario Filter** list.

## Features

| Feature | Supported |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Namespaces | No |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2026-03-19 | [75181](https://github.com/airbytehq/airbyte/pull/75181) | Initial release: smoke test source for destination regression testing |

</details>
