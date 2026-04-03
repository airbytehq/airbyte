# Implementation Plan: Migrate Redshift Destination to Bulk CDK (Direct Load)

## Context

**Current state:** Redshift destination uses the old Java CDK (`0.46.0`) with a raw-table-based typing/deduping architecture. Records are loaded as JSON blobs into a `SUPER` column in raw tables, then a separate T&D step extracts and types them into final tables.

**Target state:** Migrate to the Bulk CDK (`1.0.7`) using the "Direct Load" pattern (like Snowflake, Postgres, and ClickHouse). Records will be written directly to typed final tables. The connector will also support a legacy raw-table-only fallback mode (`disable_type_dedupe=true`).

**Primary reference:** Postgres (`destination-postgres`, CDK `1.0.6`) -- Redshift is PostgreSQL-derived, so the Postgres connector is the closest architectural match. The SQL dialect is nearly identical, differing only in Redshift-specific features (SUPER type, S3 COPY, sort keys vs indexes, etc.).

**Secondary references:** Snowflake (`destination-snowflake`, CDK `1.0.6`) for S3 staging patterns and config migration, ClickHouse (`destination-clickhouse`, CDK `0.2.8`) for alternative dedup strategies.

---

## Key CDK Insight: Column Name Mapping Is Automatic

The Bulk CDK **fully automates column name mapping**. Connectors do NOT need to manually manage `ColumnNameMapping`. The flow is:

1. The connector implements `TableSchemaMapper.toColumnName(name)` with its naming convention (e.g., lowercase + sanitize for Redshift)
2. At catalog initialization, the CDK's `ColumnNameResolver` calls `toColumnName()` for every input column, handles collision resolution (duplicate names after transformation), and stores the result in `ColumnSchema.inputToFinalColumnNames`
3. In `DestinationWriter.createStreamLoader()`, the connector wraps the pre-computed mapping: `ColumnNameMapping(stream.tableSchema.columnSchema.inputToFinalColumnNames)`
4. The CDK's `DirectLoadTable*StreamLoader` classes automatically pass the `ColumnNameMapping` to all `TableOperationsClient` and `TableSchemaEvolutionClient` method calls

This means the connector only needs to implement the `toColumnName()` transform -- everything else is handled by the CDK. (Verified in Postgres, Snowflake, and ClickHouse connectors which all follow this pattern.)

---

## Phase 0: Build System Setup

### 0.1 — Convert build configuration to Bulk CDK

**File:** `destination-redshift/build.gradle` -> `destination-redshift/build.gradle.kts`

- Replace the `airbyte-java-connector` plugin with the `airbyte-bulk-connector` plugin
- Set `core = "load"` and `toolkits = listOf("load-csv", "load-aws")`
  - `load-csv` for CSV serialization (used for S3 staging + COPY)
  - `load-aws` for AWS S3 client primitives
- Remove old CDK feature declarations (`db-destinations`, `s3-destinations`, `typing-deduping`)
- Keep existing external dependencies: `redshift-jdbc42`, `aws-java-sdk-s3`, `commons-csv`, `s3-stream-upload`
- Add HikariCP dependency (for connection pooling, like Postgres does)
- Optionally keep `airbyte-cdk-core` dependency for `JdbcUtils.parseJdbcParameters()` (like Postgres does) or inline the logic

**File:** `destination-redshift/gradle.properties`

- Add `cdkVersion=1.0.7` (or latest at time of implementation)

**Reference:** Postgres `build.gradle` and `gradle.properties`, Snowflake `build.gradle.kts`

---

## Phase 1: Configuration & Specification Layer (with Backward Compatibility)

### Identified legacy config shapes to support

Existing user configurations (stored in the Airbyte platform database) must continue to work when the connector is upgraded. The new `RedshiftSpecification` Kotlin class must be able to deserialize all historical config JSON shapes:

1. **Full config with `uploading_method`** (most common production shape):
   ```json
   {
     "host": "...", "port": 5439, "username": "...", "password": "...",
     "database": "...", "schema": "public",
     "uploading_method": {
       "method": "S3 Staging",
       "s3_bucket_name": "...", "s3_bucket_region": "us-east-1",
       "access_key_id": "...", "secret_access_key": "..."
     }
   }
   ```

2. **Config without `uploading_method`** (minimal config, used in tests):
   ```json
   {
     "host": "...", "port": 5439, "username": "...", "password": "...",
     "database": "...", "schema": "public"
   }
   ```

3. **Config with extra/unknown fields** (the old spec has `additionalProperties: true`):
   ```json
   {
     "host": "...", "some_future_field": "value"
   }
   ```

4. **Config with `s3_bucket_region` as empty string `""`** (the old spec allows this as a valid/default enum value)

5. **Config with optional fields present**: `jdbc_url_params`, `raw_data_schema`, `disable_type_dedupe`, `drop_cascade`, `purge_staging_data`, `file_name_pattern`, `s3_bucket_path`

### 1.1 — Create `RedshiftSpecification.kt`

New file implementing `ConfigurationSpecification` (replaces the static `spec.json` approach).

- Define all config fields with Jackson annotations: `host`, `port`, `username`, `password`, `database`, `schema`, `jdbc_url_params`, `raw_data_schema`, `disable_type_dedupe`, `drop_cascade`
- Define S3 staging config as a nested object: `s3_bucket_name`, `s3_bucket_path`, `s3_bucket_region`, `access_key_id`, `secret_access_key`, `purge_staging_data`
- Implement `DestinationSpecificationExtension` declaring supported sync modes: `APPEND`, `OVERWRITE`, `APPEND_DEDUP`
- Handle SSH tunnel spec injection (look at how Snowflake's `SnowflakeSpecification.kt` does this)
- Mark `uploading_method` as nullable (`@JsonProperty("uploading_method") val uploadingMethod: S3StagingConfig? = null`)
- Use `@JsonIgnoreProperties(ignoreUnknown = true)` on the spec class to handle `additionalProperties: true`
- For `s3_bucket_region`, accept both empty string and valid region strings (use a custom deserializer or post-processing in the config factory)
- All optional fields should have sensible defaults

**Reference:** `SnowflakeSpecification.kt`, `PostgresSpecification.kt`

### 1.2 — Create `RedshiftMigratingConfigurationSpecificationSupplier.kt`

Following the Snowflake pattern:
- Use `@Singleton @Replaces(ConfigurationSpecificationSupplier::class)` to intercept raw JSON before parsing
- Inject `@Value("${airbyte.connector.config.json}")` to get the raw config string
- Apply migration transformations on the raw JSON string before parsing:
  - If `uploading_method` is absent, either inject a default or ensure `RedshiftSpecification` treats it as nullable
  - If `s3_bucket_region` is `""`, normalize it to a valid default (e.g., `"us-east-1"` or handle in the specification as nullable)
  - If any future structural changes are needed (e.g., renaming fields), handle them here
- Use `ValidatedJsonUtils.parseUnvalidated()` (NOT `parseOne`) to be forgiving of edge cases
- If config is invalid JSON, throw `ConfigErrorException`

**Reference:** `SnowflakeMigratingConfigurationSpecificationSupplier.kt`

### 1.3 — Create `RedshiftConfigurationSupplierSpecificationFactory.kt`

Following the Snowflake pattern:
- Use `@Singleton @Replaces(ConfigurationSupplierSpecificationFactory::class)`
- Wire the migrating supplier + `SpecificationExtender` to produce the `ConnectorSpecification` for the `spec` operation

**Reference:** `SnowflakeConfigurationSupplierSpecificationFactory.kt`

### 1.4 — Create `RedshiftConfiguration.kt`

New file extending `DestinationConfiguration`.

- Parse the specification into a typed config object
- Expose computed properties: JDBC URL, S3 config, `legacyRawTablesOnly`, `dropCascade`, internal namespace
- Create `RedshiftConfigurationFactory` implementing `DestinationConfigurationFactory<RedshiftSpecification, RedshiftConfiguration>`

**Reference:** `PostgresConfiguration.kt`, `SnowflakeConfiguration.kt`

### 1.5 — Create backward compatibility tests

Create `RedshiftMigratingConfigurationSpecificationSupplierTest.kt` with:
- Test parsing a full production config (with `uploading_method`)
- Test parsing a minimal config (without `uploading_method`)
- Test parsing a config with extra unknown fields
- Test parsing a config with empty `s3_bucket_region`
- Test parsing a config with all optional fields present
- Test parsing invalid JSON -> `ConfigErrorException`
- Test both pretty-printed and minified JSON (like Snowflake does)
- Use real example config fixtures as JSON files in `src/test/resources/`

This ensures that **before any other code is written**, we have confidence that the new specification layer can ingest every possible existing config format.

### 1.6 — Create `RedshiftBeanFactory.kt`

Micronaut `@Factory` class that wires all beans together:

- Create a JDBC `DataSource` bean (HikariCP with Redshift JDBC driver) supporting both direct and SSH-tunneled connections
- Create `RedshiftConfiguration` bean from the specification
- Create `AggregatePublishingConfig` bean (tune batch sizes for Redshift - likely similar to Snowflake's 350MB)
- Create `TempTableNameGenerator` bean (using `DefaultTempTableNameGenerator`)
- Handle "spec-only" mode where no database connection is needed (dummy DataSource)

**Reference:** `PostgresBeanFactory.kt`, `SnowflakeBeanFactory.kt`

---

## Phase 2: Schema & Type Mapping Layer

### 2.1 — Create `RedshiftTableSchemaMapper.kt`

Implement `TableSchemaMapper` interface. The CDK will automatically call these methods during catalog initialization and handle all column name mapping, collision resolution, and schema construction.

Methods to implement:

- **`toFinalTableName()`**: Map stream descriptor to Redshift table name (lowercase, sanitized). In legacy raw mode, use `TypingDedupingUtil.concatenateRawTableName()` and place in internal schema (same pattern as Postgres).
- **`toTempTableName()`**: Delegate to `TempTableNameGenerator.generate()`.
- **`toColumnName(name)`**: Call `name.toRedshiftCompatibleName()`. In legacy raw mode, return name unchanged. **This is all the connector needs to do for column mapping** -- the CDK's `ColumnNameResolver` handles collision resolution and the CDK's stream loaders handle passing the mapping to `TableOperationsClient` methods.
- **`toColumnType(fieldType)`**: Map Airbyte types to Redshift types:

| Airbyte Type | Redshift Type |
|---|---|
| Boolean | `BOOLEAN` |
| Integer | `BIGINT` |
| Number | `FLOAT8` |
| String | `VARCHAR(65535)` (max Redshift VARCHAR) |
| Date | `DATE` |
| TimeWithTimezone | `TIMETZ` |
| TimeWithoutTimezone | `TIME` |
| TimestampWithTimezone | `TIMESTAMPTZ` |
| TimestampWithoutTimezone | `TIMESTAMP` |
| Object | `SUPER` |
| Array | `SUPER` |
| Union/Unknown | `SUPER` |

- **`toFinalSchema()`**: In normal mode, return schema unchanged. In legacy raw mode, replace entire schema with `{_airbyte_data -> SUPER}` (same pattern as Postgres using JSONB).
- **`colsConflict()`**: Case-insensitive comparison (Redshift default).

**Reference:** `PostgresTableSchemaMapper.kt` (primary -- nearly identical pattern), `SnowflakeTableSchemaMapper.kt`

### 2.2 — Create `RedshiftNamingUtils.kt`

Utility `String.toRedshiftCompatibleName()` extension function:
1. Call `Transformations.toAlphanumericAndUnderscore()` from the CDK (handles Unicode normalization, whitespace, special chars)
2. Force lowercase (Redshift convention)
3. Prepend `_` if starts with a digit
4. Generate fallback name for empty strings
5. Truncate to 127 characters (Redshift's identifier limit) with hash suffix to avoid collisions

**Reference:** `PostgresNamingUtils.kt` (primary -- same pattern, just different max length), existing `RedshiftSQLNameTransformer.kt`

### 2.3 — Create `RedshiftColumnManager.kt`

Define meta columns for Redshift tables:
- **Schema mode:** `_airbyte_raw_id` VARCHAR(36) NOT NULL, `_airbyte_extracted_at` TIMESTAMPTZ NOT NULL, `_airbyte_meta` SUPER NOT NULL, `_airbyte_generation_id` BIGINT
- **Raw mode:** Same plus `_airbyte_loaded_at` TIMESTAMPTZ (nullable) and `_airbyte_data` SUPER

**Reference:** `PostgresColumnManager.kt` (primary)

---

## Phase 3: SQL Generation Layer

### 3.1 — Create `RedshiftDirectLoadSqlGenerator.kt`

Connector-specific `@Singleton` class (NOT a CDK interface -- the SQL generator is a plain connector class, same as Postgres). Modeled closely after `PostgresDirectLoadSqlGenerator.kt` with Redshift-specific adaptations.

Key methods:

- **`createTable()`**: Generate `CREATE TABLE IF NOT EXISTS` DDL with meta columns + user columns from stream's `tableSchema.columnSchema.finalSchema`. Support `replace` flag via `DROP IF EXISTS` + `CREATE`. **No index creation** -- Redshift uses sort keys and distribution keys instead of traditional indexes. Consider adding sort keys on PKs/cursor columns.

- **`upsertTable()`**: Use the **CTE-based DELETE + UPDATE + INSERT pattern** (same as Postgres `PostgresDirectLoadSqlGenerator.upsertTable()`):

  ```sql
  WITH deduped_source AS (
    -- Deduplicate source (temp) table using ROW_NUMBER()
    SELECT <all_columns>
    FROM (
      SELECT *,
        ROW_NUMBER() OVER (
          PARTITION BY <pks>
          ORDER BY <cursor> DESC NULLS LAST, "_airbyte_extracted_at" DESC
        ) AS row_number
      FROM "schema"."temp_table"
    ) AS deduplicated
    WHERE row_number = 1
  ),

  -- CDC hard delete (if enabled): delete matching rows where _ab_cdc_deleted_at IS NOT NULL
  deleted AS (
    DELETE FROM "schema"."final_table"
    USING deduped_source
    WHERE <pk_match> AND deduped_source."_ab_cdc_deleted_at" IS NOT NULL
      AND (<cursor_comparison>)
  ),

  -- Update existing rows where source is newer
  updates AS (
    UPDATE "schema"."final_table"
    SET <col = deduped_source.col, ...>
    FROM deduped_source
    WHERE <pk_match>
      AND (<cursor_comparison>)
      [AND deduped_source."_ab_cdc_deleted_at" IS NULL -- if CDC hard delete]
  )

  -- Insert rows that don't exist in target
  INSERT INTO "schema"."final_table" (<columns>)
  SELECT <columns> FROM deduped_source
  WHERE NOT EXISTS (
    SELECT 1 FROM "schema"."final_table" WHERE <pk_match>
  )
  [AND deduped_source."_ab_cdc_deleted_at" IS NULL -- if CDC hard delete]
  ```

  This pattern works in Redshift because CTEs with DML (DELETE, UPDATE in WITH clause) are supported. It is the same pattern proven in Postgres.

  The cursor comparison logic (4-way with NULL handling):
  ```sql
  target.cursor < source.cursor
  OR (target.cursor = source.cursor AND target._airbyte_extracted_at < source._airbyte_extracted_at)
  OR (target.cursor IS NULL AND source.cursor IS NOT NULL)
  OR (target.cursor IS NULL AND source.cursor IS NULL AND target._airbyte_extracted_at < source._airbyte_extracted_at)
  ```

- **`overwriteTable()`**: Rename-based swap within a transaction (same as Postgres):
  ```sql
  BEGIN TRANSACTION;
  DROP TABLE IF EXISTS "schema"."target" [CASCADE];
  ALTER TABLE "schema"."source" RENAME TO "target";
  [ALTER TABLE "source_schema"."target" SET SCHEMA "target_schema";] -- if cross-schema
  COMMIT;
  ```

- **`copyTable()`**: `INSERT INTO target (cols) SELECT cols FROM source`

- **`matchSchemas()`** (schema evolution): Generate `ALTER TABLE ADD/DROP/ALTER COLUMN` statements. **Key Redshift difference from Postgres:** Redshift does NOT support `ALTER COLUMN ... TYPE ... USING` for type changes. Instead, use the 5-step rename pattern from Snowflake:
  1. `ALTER TABLE ADD COLUMN temp_col new_type`
  2. `UPDATE table SET temp_col = CAST(old_col AS new_type)` (or use Redshift-specific cast expressions)
  3. `ALTER TABLE DROP COLUMN old_col`
  4. `ALTER TABLE RENAME COLUMN temp_col TO old_col`

  For SUPER <-> VARCHAR conversions, use `JSON_SERIALIZE()` / `JSON_PARSE()` instead of simple CAST.

- **`dropTable()`**: `DROP TABLE IF EXISTS` (with optional `CASCADE` per config)

- **`countTable()`**, **`createNamespace()`**, **`getGenerationId()`**, **`getTableSchema()`**: Standard SQL queries (nearly identical to Postgres)

- **`copyFromS3()`**: Generate the Redshift COPY command for S3 staging (Redshift-specific, not in Postgres):
  ```sql
  COPY "schema"."table" FROM 's3://bucket/path/manifest'
  CREDENTIALS 'aws_access_key_id=...;aws_secret_access_key=...'
  CSV GZIP
  REGION 'us-east-1'
  TIMEFORMAT 'auto'
  STATUPDATE OFF
  MANIFEST;
  ```

**Reference:** `PostgresDirectLoadSqlGenerator.kt` (primary -- follow the same architecture), `SnowflakeDirectLoadSqlGenerator.kt` (for type change ALTER TABLE pattern), existing `RedshiftSqlGenerator.kt` (for Redshift-specific SQL knowledge)

### 3.2 — Create `RedshiftDataType.kt`

Enum of Redshift SQL type strings, same pattern as `PostgresDataType.kt`:

```kotlin
enum class RedshiftDataType(val typeName: String) {
    BIGINT("bigint"),
    FLOAT8("float8"),
    BOOLEAN("boolean"),
    VARCHAR("varchar(65535)"),
    DATE("date"),
    TIME("time"),
    TIMETZ("timetz"),
    TIMESTAMP("timestamp"),
    TIMESTAMPTZ("timestamptz"),
    SUPER("super"),
}
```

**Reference:** `PostgresDataType.kt`

### 3.3 — Create `RedshiftSqlEscapeUtils.kt`

SQL string escaping utilities for Redshift (single-quote escaping, identifier quoting via `"identifier"`).

**Reference:** `PostgresDirectLoadSqlGenerator.quoteIdentifier()` (can be a companion function)

---

## Phase 4: Client & Data Access Layer

### 4.1 — Create `RedshiftAirbyteClient.kt`

Implement both `TableOperationsClient` and `TableSchemaEvolutionClient`, following the Postgres pattern closely:

**`TableOperationsClient` methods:**
- **`createNamespace()`**: `CREATE SCHEMA IF NOT EXISTS` with retry logic (port the existing retry logic from `RedshiftDestinationHandler.createNamespaces()` -- handles transient errors when schemas are deleted concurrently)
- **`createTable(stream, tableName, columnNameMapping, replace)`**: Delegate to `RedshiftDirectLoadSqlGenerator.createTable()`. The `columnNameMapping` is received from the CDK stream loader and does not need manual construction.
- **`dropTable()`**: Delegate to SQL generator, handle CASCADE config
- **`overwriteTable(source, target)`**: Delegate to SQL generator's rename-based swap
- **`copyTable(columnNameMapping, source, target)`**: Delegate to SQL generator. The `columnNameMapping` tells us which columns to include.
- **`upsertTable(stream, columnNameMapping, source, target)`**: Delegate to SQL generator's CTE-based DELETE+UPDATE+INSERT pattern. The `columnNameMapping` is used to determine column names in the generated SQL.
- **`tableExists()`**: Query `information_schema.tables`
- **`namespaceExists()`**: Query `pg_namespace` or `information_schema.schemata`
- **`countTable()`**: `SELECT COUNT(*) FROM ...`
- **`getGenerationId()`**: `SELECT _airbyte_generation_id FROM ... LIMIT 1`

**`TableSchemaEvolutionClient` methods:**
- **`discoverSchema()`**: Query `information_schema.columns` for column names, types, nullability
- **`computeSchema(stream, columnNameMapping)`**: Derive expected schema from `stream.tableSchema.columnSchema.finalSchema` using the `columnNameMapping` (same pattern as Postgres)
- **`applyChangeset()`**: Delegate to SQL generator's `matchSchemas()`
- Optionally override `ensureSchemaMatches()` if Redshift needs custom schema comparison logic (e.g., for sort key/PK index changes like Postgres does)

**Redshift-specific concerns:**
- SQL execution: Wrap with `SET enable_case_sensitive_identifier to TRUE` (required for Redshift SUPER column JSON path access)
- Error handling: Catch "cannot drop table because other objects depend on it" -> `ConfigErrorException` with `drop_cascade` hint (port from existing `RedshiftDestinationHandler`)

**Reference:** `PostgresAirbyteClient.kt` (primary -- follow the same structure), existing `RedshiftDestinationHandler.kt` (for Redshift-specific error handling and retry logic)

---

## Phase 5: Data Loading Layer (S3 Staging + COPY)

### 5.1 — Create `RedshiftAggregate.kt` and `RedshiftAggregateFactory.kt`

Implement `Aggregate` and `AggregateFactory`, same pattern as Postgres:

- `RedshiftAggregateFactory` creates a `RedshiftAggregate` per stream store key
- `RedshiftAggregate.accept()` writes records to a `RedshiftInsertBuffer`
- `RedshiftAggregate.flush()` triggers the S3 upload + COPY INTO

**Reference:** `PostgresAggregate.kt` and `PostgresAggregateFactory.kt` (primary)

### 5.2 — Create `RedshiftInsertBuffer.kt`

The core data loading mechanism. Unlike Postgres (which uses `COPY FROM STDIN`), Redshift loads via S3 staging:

1. Format records as CSV (GZIP-compressed) using the `load-csv` toolkit
2. Upload CSV file to S3 staging bucket
3. Build a Redshift COPY manifest (JSON file listing S3 URLs)
4. Upload manifest to S3
5. Execute Redshift COPY command via SQL generator's `copyFromS3()`
6. Clean up staging files (if `purge_staging_data` is true)

**For schema mode:** Format each column value according to its typed representation (one CSV column per schema field), matching the column order of the table DDL. Use `RedshiftSchemaRecordFormatter`.

**For legacy raw mode:** Format as: `_airbyte_raw_id`, `_airbyte_extracted_at`, `_airbyte_loaded_at`, `_airbyte_data` (JSON string), `_airbyte_meta` (JSON string), `_airbyte_generation_id`. Use `RedshiftRawRecordFormatter`.

Port the manifest logic from existing `Manifest.kt` / `Entry.kt`.

**Reference:** `PostgresInsertBuffer.kt` (for record formatting structure), `SnowflakeInsertBuffer.kt` (for S3 staging pattern), existing `RedshiftStagingStorageOperation.kt` (for S3 + COPY specifics)

### 5.3 — Create `RedshiftRecordFormatter.kt`

Two implementations, same pattern as Postgres:
- **`RedshiftSchemaRecordFormatter`**: Maps typed column values to CSV in column order (meta columns first, then user columns)
- **`RedshiftRawRecordFormatter`**: Serializes non-meta columns as JSON into `_airbyte_data` SUPER column, outputs meta columns individually

**Reference:** `PostgresRecordFormatter.kt` (primary)

---

## Phase 6: Value Coercion Layer

### 6.1 — Create `RedshiftValueCoercer.kt`

Implement `ValueCoercer` to handle Redshift-specific size and type limitations. Follow the Postgres `ValueCoercer` pattern with Redshift-specific limits:

- **`map()`**:
  - Union/Unknown types: serialize to JSON string in schema mode

- **`validate()`**:
  - **VARCHAR limit**: Redshift VARCHAR max is 65,535 bytes. Nullify strings exceeding this with `DESTINATION_FIELD_SIZE_LIMITATION`.
  - **SUPER value limit**: 16 MB per SUPER value. For Object/Array columns, check serialized JSON size and nullify if over 16MB.
  - **Integer range**: Validate against `BIGINT` range (int64) -- same as Postgres.
  - **Number range**: Validate against `FLOAT8` range -- same as Postgres.
  - **String sanitization**: Strip `\u0000` null bytes (Redshift, like Postgres, rejects them).
  - **Date/Timestamp range**: Validate against Redshift's supported ranges.

This replaces the current `RedshiftSuperLimitationTransformer` but is now integrated as a CDK `ValueCoercer`.

**Reference:** `PostgresValueCoercer.kt` (primary -- same pattern), existing `RedshiftSuperLimitationTransformer.kt` (for Redshift-specific limits)

---

## Phase 7: Writer & Stream Loader Orchestration

### 7.1 — Create `RedshiftWriter.kt`

Implement `DestinationWriter`, same pattern as Postgres:

- **`setup()`**: Create namespaces for all streams, gather initial table statuses
- **`createStreamLoader()`**: 
  1. Extract `ColumnNameMapping` from the stream: `ColumnNameMapping(stream.tableSchema.columnSchema.inputToFinalColumnNames)` -- the mapping was auto-generated by the CDK during catalog initialization
  2. Select the appropriate CDK-provided stream loader based on sync mode and generation ID:

| Condition | Stream Loader |
|---|---|
| Append + `minGenId == 0` | `DirectLoadTableAppendStreamLoader` |
| Append + `minGenId == genId` | `DirectLoadTableAppendTruncateStreamLoader` |
| Dedupe + `minGenId == 0` | `DirectLoadTableDedupStreamLoader` |
| Dedupe + `minGenId == genId` | `DirectLoadTableDedupTruncateStreamLoader` |
| Legacy raw mode + Dedupe | Fall back to Append loader (like Snowflake/Postgres) |
| Other | Error ("hybrid refresh not supported") |

  3. Pass `columnNameMapping`, `redshiftClient` (as both `tableOperationsClient` and `schemaEvolutionClient`), and `streamStateStore` to the CDK stream loader constructor. The CDK handles all table lifecycle operations from there.

- **`teardown()`**: Clean up resources (close DataSource, etc.)

**Reference:** `PostgresWriter.kt` (primary -- nearly identical pattern), `SnowflakeWriter.kt`

### 7.2 — Create `RedshiftInitialStatusGatherer.kt`

Extend `BaseDirectLoadInitialStatusGatherer`:
- Override if needed for Redshift-specific table status queries
- Check real table and temp table existence and emptiness

**Reference:** `PostgresDirectLoadDatabaseInitialStatusGatherer.kt` (primary)

---

## Phase 8: Connection Check

### 8.1 — Create `RedshiftChecker.kt`

Implement `DestinationChecker`:

- Create a test schema/table
- Write a test row via the S3 staging + COPY mechanism (validates both S3 and Redshift access)
- Verify the row was written
- Clean up (drop test table)
- Validate S3 bucket access (write + delete test object)

Port the connection validation logic from the existing `RedshiftDestination.check()` method.

**Reference:** `PostgresOssChecker.kt` (for structure), existing `RedshiftDestination.kt` check logic (for S3 validation)

---

## Phase 9: Entry Point

### 9.1 — Create `RedshiftDestination.kt` (rewrite)

Minimal Micronaut-based entry point:

```kotlin
fun main(args: Array<String>) {
    AirbyteDestinationRunner.run(*args)
}
```

The entire connector is wired via Micronaut DI through `@Singleton` beans.

**Reference:** `PostgresDestinationV2.kt`, `SnowflakeDestination.kt`

---

## Phase 10: Tests

The Bulk CDK provides a standardized component test framework via suite interfaces that every connector should implement. These are the primary quality gates and should be prioritized. The test structure follows a three-tier architecture: component tests (CDK suites against a real DB), unit tests (mocked), and acceptance tests (full E2E).

### 10.1 — Component tests (CDK suite interfaces)

These tests run against a real Redshift instance using Micronaut DI with `@MicronautTest(environments = ["component"])`. They exercise the connector's production beans in isolation against the actual database. Since Redshift is a managed service (no Testcontainers available), they connect to a dedicated test Redshift cluster via secrets.

**Infrastructure files to create (under `src/test-integration/.../component/`):**

- **`RedshiftComponentTestConfigFactory.kt`** — A Micronaut `@Factory` annotated with `@Requires(env = ["component"])`. Loads Redshift connection config from a secrets file (`secrets/test-instance.json` fetched from GSM via `TestConfigLoader.loadTestConfig()`). Creates a `RedshiftConfiguration` bean for the test environment, including S3 staging credentials.

  **Reference:** `PostgresComponentTestConfigFactory.kt`, `SnowflakeTestConfigFactory.kt`

- **`RedshiftTestTableOperationsClient.kt`** — Implements the CDK's `TestTableOperationsClient` interface (`@Singleton`, `@Requires(env = ["component"])`). Provides low-level JDBC operations for test setup/verification:
  - `ping()` — simple connectivity check (`SELECT 1`)
  - `dropNamespace(namespace)` — `DROP SCHEMA IF EXISTS ... CASCADE`
  - `insertRecords(table, records)` — direct JDBC INSERT for test data. Must handle Redshift SUPER type serialization: convert `ObjectValue`/`ArrayValue` to JSON strings via `JSON_PARSE()`.
  - `readTable(table)` — `SELECT * FROM ...` returning `List<Map<String, Any>>` with proper type conversion (SUPER -> JSON string, TIMESTAMPTZ -> OffsetDateTime, etc.)

  **Reference:** `PostgresTestTableOperationsClient.kt`, `SnowflakeTestTableOperationsClient.kt`

- **`RedshiftComponentTestFixtures.kt`** — Redshift-specific test fixtures:
  - `airbyteMetaColumnMapping` — identity mapping for `_airbyte_raw_id`, `_airbyte_extracted_at`, `_airbyte_meta`, `_airbyte_generation_id` (Redshift preserves lowercase column names when quoted)
  - `testMapping`, `idAndTestMapping`, `idTestWithCdcMapping` — Redshift-compatible versions of the CDK standard test column mappings
  - `allTypesTableSchema` — maps all CDK data types to Redshift column types (`IntegerType -> bigint`, `NumberType -> float8`, `StringType -> varchar(65535)`, `ObjectType -> super`, `ArrayType -> super`, `UnionType -> super`, etc.)

  **Reference:** `PostgresComponentTestFixtures.kt`, `SnowflakeComponentTestFixtures.kt`

**CDK suite implementations to create:**

- **`RedshiftTableOperationsTest.kt`** — Implements `TableOperationsSuite`. Injects `client: TableOperationsClient`, `testClient: TestTableOperationsClient`, `schemaFactory: TableSchemaFactory`. Tests:
  - `connect to database` — basic connectivity ping
  - `create and drop namespaces` — schema lifecycle
  - `create and drop tables` — table lifecycle
  - `insert records` — insert via S3 staging + COPY, verify data
  - `count table rows` — incremental insert + count verification
  - `get generation id` — insert record with generation_id, read back
  - `overwrite tables` — rename-based swap, verify source dropped
  - `copy tables` — INSERT INTO ... SELECT, verify combined records
  - `upsert tables` — CTE-based DELETE+UPDATE+INSERT with CDC, cursor-based conflict resolution

  Each test delegates to `super.<method>(redshiftSpecificMapping)`.

  **Reference:** `PostgresTableOperationsTest.kt`

- **`RedshiftTableSchemaEvolutionTest.kt`** — Implements `TableSchemaEvolutionSuite`. Injects `client: TableSchemaEvolutionClient`, `opsClient: TableOperationsClient`, `testClient: TestTableOperationsClient`, `schemaFactory: TableSchemaFactory`. Tests:
  - `discover recognizes all data types` — create table with all Redshift types, discover schema, assert match
  - `computeSchema handles all data types` — compute expected schema from stream definition
  - `noop diff` — no-change detection
  - `changeset is correct when adding a column` — detect column addition
  - `changeset is correct when dropping a column` — detect column removal
  - `changeset is correct when changing a column's type` — detect type change
  - `apply changeset - handle sync mode append/dedup` — apply schema evolution across all sync mode transitions (append->append, append->dedup, dedup->append, dedup->dedup)
  - `change from string type to unknown type` — string -> unknown column evolution
  - `change from unknown type to string type` — unknown -> string column evolution

  **Critical:** The `apply changeset` tests for type changes are especially important since Redshift uses the 5-step rename pattern (not Postgres's `ALTER COLUMN TYPE ... USING`). These tests validate that the pattern works correctly with data preservation.

  **Reference:** `PostgresTableSchemaEvolutionTest.kt`, `SnowflakeTableSchemaEvolutionTest.kt`

- **`RedshiftDataCoercionTest.kt`** — Implements `DataCoercionSuite`. Uses `@ParameterizedTest` with `@MethodSource` pointing at CDK fixture classes. Injects `coercer: ValueCoercer`, `opsClient: TableOperationsClient`, `testClient: TestTableOperationsClient`, `schemaFactory: TableSchemaFactory`. Tests value coercion roundtrip (coerce -> insert -> read -> verify) for:
  - `handle integer values` — BIGINT range validation
  - `handle number values` — FLOAT8 range validation
  - `handle timestamptz values` — TIMESTAMPTZ range and precision
  - `handle timestampntz values` — TIMESTAMP range and precision
  - `handle timetz values` — TIMETZ handling
  - `handle timentz values` — TIME handling
  - `handle date values` — DATE range validation
  - `handle bool values` — BOOLEAN roundtrip
  - `handle string values` — VARCHAR(65535) limit, null byte stripping
  - `handle object values` — SUPER type for JSON objects (16MB limit)
  - `handle empty/schemaless object values` — SUPER for untyped objects
  - `handle array values` — SUPER for JSON arrays
  - `handle schemaless array values` — SUPER for untyped arrays
  - `handle union values` — SUPER for union types
  - `handle legacy union values` — legacy union handling
  - `handle unknown values` — SUPER for unknown types

  Must customize CDK fixtures for Redshift-specific behaviors: SUPER type JSON serialization format, VARCHAR size limits, numeric precision, timestamp ranges.

  **Reference:** `SnowflakeDataCoercionTest.kt`, `ClickhouseDataCoercionTest.kt`

- **`RedshiftSchemaMapperTest.kt`** — Implements `SchemaMapperSuite`. Injects `tableSchemaMapper: TableSchemaMapper`, `schemaFactory: TableSchemaFactory`, `opsClient: TableOperationsClient`, `streamFactory: DestinationStreamFactory`, `tableNameResolver: TableNameResolver`, `namespaceMapper: NamespaceMapper`. Tests:
  - `simple table name` — basic namespace/table mapping
  - `funky chars in table name` — special characters sanitization
  - `table name starts with non-letter character` — digit prefix handling
  - `table name is reserved keyword` — reserved word handling
  - `simple temp table name` — temp table generation
  - `simple column name` — basic column mapping
  - `column name with funky chars` — special character sanitization in columns
  - `column name starts with non-letter character` — digit prefix in columns
  - `column name is reserved keyword` — reserved word in columns
  - `stream names avoid collisions` — two streams mapping to same table name
  - `column names avoid collisions` — two columns mapping to same column name
  - `column types support all airbyte types` — all type mappings + table creation validation

  **Reference:** `ClickhouseSchemaMapperTest.kt`

### 10.2 — Unit tests (mocked, no DB needed)

Under `src/test/`:

- **`RedshiftDirectLoadSqlGeneratorTest.kt`**: Verify generated SQL strings for CREATE TABLE, upsert (CTE-based DELETE+UPDATE+INSERT), ALTER TABLE (5-step type change pattern), overwrite (rename-based swap), copy, drop, count, COPY FROM S3.
- **`RedshiftValueCoercerTest.kt`**: Test VARCHAR 64KB limit, SUPER 16MB limit, BIGINT range, FLOAT8 range, date/timestamp ranges, null byte stripping, union/unknown serialization.
- **`RedshiftAirbyteClientTest.kt`**: Test client logic with mocked DataSource/JDBC. Verify SQL delegation to generator, error handling (CASCADE hint), retry logic for namespace creation.
- **`RedshiftWriterTest.kt`**: Test stream loader selection logic for each sync mode + generation ID combination. Verify `ColumnNameMapping` is correctly extracted from stream schema.
- **`RedshiftCheckerTest.kt`**: Test check logic with mocked dependencies.
- **`RedshiftAggregateFactoryTest.kt`**: Test aggregate creation and buffer selection (schema vs raw mode).
- **`RedshiftInsertBufferTest.kt`**: Test CSV formatting, S3 upload sequencing, manifest generation.
- **`RedshiftRecordFormatterTest.kt`**: Test schema and raw record formatting (CSV column ordering, SUPER serialization).

### 10.3 — Acceptance tests (full E2E via CDK runner)

Under `src/test-integration/`:

- **`RedshiftAcceptanceTest.kt`** — Extends `BasicFunctionalityIntegrationTest`. Full end-to-end test running the connector as a process. Create concrete subclasses for different configurations:
  - `RedshiftS3StagingAcceptanceTest` — standard S3 staging mode with typed tables
  - `RedshiftRawAcceptanceTest` — legacy raw tables mode (`disable_type_dedupe=true`)

  Supporting utility classes:
  - **`RedshiftDataDumper.kt`** — implements `DestinationDataDumper`, reads typed records from Redshift for verification
  - **`RedshiftRawDataDumper.kt`** — reads raw mode records (SUPER `_airbyte_data` column)
  - **`RedshiftExpectedRecordMapper.kt`** — implements `ExpectedRecordMapper`, normalizes expected records for Redshift behaviors (SUPER JSON format, timestamp precision, etc.)
  - **`RedshiftDataCleaner.kt`** — implements `DestinationCleaner`, cleans up test schemas/tables

  **Reference:** `PostgresAcceptanceTest.kt`, `SnowflakeAcceptanceTest.kt`

- **`RedshiftCheckTest.kt`** — Extends `CheckIntegrationTest<RedshiftSpecification>`. Tests connection check with valid credentials, invalid credentials, invalid S3 bucket, etc.

  **Reference:** `PostgresCheckTest.kt`, `SnowflakeCheckTest.kt`

- **`RedshiftSpecTest.kt`** — Extends `SpecTest`. Validates the generated connector spec against expected JSON files.

  **Test resources:**
  - `src/test-integration/resources/expected-spec-oss.json` — expected spec output

  **Reference:** `PostgresSpecTest.kt`, `SnowflakeSpecTest.kt`

### 10.4 — Drop obsolete tests

- Remove V1->V2 migration tests (migration dropped)
- Remove tests for old CDK classes that no longer exist
- Remove old `AbstractRedshiftTypingDedupingTest` (replaced by CDK acceptance tests)
- Remove old `RedshiftSqlGeneratorIntegrationTest` (replaced by component tests)

### 10.5 — Test secrets and metadata

Update `metadata.yaml` to declare test secrets:
```yaml
connectorTestSuitesOptions:
  - suite: unitTests
  - suite: integrationTests
    testSecrets:
      - name: destination_redshift_component_test_instance
        fileName: test-instance.json
        secretStore:
          type: GSM
          alias: airbyte-connector-testing-secret-store
```

The secret should contain Redshift connection details + S3 staging credentials for the test cluster.

### Test file summary

| New Test File | CDK Base | Location |
|---|---|---|
| `RedshiftComponentTestConfigFactory.kt` | -- | `src/test-integration/.../component/` |
| `RedshiftTestTableOperationsClient.kt` | `TestTableOperationsClient` | `src/test-integration/.../component/` |
| `RedshiftComponentTestFixtures.kt` | -- | `src/test-integration/.../component/` |
| `RedshiftTableOperationsTest.kt` | `TableOperationsSuite` | `src/test-integration/.../component/` |
| `RedshiftTableSchemaEvolutionTest.kt` | `TableSchemaEvolutionSuite` | `src/test-integration/.../component/` |
| `RedshiftDataCoercionTest.kt` | `DataCoercionSuite` | `src/test-integration/.../component/` |
| `RedshiftSchemaMapperTest.kt` | `SchemaMapperSuite` | `src/test-integration/.../component/` |
| `RedshiftAcceptanceTest.kt` (+ subclasses) | `BasicFunctionalityIntegrationTest` | `src/test-integration/.../write/` |
| `RedshiftCheckTest.kt` | `CheckIntegrationTest` | `src/test-integration/.../check/` |
| `RedshiftSpecTest.kt` | `SpecTest` | `src/test-integration/.../spec/` |
| `RedshiftDataDumper.kt` | `DestinationDataDumper` | `src/test-integration/.../write/` |
| `RedshiftRawDataDumper.kt` | `DestinationDataDumper` | `src/test-integration/.../write/` |
| `RedshiftExpectedRecordMapper.kt` | `ExpectedRecordMapper` | `src/test-integration/.../write/` |
| `RedshiftDataCleaner.kt` | `DestinationCleaner` | `src/test-integration/.../write/` |
| `RedshiftDirectLoadSqlGeneratorTest.kt` | -- | `src/test/.../sql/` |
| `RedshiftValueCoercerTest.kt` | -- | `src/test/.../write/transform/` |
| `RedshiftAirbyteClientTest.kt` | -- | `src/test/.../client/` |
| `RedshiftWriterTest.kt` | -- | `src/test/.../write/` |
| `RedshiftCheckerTest.kt` | -- | `src/test/.../check/` |
| `RedshiftAggregateFactoryTest.kt` | -- | `src/test/.../dataflow/` |
| `RedshiftInsertBufferTest.kt` | -- | `src/test/.../write/load/` |
| `RedshiftRecordFormatterTest.kt` | -- | `src/test/.../write/load/` |

**References:** Postgres test structure (primary for component tests), Snowflake test structure (for S3/secrets and `DataCoercionSuite` patterns), ClickHouse test structure (for `SchemaMapperSuite`)

---

## Phase 11: Cleanup

### 11.1 — Remove old files

Delete all files that have been fully replaced:
- `RedshiftDestination.kt` (old version)
- `RedshiftSQLNameTransformer.kt`
- `RedshiftStagingStorageOperation.kt`
- `RedshiftSqlGenerator.kt` (old T&D version)
- `RedshiftDestinationHandler.kt`
- `RedshiftState.kt`
- `RedshiftSuperLimitationTransformer.kt`
- `RedshiftDV2Migration.kt`
- `RedshiftRawTableAirbyteMetaMigration.kt`
- `RedshiftGenerationIdMigration.kt`
- `RedshiftGenerationHandler.kt`
- `spec.json` (replaced by `RedshiftSpecification.kt`)

### 11.2 — Update metadata

- Update `metadata.yaml` with new major version (this is a breaking change -> next major)
- Update connector documentation

---

## File Mapping Summary (Old -> New)

| Old File | New File | Notes |
|---|---|---|
| `RedshiftDestination.kt` | `RedshiftDestination.kt` | Complete rewrite (Micronaut entry point) |
| `build.gradle` | `build.gradle.kts` | New Bulk CDK plugin |
| `spec.json` | `RedshiftSpecification.kt` | Config-as-code |
| -- | `RedshiftMigratingConfigurationSpecificationSupplier.kt` | New (config migration) |
| -- | `RedshiftConfigurationSupplierSpecificationFactory.kt` | New (spec factory override) |
| -- | `RedshiftConfiguration.kt` | New |
| -- | `RedshiftBeanFactory.kt` | New (Micronaut DI) |
| `RedshiftSQLNameTransformer.kt` | `RedshiftNamingUtils.kt` | Simplified, uses CDK `Transformations` |
| `RedshiftSqlGenerator.kt` | `RedshiftDirectLoadSqlGenerator.kt` | Complete rewrite, follows Postgres pattern |
| `RedshiftDestinationHandler.kt` | `RedshiftAirbyteClient.kt` | Rewrite to CDK interfaces |
| `RedshiftStagingStorageOperation.kt` | `RedshiftInsertBuffer.kt` + `RedshiftRecordFormatter.kt` | Split into buffer + formatter |
| `RedshiftSuperLimitationTransformer.kt` | `RedshiftValueCoercer.kt` | Rewrite as CDK ValueCoercer |
| -- | `RedshiftTableSchemaMapper.kt` | New (CDK handles column mapping automatically) |
| -- | `RedshiftColumnManager.kt` | New |
| -- | `RedshiftDataType.kt` | New |
| -- | `RedshiftWriter.kt` | New |
| -- | `RedshiftAggregate.kt` + `RedshiftAggregateFactory.kt` | New |
| -- | `RedshiftChecker.kt` | New |
| -- | `RedshiftInitialStatusGatherer.kt` | New |
| `RedshiftState.kt` | -- | Dropped (CDK manages state) |
| `RedshiftDV2Migration.kt` | -- | Dropped |
| `RedshiftRawTableAirbyteMetaMigration.kt` | -- | Dropped |
| `RedshiftGenerationIdMigration.kt` | -- | Dropped (CDK handles generation IDs) |
| `RedshiftGenerationHandler.kt` | -- | Dropped |
| `RedshiftDestinationConstants.kt` | `RedshiftDataType.kt` | Merged |
| `Manifest.kt` / `Entry.kt` | Kept or inlined in `RedshiftInsertBuffer.kt` | S3 COPY manifest model |

---

## Recommended Implementation Order

1. **Phase 0** (Build system) -- Get the project compiling with Bulk CDK
2. **Phase 1** (Config/Spec + backward compatibility tests) -- Can be tested in isolation; safety net for the migration
3. **Phase 2** (Schema mapping) -- Pure logic, easily unit tested
4. **Phase 3** (SQL generation) -- Core complexity, unit test thoroughly
5. **Phase 6** (Value coercer) -- Independent of other phases
6. **Phase 4** (Client) -- Depends on Phases 2-3
7. **Phase 5** (Data loading) -- Depends on Phase 4
8. **Phase 7** (Writer) -- Ties everything together
9. **Phase 8** (Checker) -- Needs the client layer
10. **Phase 9** (Entry point) -- Trivial once everything else works
11. **Phase 10** (Tests) -- Continuously throughout, but full integration tests last
12. **Phase 11** (Cleanup) -- After everything is working

---

## Key Risks & Considerations

1. **S3 staging in Direct Load mode**: The current S3 COPY loads into a raw table with a single SUPER column. In Direct Load mode, the COPY must load into typed columns. This means the CSV format must match the column types exactly, and the COPY command needs appropriate format options. This is the most technically risky area.

2. **Redshift ALTER TABLE limitations**: Unlike Postgres, Redshift does NOT support `ALTER COLUMN ... TYPE ... USING` for inline type conversions. Schema evolution type changes must use the 5-step add/update/drop/rename pattern from Snowflake. This is a key divergence from the Postgres reference.

3. **No traditional indexes in Redshift**: Redshift does not support `CREATE INDEX`. The Postgres pattern of creating PK/cursor/extracted_at indexes cannot be ported. Consider using Redshift sort keys (`SORTKEY`) and distribution keys (`DISTKEY`) instead, though these can only be set at table creation time.

4. **CTE-based DML support**: Verify that Redshift supports the `WITH ... DELETE/UPDATE ... INSERT` CTE pattern used by the Postgres upsert. Redshift's DML-in-CTE support may have limitations.

5. **`ALTER TABLE ... APPEND FROM`**: The current connector uses this Redshift-specific optimization for transferring data between tables. This can't run inside transactions. The CDK's `copyTable()` method uses `INSERT INTO ... SELECT FROM` instead, which is transactional but slower. Evaluate whether this performance trade-off is acceptable.

6. **Breaking change**: This is a major version bump. Users will need to be aware that:
   - Table format changes (raw tables -> typed tables in default mode)
   - Existing raw tables won't be migrated automatically
   - The connector configuration structure may change slightly

7. **Column name mapping is CDK-managed**: The `ColumnNameMapping` is automatically generated by the CDK from `TableSchemaMapper.toColumnName()` and passed to all `TableOperationsClient`/`TableSchemaEvolutionClient` methods by the CDK stream loaders. The connector must NOT try to build or manage its own column mappings -- it should use the `columnNameMapping` parameter received in each method call.
