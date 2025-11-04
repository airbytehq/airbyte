# End-to-End Testing (DataGen)

## Overview

The DataGen source connector generates synthetic data for testing and benchmarking Airbyte destinations. Use this connector to validate destination behavior, test data pipeline performance, and develop without connecting to production data sources.

### Output schema

The DataGen connector produces different schemas depending on the selected data generation type.

#### Incremental type

Generates a simple stream with monotonically increasing integers. Despite the name, this type is not related to incremental sync support—it refers to the incrementing pattern of the data itself:

```sql
CREATE TABLE "incremental" (
    "id" int8
);
```

#### All Types type

Generates a stream containing one column for each Airbyte data type, useful for testing destination type handling. This type is faster than the Incremental type and recommended for performance and speed testing:

```sql
CREATE TABLE "all types" (
    "id" int8,
    "string" text,
    "boolean" boolean,
    "number" float8,
    "big integer" numeric,
    "big decimal" numeric,
    "date" date,
    "time with time zone" time with time zone,
    "time without time zone" time,
    "timestamp with time zone" timestamptz,
    "timestamp without time zone" timestamp,
    "json" jsonb,
    "array" int8[]
);
```

### Features

| Feature           | Supported | Notes |
|:------------------|:----------|:------|
| Full Refresh Sync | Yes       |       |

### Requirements

None. This connector generates data locally without external dependencies.

## Setup guide

1. In the navigation bar, click **Sources**.
2. Select **End-to-End Testing (DataGen)** from the source list.
3. Enter a **Source name**.
4. Choose a **Data Generation Type**:
   - **Incremental**: Generates simple sequential integers
   - **All Types**: Generates one column per Airbyte data type
5. Set **Max Records** (default: 100, range: 1 to 100 billion).
6. Optionally configure **Max Concurrency** to control data generation performance.
7. Click **Set up source**.

### Configuration options

| Option | Description | Default | Required |
|:-------|:------------|:--------|:---------|
| Data Generation Type | Pattern for data generation: `Incremental` or `All Types` | Incremental | Yes |
| Max Records | Number of records to generate | 100 | Yes |
| Max Concurrency | Maximum number of concurrent data generators (leave empty to let Airbyte optimize) | Auto | No |

## Changelog

<details>
    <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                            |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------|
| 0.1.1   | 2025-10-08 | [67110](https://github.com/airbytehq/airbyte/pull/67110) | Addition of proto types            |
| 0.1.0   | 2025-09-16 | [66331](https://github.com/airbytehq/airbyte/pull/66331) | Creation of initial DataGen Source |
</details>
