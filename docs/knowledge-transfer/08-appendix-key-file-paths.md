# Appendix: Key File Paths

Master table of all key files referenced in this knowledge transfer, grouped by section. Each path is clickable.

## 8.1 Bulk CDK

[§2 Bulk CDK](02-bulk-cdk.md)

### Module roots and versions

| File | Purpose |
|------|---------|
| [`airbyte-cdk/bulk/`](../../airbyte-cdk/bulk) | Bulk CDK root |
| [`airbyte-cdk/bulk/build.gradle`](../../airbyte-cdk/bulk/build.gradle) | Loads three independent `version.properties`; sets group `io.airbyte.bulk-cdk` |
| [`airbyte-cdk/bulk/core/base/version.properties`](../../airbyte-cdk/bulk/core/base/version.properties) | `base` module version (`1.0.3`) |
| [`airbyte-cdk/bulk/core/extract/version.properties`](../../airbyte-cdk/bulk/core/extract/version.properties) | `extract` module version (`1.1.6`) |
| [`airbyte-cdk/bulk/core/load/version.properties`](../../airbyte-cdk/bulk/core/load/version.properties) | `load` module version (`1.0.11`) |

### Dataflow pipeline

| File | Class / role |
|------|--------------|
| [`airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/DestinationLifecycle.kt`](../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/DestinationLifecycle.kt) | `DestinationLifecycle` (line 22): setup → init streams → pipeline → finalize streams → teardown |
| [`airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/finalization/StreamCompletionTracker.kt`](../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/finalization/StreamCompletionTracker.kt) | `StreamCompletionTracker` (line 15) |
| [`airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/stages/ParseStage.kt`](../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/stages/ParseStage.kt) | Parse stage |
| [`airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/stages/AggregateStage.kt`](../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/stages/AggregateStage.kt) | Aggregate stage |
| [`airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/stages/FlushStage.kt`](../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/stages/FlushStage.kt) | Flush stage |
| [`airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/stages/StateStage.kt`](../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/stages/StateStage.kt) | State stage |
| [`airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/pipeline/DataFlowPipeline.kt`](../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/pipeline/DataFlowPipeline.kt) | Pipeline runner |
| [`airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/pipeline/PipelineRunner.kt`](../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/pipeline/PipelineRunner.kt) | STDIN reader / outer driver |
| [`airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/config/model/`](../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/dataflow/config/model) | Per-concern resource config (no `ResourceConfig` umbrella class) |

### Write API and stream loaders

| File | Class / role |
|------|--------------|
| [`airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/write/StreamLoader.kt`](../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/write/StreamLoader.kt) | `StreamLoader` (line 17): `start()`, `teardown(completedSuccessfully)` |
| [`airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/write/DestinationWriter.kt`](../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/write/DestinationWriter.kt) | `DestinationWriter` (line 13): `setup()`, `createStreamLoader(stream)`, `teardown(hadFailure = false)` |
| [`airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/table/directload/DirectLoadTableStreamLoader.kt`](../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/table/directload/DirectLoadTableStreamLoader.kt) | `DirectLoadTableAppendStreamLoader` (line 26), `…AppendTruncate…` (line 141), `…DedupTruncate…` (line 266) |
| [`airbyte-cdk/bulk/core/load/src/test/kotlin/io/airbyte/cdk/load/table/directload/DirectLoadTableStreamLoaderTest.kt`](../../airbyte-cdk/bulk/core/load/src/test/kotlin/io/airbyte/cdk/load/table/directload/DirectLoadTableStreamLoaderTest.kt) | Drop-temp-on-success / no-drop-on-failure tests (lines 160, 199) |

### Value coercion

| File | Class / role |
|------|--------------|
| [`airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/data/AirbyteValueCoercer.kt`](../../airbyte-cdk/bulk/core/load/src/main/kotlin/io/airbyte/cdk/load/data/AirbyteValueCoercer.kt) | `AirbyteValueCoercer` (line 37), `coerce(value, type, respectLegacyUnions)` (line 38) |
| [`airbyte-cdk/bulk/core/load/src/test/kotlin/io/airbyte/cdk/load/data/AirbyteValueCoercerTest.kt`](../../airbyte-cdk/bulk/core/load/src/test/kotlin/io/airbyte/cdk/load/data/AirbyteValueCoercerTest.kt) | Tests |

## 8.2 Destination ClickHouse

[§3 Destination ClickHouse](03-clickhouse.md)

| File | Class / role |
|------|--------------|
| [`airbyte-integrations/connectors/destination-clickhouse/`](../../airbyte-integrations/connectors/destination-clickhouse) | Connector root (image `2.1.23`) |
| [`airbyte-integrations/connectors/destination-clickhouse/metadata.yaml`](../../airbyte-integrations/connectors/destination-clickhouse/metadata.yaml) | Connector metadata (definitionId `ce0d828e-…`) |
| [`airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/ClickhouseDestination.kt`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/ClickhouseDestination.kt) | Micronaut entry point |
| [`airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/write/ClickHouseWriter.kt`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/write/ClickHouseWriter.kt) | `ClickHouseWriter` (line 23): Append + AppendTruncate dispatch |
| [`airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseSqlGenerator.kt`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseSqlGenerator.kt) | DDL/DML, engine selection (`ReplacingMergeTree` for dedup, lines 51-71) |
| [`airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseAirbyteClient.kt`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseAirbyteClient.kt) | JDBC client |
| [`airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseSqlTypes.kt`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/client/ClickhouseSqlTypes.kt) | Type mapping (`String` for JSON, `Decimal` for number) |
| [`airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/schema/ClickhouseTableSchemaMapper.kt`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/schema/ClickhouseTableSchemaMapper.kt) | Schema mapper |
| [`airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/schema/ClickhouseNamingUtils.kt`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/schema/ClickhouseNamingUtils.kt) | Identifier quoting and length limits |
| [`airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/write/transform/ClickhouseCoercer.kt`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/write/transform/ClickhouseCoercer.kt) | Value coercion |
| [`airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/check/ClickhouseChecker.kt`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/check/ClickhouseChecker.kt) | Check operation |
| [`airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/spec/ClickhouseSpecification.kt`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/spec/ClickhouseSpecification.kt) | Connector spec |
| [`airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/spec/ClickhouseConfiguration.kt`](../../airbyte-integrations/connectors/destination-clickhouse/src/main/kotlin/io/airbyte/integrations/destination/clickhouse/spec/ClickhouseConfiguration.kt) | Parsed config |

## 8.3 Destination Postgres

[§4 Destination Postgres](04-destination-postgres.md)

| File | Class / role |
|------|--------------|
| [`airbyte-integrations/connectors/destination-postgres/`](../../airbyte-integrations/connectors/destination-postgres) | Connector root (image `3.0.13`) |
| [`airbyte-integrations/connectors/destination-postgres/metadata.yaml`](../../airbyte-integrations/connectors/destination-postgres/metadata.yaml) | Connector metadata (definitionId `25c5221d-…`) |
| [`airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/PostgresDestinationV2.kt`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/PostgresDestinationV2.kt) | Micronaut entry point |
| [`airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/schema/PostgresTableSchemaMapper.kt`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/schema/PostgresTableSchemaMapper.kt) | Schema mapper (replaces deleted `PostgresColumnUtils.kt`) |
| [`airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/schema/PostgresColumnManager.kt`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/schema/PostgresColumnManager.kt) | Column add/drop/alter planning |
| [`airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/schema/PostgresNamingUtils.kt`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/schema/PostgresNamingUtils.kt) | Identifier quoting and length limits |
| [`airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/sql/PostgresDirectLoadSqlGenerator.kt`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/sql/PostgresDirectLoadSqlGenerator.kt) | DDL/DML generation; `ALTER COLUMN TYPE` `USING` matrix at lines 599-619 |
| [`airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/client/PostgresAirbyteClient.kt`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/client/PostgresAirbyteClient.kt) | JDBC client; CASCADE error guidance at 455-465 |
| [`airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/write/PostgresWriter.kt`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/write/PostgresWriter.kt) | Loader dispatch (`legacyRawTablesOnly` at 65-69) |
| [`airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/write/load/PostgresInsertBuffer.kt`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/write/load/PostgresInsertBuffer.kt) | Insert buffering; raw-payload branch at 39 |
| [`airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/check/PostgresOssChecker.kt`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/check/PostgresOssChecker.kt) | OSS check (`@Requires(notEnv = [AIRBYTE_CLOUD_ENV])`, line 35) |
| [`airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/check/PostgresCloudChecker.kt`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/check/PostgresCloudChecker.kt) | Cloud check |
| [`airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/spec/PostgresSpecification.kt`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/spec/PostgresSpecification.kt) | Spec (raw mode at 41, CASCADE at 157) |
| [`airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/spec/PostgresConfiguration.kt`](../../airbyte-integrations/connectors/destination-postgres/src/main/kotlin/io/airbyte/integrations/destination/postgres/spec/PostgresConfiguration.kt) | Parsed config (`legacyRawTablesOnly` at 24, 53) |

## 8.4 Other Destinations

[§5 Other Destinations](05-other-destinations.md)

### Snowflake

| File | Class / role |
|------|--------------|
| [`airbyte-integrations/connectors/destination-snowflake/`](../../airbyte-integrations/connectors/destination-snowflake) | Connector root (image `4.0.41`) |
| [`airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/SnowflakeDestination.kt`](../../airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/SnowflakeDestination.kt) | Micronaut entry point |
| [`airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/write/SnowflakeWriter.kt`](../../airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/write/SnowflakeWriter.kt) | Writer; loader dispatch (Append + AppendTruncate + DedupTruncate) |
| [`airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/write/load/SnowflakeRecordFormatter.kt`](../../airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/write/load/SnowflakeRecordFormatter.kt) | Mode-aware record formatter (injected into checker) |
| [`airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/check/SnowflakeChecker.kt`](../../airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/check/SnowflakeChecker.kt) | `SnowflakeChecker` (line 34); injects formatter at line 38 |
| [`airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/sql/SnowflakeDirectLoadSqlGenerator.kt`](../../airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/sql/SnowflakeDirectLoadSqlGenerator.kt) | SQL generation |
| [`airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/schema/SnowflakeTableSchemaMapper.kt`](../../airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/schema/SnowflakeTableSchemaMapper.kt) | Schema mapper (pattern Postgres mirrored) |
| [`airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/write/transform/SnowflakeValueCoercer.kt`](../../airbyte-integrations/connectors/destination-snowflake/src/main/kotlin/io/airbyte/integrations/destination/snowflake/write/transform/SnowflakeValueCoercer.kt) | Value coercion |

### Iceberg / S3 Data Lake

| File | Class / role |
|------|--------------|
| [`airbyte-integrations/connectors/destination-s3-data-lake/`](../../airbyte-integrations/connectors/destination-s3-data-lake) | Active connector root (image `0.3.48`) |
| [`airbyte-integrations/connectors/destination-iceberg/`](../../airbyte-integrations/connectors/destination-iceberg) | Empty husk (metadata + icon only); see [§5.6.2](05-other-destinations.md#562-bring-destination-iceberg-and-destination-s3-data-lake-together) |
| [`airbyte-cdk/bulk/toolkits/load-iceberg-parquet/src/main/kotlin/io/airbyte/cdk/load/data/iceberg/parquet/AirbyteTypeToIcebergSchema.kt`](../../airbyte-cdk/bulk/toolkits/load-iceberg-parquet/src/main/kotlin/io/airbyte/cdk/load/data/iceberg/parquet/AirbyteTypeToIcebergSchema.kt) | Type conversion; `NumberType → DoubleType` (line 70), PK override → `StringType` (lines 111-114) |
| [`airbyte-cdk/bulk/toolkits/load-iceberg-parquet/src/main/kotlin/io/airbyte/cdk/load/data/iceberg/parquet/AirbyteValueToIcebergRecord.kt`](../../airbyte-cdk/bulk/toolkits/load-iceberg-parquet/src/main/kotlin/io/airbyte/cdk/load/data/iceberg/parquet/AirbyteValueToIcebergRecord.kt) | Value side; PK stringification at line 68 |
| [`airbyte-cdk/bulk/toolkits/load-iceberg-parquet/src/main/kotlin/io/airbyte/cdk/load/toolkits/iceberg/parquet/IcebergTableSynchronizer.kt`](../../airbyte-cdk/bulk/toolkits/load-iceberg-parquet/src/main/kotlin/io/airbyte/cdk/load/toolkits/iceberg/parquet/IcebergTableSynchronizer.kt) | Schema sync; deferred `setIdentifierFields` at lines 230, 253, 274 |
| [`airbyte-cdk/bulk/toolkits/load-iceberg-parquet/src/main/kotlin/io/airbyte/cdk/load/toolkits/iceberg/parquet/IcebergTypesComparator.kt`](../../airbyte-cdk/bulk/toolkits/load-iceberg-parquet/src/main/kotlin/io/airbyte/cdk/load/toolkits/iceberg/parquet/IcebergTypesComparator.kt) | `identifierFieldsChanged` detection (lines 71, 97-99) |
| [`airbyte-cdk/bulk/toolkits/load-iceberg-parquet/src/main/kotlin/io/airbyte/cdk/load/toolkits/iceberg/parquet/io/IcebergUtil.kt`](../../airbyte-cdk/bulk/toolkits/load-iceberg-parquet/src/main/kotlin/io/airbyte/cdk/load/toolkits/iceberg/parquet/io/IcebergUtil.kt) | `toIcebergSchema(stream)` at line 174; identifier sort fields at 187 |

### MSSQL

| File | Class / role |
|------|--------------|
| [`airbyte-integrations/connectors/destination-mssql/`](../../airbyte-integrations/connectors/destination-mssql) | Connector root (image `2.2.16`) |
| [`airbyte-integrations/connectors/destination-mssql/src/main/kotlin/io/airbyte/integrations/destination/mssql/v2/config/DataSourceFactory.kt`](../../airbyte-integrations/connectors/destination-mssql/src/main/kotlin/io/airbyte/integrations/destination/mssql/v2/config/DataSourceFactory.kt) | `DataSourceFactory` (line 20); SSH tunnel branch 44-57; `createTunnelSession` at 51 |
| [`airbyte-integrations/connectors/destination-mssql/src/main/kotlin/io/airbyte/integrations/destination/mssql/v2/config/MSSQLSpecification.kt`](../../airbyte-integrations/connectors/destination-mssql/src/main/kotlin/io/airbyte/integrations/destination/mssql/v2/config/MSSQLSpecification.kt) | Spec; SSH at 20-21, 89-107 |
| [`airbyte-integrations/connectors/destination-mssql/src/main/kotlin/io/airbyte/integrations/destination/mssql/v2/config/MSSQLConfiguration.kt`](../../airbyte-integrations/connectors/destination-mssql/src/main/kotlin/io/airbyte/integrations/destination/mssql/v2/config/MSSQLConfiguration.kt) | Parsed config; SSH at 13, 26, 74 |

### Redshift

| File | Class / role |
|------|--------------|
| [`airbyte-integrations/connectors/destination-redshift/`](../../airbyte-integrations/connectors/destination-redshift) | Connector root (Bulk-CDK migration planned, not yet shipped) |

## 8.5 File Transfer

[§6 File Transfer](06-file-transfer.md)

| File | Class / role |
|------|--------------|
| [`airbyte-cdk/bulk/toolkits/legacy-task-loader/src/main/kotlin/io/airbyte/cdk/load/message/DestinationMessage.kt`](../../airbyte-cdk/bulk/toolkits/legacy-task-loader/src/main/kotlin/io/airbyte/cdk/load/message/DestinationMessage.kt) | `DestinationFile` (line 357), `DestinationFileStreamComplete` (464), `DestinationFileDomainMessage` sealed interface (71), `FileReference` (342) |
| [`airbyte-cdk/bulk/toolkits/legacy-task-loader/src/main/kotlin/io/airbyte/cdk/load/message/FileTransferQueueMessageLegacy.kt`](../../airbyte-cdk/bulk/toolkits/legacy-task-loader/src/main/kotlin/io/airbyte/cdk/load/message/FileTransferQueueMessageLegacy.kt) | `FileTransferQueueMessage` sealed interface (line 11); `FileTransferQueueRecord(file: DestinationFile)` (17) |
| [`airbyte-cdk/bulk/toolkits/legacy-task-loader/src/main/kotlin/io/airbyte/cdk/load/message/DestinationMessageFactory.kt`](../../airbyte-cdk/bulk/toolkits/legacy-task-loader/src/main/kotlin/io/airbyte/cdk/load/message/DestinationMessageFactory.kt) | Factory; file-mode dispatch at 66, 70, 123 |
| [`airbyte-cdk/bulk/toolkits/legacy-task-loader/src/main/kotlin/io/airbyte/cdk/load/state/PipelineEventBookkeepingRouter.kt`](../../airbyte-cdk/bulk/toolkits/legacy-task-loader/src/main/kotlin/io/airbyte/cdk/load/state/PipelineEventBookkeepingRouter.kt) | Router; routing types (14-21), file-mode dispatch (66), queue insertion (135-145), stream-complete (297) |
| [`airbyte-cdk/bulk/toolkits/legacy-task-loader/src/main/kotlin/io/airbyte/cdk/load/message/InputMessage.kt`](../../airbyte-cdk/bulk/toolkits/legacy-task-loader/src/main/kotlin/io/airbyte/cdk/load/message/InputMessage.kt) | Input parsing; file branch at 173-180 |
| [`airbyte-cdk/bulk/toolkits/legacy-task-load-object-storage/src/main/kotlin/io/airbyte/cdk/load/write/object_storage/FilePartAccumulatorLegacy.kt`](../../airbyte-cdk/bulk/toolkits/legacy-task-load-object-storage/src/main/kotlin/io/airbyte/cdk/load/write/object_storage/FilePartAccumulatorLegacy.kt) | Object-storage multipart upload assembly (line 41) |

### Configuration flag

| Knob | Where |
|------|-------|
| Micronaut property `airbyte.destination.core.file-transfer.enabled` | Connector `application.yaml` |
| Test fixture `useFileTransfer: Boolean` | `IntegrationTest`, `DestinationProcess`, `Dockerized/NonDockerizedDestination` (both `core/load` and `legacy-task-loader` testFixtures) |

## 8.6 CI/CD Tooling

[§7 CI/CD Tooling](07-ci-cd-tooling.md)

### Per-module version-bump enforcement

| File | Role |
|------|------|
| [`.github/workflows/java-cdk-tests.yml`](../../.github/workflows/java-cdk-tests.yml) | `changes-in-bulk-cdk-packages` (44), `run-check-bulk-cdk-version` (71), `bulk-cdk-version-check-result` aggregator (151) |
| [`.github/workflows/java-bulk-cdk-base-publish.yml`](../../.github/workflows/java-bulk-cdk-base-publish.yml) | Publish workflow for `core/base` |
| [`.github/workflows/java-bulk-cdk-extract-publish.yml`](../../.github/workflows/java-bulk-cdk-extract-publish.yml) | Publish workflow for `core/extract` |
| [`.github/workflows/java-bulk-cdk-load-publish.yml`](../../.github/workflows/java-bulk-cdk-load-publish.yml) | Publish workflow for `core/load` |
| [`.github/workflows/kotlin-bulk-cdk-dokka-publish.yml`](../../.github/workflows/kotlin-bulk-cdk-dokka-publish.yml) | Dokka API-docs publish |

### Auto-upgrade and connector compatibility

| File | Role |
|------|------|
| [`.github/workflows/auto-upgrade-certified-connectors-cdk.yml`](../../.github/workflows/auto-upgrade-certified-connectors-cdk.yml) | Monthly scheduled auto-upgrade (cron line 5) |
| [`.github/workflows/cdk-destination-connector-compatibility-test.yml`](../../.github/workflows/cdk-destination-connector-compatibility-test.yml) | Connector matrix from `get-certified-connectors.sh destinations` (29); auto-file gh-issue (135) |
| [`.github/workflows/cdk-source-connector-compatibility-test.yml`](../../.github/workflows/cdk-source-connector-compatibility-test.yml) | Source-side compatibility test |
| [`.github/workflows/connectors-cdk-version-check.yml`](../../.github/workflows/connectors-cdk-version-check.yml) | Test-only-changes escape hatch |
| [`tools/bin/bulk-cdk/get-certified-connectors.sh`](../../tools/bin/bulk-cdk/get-certified-connectors.sh) | Source of truth for the auto-upgrade matrix |
| [`tools/bin/bulk-cdk/auto-upgrade/bump-connector-metadata.sh`](../../tools/bin/bulk-cdk/auto-upgrade/bump-connector-metadata.sh) | Patch-bumps a connector's `dockerImageTag` |
| [`tools/bin/bulk-cdk/auto-upgrade/populate-connector-changelog.sh`](../../tools/bin/bulk-cdk/auto-upgrade/populate-connector-changelog.sh) | Writes the per-connector changelog entry |

### Slash-command dispatcher and ad-hoc bumps

| File | Role |
|------|------|
| [`.github/workflows/slash-commands.yml`](../../.github/workflows/slash-commands.yml) | Slash-command router (`/bump-version` and `/bump-progressive-rollout-version` at lines 69-70) |
| [`.github/workflows/bump-version-command.yml`](../../.github/workflows/bump-version-command.yml) | Ad-hoc per-connector version bump (`workflow_dispatch` line 28, `bump-version` job 71) |
| [`.github/workflows/bump-progressive-rollout-version-command.yml`](../../.github/workflows/bump-progressive-rollout-version-command.yml) | Delegates to `bump-version-command.yml` |
| [`.github/workflows/update-connector-cdk-version-command.yml`](../../.github/workflows/update-connector-cdk-version-command.yml) | Ad-hoc per-connector CDK reference bump |
| [`.github/workflows/connectors-up-to-date.yml`](../../.github/workflows/connectors-up-to-date.yml) | Periodic check; programmatic version bump at 351 |
| [`.github/workflows/publish-java-cdk-command.yml`](../../.github/workflows/publish-java-cdk-command.yml) | Manual Java CDK publish |

---

[Back to Index](../../KNOWLEDGE-TRANSFER.md)
