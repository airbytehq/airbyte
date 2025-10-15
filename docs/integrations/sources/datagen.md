# DataGen

The DataGen source connector generates synthetic data for testing Airbyte destinations. This connector is designed for internal testing and benchmarking purposes, particularly for evaluating destination performance and data type compatibility.

## Features

The DataGen connector produces two types of data streams:

### Incremental stream

Generates records with a single `id` column that contains monotonically increasing integers. This stream is useful for testing incremental sync behavior and performance.

### All Types stream

Produces records with one column for each Airbyte data type, allowing you to test destination compatibility with various data types. The supported types include:

- **id**: Integer (primary key)
- **string**: String values
- **boolean**: Boolean values
- **number**: Number (double precision)
- **big integer**: Large integer values
- **big decimal**: Large decimal numbers
- **date**: Date values
- **time with time zone**: Time values with timezone information
- **time without time zone**: Time values without timezone
- **timestamp with time zone**: Timestamp values with timezone information
- **timestamp without time zone**: Timestamp values without timezone
- **json**: JSONB formatted data

Note: Array data types were removed in version 0.1.2 due to compatibility issues.

## Changelog

<details>
    <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                            |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------|
| 0.1.2   | 2025-10-13 | [67720](https://github.com/airbytehq/airbyte/pull/67720) | Removal of Array type              |
| 0.1.1   | 2025-10-08 | [67110](https://github.com/airbytehq/airbyte/pull/67110) | Addition of proto types            |
| 0.1.0   | 2025-09-16 | [66331](https://github.com/airbytehq/airbyte/pull/66331) | Creation of initial DataGen Source |
</details>
