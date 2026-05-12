# Overview

> *Quick file reference: [Appendix](08-appendix-key-file-paths.md) for the master file-path tables across every section below.*

The work covered in this document spans seven areas of the Airbyte destination stack, all completed between November 2024 and April 2026:

| Area | What It Is | Where It Lives |
|------|-----------|----------------|
| Bulk CDK | The Kotlin destination CDK framework -- pipeline, lifecycle, value coercion, schema mapping toolkit | [`airbyte-cdk/bulk/`](../../airbyte-cdk/bulk) |
| Destination ClickHouse | Ground-up rewrite on the Bulk CDK (was previously a separate Java connector) | [`airbyte-integrations/connectors/destination-clickhouse/`](../../airbyte-integrations/connectors/destination-clickhouse) |
| Destination Postgres | Migration of the Postgres destination to the Bulk CDK with Direct Load | [`airbyte-integrations/connectors/destination-postgres/`](../../airbyte-integrations/connectors/destination-postgres) |
| Destination Snowflake | Migration of the Snowflake destination to the Bulk CDK, plus raw-tables-mode check fix | [`airbyte-integrations/connectors/destination-snowflake/`](../../airbyte-integrations/connectors/destination-snowflake) |
| Iceberg / S3 Data Lake | PK type mapping and Iceberg identifier-field-evolution fix | [`airbyte-integrations/connectors/destination-s3-data-lake/`](../../airbyte-integrations/connectors/destination-s3-data-lake) + [`airbyte-cdk/bulk/toolkits/load-iceberg-parquet/`](../../airbyte-cdk/bulk/toolkits/load-iceberg-parquet) |
| File Transfer | The `DestinationFile` message and legacy file-transfer toolkit on the Bulk CDK | [`airbyte-cdk/bulk/toolkits/legacy-task-loader/`](../../airbyte-cdk/bulk/toolkits/legacy-task-loader), [`airbyte-cdk/bulk/toolkits/legacy-task-load-object-storage/`](../../airbyte-cdk/bulk/toolkits/legacy-task-load-object-storage) |
| CI/CD Tooling | GitHub Actions workflows for auto-bumping CDK / Bulk CDK versions across connectors | [`.github/workflows/`](../../.github/workflows) |

## How these areas fit together

The Bulk CDK ([§2](02-bulk-cdk.md)) provides a common Kotlin framework that every modern destination uses. Each destination implements a small set of pluggable interfaces (`DestinationWriter`, `StreamLoader`, value coercer, SQL generator, schema mapper) and inherits everything else -- pipeline orchestration, lifecycle (setup / per-stream loaders / teardown), value coercion, dedup/truncate semantics, table-direct-load loaders, the AirbyteValue type system -- from the CDK.

ClickHouse ([§3](03-clickhouse.md)) was the first ground-up Bulk-CDK destination I shipped; Snowflake ([§5.1](05-other-destinations.md#51-destination-snowflake)) and Postgres ([§4](04-destination-postgres.md)) were migrations from older Java/Java-CDK connectors. Iceberg / S3 Data Lake ([§5.2](05-other-destinations.md#52-iceberg--s3-data-lake)) was a smaller set of correctness fixes on a connector built by another team.

File Transfer ([§6](06-file-transfer.md)) is the one piece that hasn't yet been ported to the modern `core/load/dataflow/` pipeline. It lives entirely in the `legacy-task-loader` toolkit -- a deliberate scoping decision (see [§6.4](06-file-transfer.md#64-potential-improvements)).

CI/CD Tooling ([§7](07-ci-cd-tooling.md)) wraps all of the above with automation: when the Bulk CDK ships a new version, the auto-upgrade workflow opens PRs against every certified connector to pull in the new version, and the per-module version-bump check rejects PRs that change CDK source without bumping the corresponding `version.properties` file.

## How the docs are organized

Each section is self-contained. The numbering matches the order of dependency: read [§2 Bulk CDK](02-bulk-cdk.md) first if you want to understand the framework, then any individual destination chapter ([§3](03-clickhouse.md)-[§5](05-other-destinations.md)) for connector-specific behavior. Sections [§6 File Transfer](06-file-transfer.md) and [§7 CI/CD Tooling](07-ci-cd-tooling.md) sit on the side. [§8 Appendix](08-appendix-key-file-paths.md) collects every key path into one master table.

Most sections close with a **Past Issues** subsection (real PR-level incidents and what we learned) and a **Potential Improvements** subsection (forward-looking ideas, not a TODO list).

---

[Back to Index](../../KNOWLEDGE-TRANSFER.md)
