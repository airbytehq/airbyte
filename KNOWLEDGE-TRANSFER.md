# Knowledge Transfer: Bulk CDK & Destination Connectors

This document is a knowledge transfer reference for the systems I (Benoit, `@benmoriceau`) have built and maintained in the `airbyte` (OSS) repository between late 2024 and early 2026. The scope is intentionally narrow: the **Bulk CDK** (the next-generation Kotlin Connector Development Kit for destinations) and the connectors that were either built on it or migrated to it. Earlier work on the Airbyte platform (Temporal, per-stream state, Micronaut server migration) lives in the sister repo `airbyte-platform-internal` and is covered there.

Each section explains the architecture, the design decisions that shaped it, the edge cases that bit us, and where to find the code. Every file path and class name has been verified against the working tree on the branch this doc lives on.

The repository is a polyglot monorepo. The Bulk CDK is Kotlin (`airbyte-cdk/bulk/`). Connectors live in `airbyte-integrations/connectors/<name>/` and are mostly Kotlin for the destinations covered here. CI/CD workflows live in `.github/workflows/`.

---

## Table of Contents

| # | Section | Description |
|---|---------|-------------|
| 1 | [Overview](docs/knowledge-transfer/01-overview.md) | Summary of areas covered and codebase map |
| 2 | [Bulk CDK](docs/knowledge-transfer/02-bulk-cdk.md) | The dataflow pipeline, finalization, teardown, `AirbyteValueCoercer`, independent SemVer modules |
| 3 | [Destination ClickHouse](docs/knowledge-transfer/03-clickhouse.md) | Ground-up rewrite on the Bulk CDK -- schema mapping, dedup/truncate via shared loaders, JSON-as-String, batch sizing |
| 4 | [Destination Postgres](docs/knowledge-transfer/04-destination-postgres.md) | Direct Load Postgres -- raw-tables-only mode, OSS/Cloud checker split, schema-utility refactor following the Snowflake pattern |
| 5 | [Snowflake, Iceberg/S3 Data Lake, MSSQL, Redshift](docs/knowledge-transfer/05-other-destinations.md) | Snowflake checker refactor, Iceberg PK type mapping and identifier-field deferral, MSSQL SSH tunnel, Redshift Bulk CDK migration plan |
| 6 | [File Transfer](docs/knowledge-transfer/06-file-transfer.md) | The `DestinationFile` message, legacy file-transfer toolkit, opt-in via Micronaut property |
| 7 | [CI/CD Tooling](docs/knowledge-transfer/07-ci-cd-tooling.md) | CDK / Bulk CDK auto-bump workflows, per-module version-bump enforcement, test-only-changes skip |
| 8 | [Appendix: Key File Paths](docs/knowledge-transfer/08-appendix-key-file-paths.md) | Master table of all key files grouped by area |
