# Smoke Test Source

The Smoke Test source generates synthetic test data for destination regression testing. It produces records across 15 predefined scenarios covering common destination failure patterns: type variations, null handling, naming edge cases, schema variations, and batch sizes.

All business logic lives in PyAirbyte's `airbyte.cli.smoke_test_source` module. This connector is a thin wrapper that delegates to it.

## Features

| Feature | Supported |
|---|---|
| Full Refresh Sync | Yes |
| Incremental Sync | No |

## Getting Started

This connector requires no configuration. It generates synthetic data deterministically.

## Supported Streams

### Fast Scenarios (default)

- `basic_types` — string, integer, number, boolean (3 records)
- `timestamp_types` — date, datetime, epoch values (3 records)
- `large_decimals_and_numbers` — precision, large integers, boundary values (3 records)
- `nested_json_objects` — nested objects, arrays, deep nesting (2 records)
- `null_handling` — null across all types, always-null columns (3 records)
- `column_naming_edge_cases` — CamelCase, dashes, dots, spaces, SQL reserved words (1 record)
- `table_naming_edge_cases` — special characters in stream name (1 record)
- `CamelCaseStreamName` — CamelCase stream name handling (1 record)
- `wide_table_50_columns` — 50-column table with nullable strings (2 records)
- `empty_stream` — zero records (0 records)
- `single_record_stream` — exactly one record (1 record)
- `unicode_and_special_strings` — emoji, CJK, Cyrillic, escape sequences (4 records)
- `schema_with_no_primary_key` — append-only / no dedup (3 records)
- `long_column_names` — column names exceeding typical DB limits (1 record)

### Slow Scenarios

- `large_batch_stream` — 1000 records for batch/flush testing

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---|---|---|---|
| 0.1.0 | 2026-03-18 | [75181](https://github.com/airbytehq/airbyte/pull/75181) | Initial release: smoke test source for destination regression testing |

</details>
