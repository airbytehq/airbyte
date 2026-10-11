# Dataflow CDK Implementation Reference

**Summary:** Quick reference for implementing destination connectors. Covers the 4 core custom components, type mapping, schema evolution, CDC handling, and integration points. Use as a lookup guide during development.

---

## The 4 Core Custom Components

### 1. SQL Generator

**Purpose:** Generate all database-specific SQL statements

**Key Methods:**

```kotlin
@Singleton
class MySqlGenerator {
    fun createNamespace(namespace: String): String
    fun createTable(stream, tableName, columnMapping, replace): String
    fun dropTable(tableName: TableName): String
    fun copyTable(columnMapping, source, target): String
    fun upsertTable(stream, columnMapping, source, target): String
    fun overwriteTable(source, target): String
    fun alterTable(tableName, added, dropped, modified): Set<String>
    fun countTable(tableName): String
}
```

**Responsibilities:**
- Generate SQL for database dialect
- Handle quoting (quotes, backticks, brackets)
- Generate MERGE/UPSERT for deduplication
- Generate window functions for deduplication
- Handle CDC deletions (DELETE clause in MERGE)
- **Always** call `.andLog()` on generated SQL

**Example:**

```kotlin
fun createTable(stream: DestinationStream, tableName: TableName, ...): String {
    val columnDeclarations = stream.schema.asColumns()
        .map { (name, type) ->
            "${name.quote()} ${columnUtils.toDialectType(type)}"
        }
        .joinToString(",\n")

    return """
        CREATE TABLE ${fullyQualifiedName(tableName)} (
          ${COLUMN_NAME_AB_RAW_ID} VARCHAR NOT NULL,
          ${COLUMN_NAME_AB_EXTRACTED_AT} TIMESTAMP NOT NULL,
          ${COLUMN_NAME_AB_META} JSON NOT NULL,
          ${COLUMN_NAME_AB_GENERATION_ID} INTEGER,
          ${columnDeclarations}
        )
    """.trimIndent().andLog()
}
```

---

### 2. Database Client

**Purpose:** Execute database operations

**Implements:** `TableOperationsClient` + `TableSchemaEvolutionClient`

**TableOperationsClient Methods:**

```kotlin
@Singleton
class MyAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: MySqlGenerator,
) : TableOperationsClient, TableSchemaEvolutionClient {

    // Namespace operations
    suspend fun createNamespace(namespace: String)
    suspend fun namespaceExists(namespace: String): Boolean

    // Table operations
    suspend fun createTable(stream, tableName, columnMapping, replace)
    suspend fun tableExists(table: TableName): Boolean
    suspend fun dropTable(tableName: TableName)
    suspend fun countTable(tableName: TableName): Long?  // null if not exists

    // Finalization operations
    suspend fun overwriteTable(source, target)  // SWAP/RENAME for truncate
    suspend fun copyTable(columnMapping, source, target)  // Copy data
    suspend fun upsertTable(stream, columnMapping, source, target)  // MERGE for dedupe

    // Metadata
    suspend fun getGenerationId(tableName: TableName): Long
}
```

**TableSchemaEvolutionClient Methods:**

```kotlin
// Schema evolution (4 steps)
suspend fun discoverSchema(tableName): TableSchema
fun computeSchema(stream, columnMapping): TableSchema
suspend fun ensureSchemaMatches(stream, tableName, columnMapping)
suspend fun applyChangeset(stream, columnMapping, tableName, expectedColumns, changeset)
```

**Pattern:**

```kotlin
override suspend fun createTable(...) {
    execute(sqlGenerator.createTable(...))
}

override suspend fun upsertTable(...) {
    execute(sqlGenerator.upsertTable(...))
}

private suspend fun execute(sql: String) {
    dataSource.connection.use { conn ->
        conn.createStatement().use { stmt ->
            stmt.executeQuery(sql)
        }
    }
}
```

**Key Responsibilities:**
- Delegate SQL generation to SqlGenerator
- Execute SQL via connection/client
- Handle database errors → ConfigErrorException for user errors
- Implement schema evolution (discover → compute → compare → apply)
- Return `null` for expected missing data (table doesn't exist)

---

### 3. Insert Buffer

**Purpose:** Efficient batch writes to database

**Custom Implementation (database-specific):**

```kotlin
class MyInsertBuffer(
    private val tableName: TableName,
    private val client: MyAirbyteClient,
    private val flushLimit: Int = 1000,
) {
    private val buffer = mutableListOf<Map<String, AirbyteValue>>()
    private var recordCount = 0

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        buffer.add(format(recordFields))
        recordCount++

        if (recordCount >= flushLimit) {
            runBlocking { flush() }
        }
    }

    suspend fun flush() {
        if (buffer.isEmpty()) return

        try {
            // Write batch to database
            writeBatchToDatabase(tableName, buffer)
        } finally {
            buffer.clear()
            recordCount = 0
        }
    }

    private fun format(fields: Map<String, AirbyteValue>): Map<String, Any> {
        // Convert AirbyteValue to database types
    }
}
```

**Database-Specific Strategies:**

| Database | Strategy | Details |
|----------|----------|---------|
| **Snowflake** | CSV staging | CSV → GZIP → stage via PUT → COPY INTO |
| **ClickHouse** | Binary rows | Binary format → in-memory → direct insert |
| **Postgres** | COPY | CSV → temp file → COPY FROM file |
| **BigQuery** | JSON | Batch JSON → streaming insert API |
| **MySQL** | Multi-row INSERT | `INSERT INTO ... VALUES (...), (...), (...)` |

**Key Points:**
- Format records for database (CSV, binary, JSON)
- Buffer in memory or temp files
- Auto-flush at thresholds (count, size, time)
- Clean up resources in `finally`
- **Do NOT** call `upsertTable()` or `overwriteTable()` - StreamLoader does that

---

### 4. Column Utilities

**Purpose:** Type mapping and column declarations

**Key Methods:**

```kotlin
class MyColumnUtils {
    fun toDialectType(type: AirbyteType): String
    fun columnsAndTypes(columns, columnMapping): List<ColumnAndType>
    fun formatColumn(name, type): String
}
```

**Type Mapping:**

| Airbyte Type | Snowflake | ClickHouse | Postgres | BigQuery |
|--------------|-----------|------------|----------|----------|
| `BooleanType` | `BOOLEAN` | `Bool` | `BOOLEAN` | `BOOL` |
| `IntegerType` | `NUMBER(38,0)` | `Int64` | `BIGINT` | `INT64` |
| `NumberType` | `FLOAT` | `Decimal(38,9)` | `DOUBLE PRECISION` | `FLOAT64` |
| `StringType` | `VARCHAR` | `String` | `TEXT` | `STRING` |
| `DateType` | `DATE` | `Date32` | `DATE` | `DATE` |
| `TimestampTypeWithTimezone` | `TIMESTAMP_TZ` | `DateTime64(3)` | `TIMESTAMPTZ` | `TIMESTAMP` |
| `TimestampTypeWithoutTimezone` | `TIMESTAMP_NTZ` | `DateTime64(3)` | `TIMESTAMP` | `DATETIME` |
| `ArrayType` | `ARRAY` | `String` | `JSONB` | `ARRAY` |
| `ObjectType` | `VARIANT` | `String`/`JSON` | `JSONB` | `JSON` |
| `UnionType` | `VARIANT` | `String` | `JSONB` | `JSON` |

**Implementation:**

```kotlin
fun AirbyteType.toDialectType(): String = when (this) {
    BooleanType -> "BOOLEAN"
    IntegerType -> "BIGINT"
    NumberType -> "DECIMAL(38, 9)"
    StringType -> "VARCHAR"
    DateType -> "DATE"
    TimestampTypeWithTimezone -> "TIMESTAMP WITH TIME ZONE"
    TimestampTypeWithoutTimezone -> "TIMESTAMP"
    is ArrayType -> "JSONB"
    is ObjectType -> "JSONB"
    is UnionType -> "JSONB"
    else -> "VARCHAR"  // Fallback
}
```

**Nullable Handling:**

```kotlin
// Snowflake: Add NOT NULL suffix
val typeDecl = if (columnType.nullable) {
    columnType.type  // "VARCHAR"
} else {
    "${columnType.type} NOT NULL"  // "VARCHAR NOT NULL"
}

// ClickHouse: Wrap in Nullable()
val typeDecl = if (columnType.nullable) {
    "Nullable(${columnType.type})"  // "Nullable(String)"
} else {
    columnType.type  // "String"
}
```

---

## Sync Mode Decision Tree

**Selection Logic:**

```kotlin
when (stream.minimumGenerationId) {
    0L -> when (stream.importType) {
        Dedupe -> DirectLoadTableDedupStreamLoader       // Temp → MERGE
        else   -> DirectLoadTableAppendStreamLoader      // Direct write
    }
    stream.generationId -> when (stream.importType) {
        Dedupe -> DirectLoadTableDedupTruncateStreamLoader  // Temp → dedupe → SWAP
        else   -> DirectLoadTableAppendTruncateStreamLoader // Temp → SWAP
    }
}
```

**Temp Table Usage:**

| StreamLoader | Temp Table? | Finalization | When |
|--------------|-------------|--------------|------|
| Append | No | None | Incremental, no PK |
| Dedupe | Yes | MERGE temp→final | Incremental with PK |
| AppendTruncate | Yes | SWAP temp↔final | Full refresh, no PK |
| DedupTruncate | Yes (sometimes 2) | MERGE temp→temp2, SWAP temp2↔final | Full refresh with PK |

**Dedupe+Truncate Complexity:**

When dedupe+truncate and real table doesn't exist or wrong generation:
1. Write to temp1
2. Create temp2
3. MERGE temp1 → temp2 (deduplicate)
4. SWAP temp2 ↔ real (atomic replacement)

Why: Can't MERGE into non-existent table. Can't MERGE then SWAP (two operations, not atomic).

---

## Component Interaction Flow

### Full Sync Lifecycle

```
1. CONFIGURATION
   User Config → ConfigFactory → Configuration
   BeanFactory creates all singletons

2. SETUP (Writer.setup())
   - Create all namespaces
   - Gather initial table state

3. STREAM INIT (per stream)
   Writer.createStreamLoader() → select appropriate StreamLoader

   StreamLoader.start():
     - tableExists(finalTable)
     - If exists: ensureSchemaMatches() [schema evolution]
     - If not: createTable(finalTable)
     - If dedupe/truncate: createTable(tempTable)
     - Store target table in streamStateStore

   AggregateFactory.create():
     - Read tableName from streamStateStore
     - Create InsertBuffer(tableName, client)
     - Wrap in Aggregate

4. DATA PROCESSING (automatic)
   Pipeline → Aggregate.accept(record):
     → InsertBuffer.accumulate(record)
     → [auto-flush at threshold]

   Aggregate.flush():
     → InsertBuffer.flush() → write batch to database

5. FINALIZATION (StreamLoader.close())
   If streamCompleted:
     - Dedupe: upsertTable(temp → final) [MERGE]
     - Truncate: overwriteTable(temp → final) [SWAP]
     - Append: nothing (already in final)
   Always:
     - dropTable(tempTable)
```

### Component Dependencies

```
Writer
  ├─ depends on: client, statusGatherer, names, streamStateStore
  └─ creates: StreamLoaders

StreamLoader (CDK-provided)
  ├─ depends on: client (TableOperationsClient + TableSchemaEvolutionClient)
  └─ calls: createTable(), ensureSchemaMatches(), upsertTable(), dropTable()

AggregateFactory
  ├─ depends on: client, streamStateStore
  └─ creates: Aggregate + InsertBuffer

InsertBuffer
  ├─ depends on: client, columnUtils
  └─ calls: Only insert operations (NOT upsert/merge/swap)

Client
  ├─ depends on: sqlGenerator, dataSource, config
  └─ calls: sqlGenerator for SQL, executes via dataSource

SqlGenerator
  ├─ depends on: columnUtils, config
  └─ called by: client for SQL generation
```

---

## Integration Points

**Where framework calls your code:**

### 1. Setup Phase

```kotlin
// Framework: Writer.setup()
override suspend fun setup() {
    // Your code:
    namespaces.forEach { client.createNamespace(it) }
    initialStatuses = gatherer.gatherInitialStatus(names)
}
```

### 2. Stream Initialization

```kotlin
// Framework: Writer.createStreamLoader(stream)
override fun createStreamLoader(stream: DestinationStream): StreamLoader {
    // Your code:
    return when (stream.minimumGenerationId) {
        0L -> when (stream.importType) {
            is Dedupe -> DirectLoadTableDedupStreamLoader(...)
            else -> DirectLoadTableAppendStreamLoader(...)
        }
        stream.generationId -> /* truncate modes */
    }
}

// Framework: StreamLoader.start() (inside)
if (tableExists(finalTable)) {
    client.ensureSchemaMatches(stream, finalTable, columnMapping)  // Your code
} else {
    client.createTable(stream, finalTable, columnMapping, false)  // Your code
}
```

### 3. Data Processing

```kotlin
// Framework: Aggregate.accept(record)
override fun accept(record: RecordDTO) {
    buffer.accumulate(record.fields)  // Your code (InsertBuffer)
}

// Framework: Aggregate.flush()
override suspend fun flush() {
    buffer.flush()  // Your code (InsertBuffer writes batch)
}
```

### 4. Finalization

```kotlin
// Framework: StreamLoader.close() (inside)
if (streamCompleted) {
    // Dedupe mode
    client.upsertTable(stream, columnMapping, tempTable, finalTable)  // Your code

    // Truncate mode
    client.overwriteTable(tempTable, finalTable)  // Your code
}
client.dropTable(tempTable)  // Your code
```

---

## Schema Evolution

**Automatic during `StreamLoader.start()` if table exists**

### 4-Step Process

**1. Discover Current Schema**

```kotlin
override suspend fun discoverSchema(tableName): TableSchema {
    // Query system catalog: DESCRIBE TABLE, information_schema, etc.
    // Return: Map<columnName, ColumnType(type, nullable)>
    // Filter out Airbyte metadata columns
}
```

**Examples:**
- Snowflake: `DESCRIBE TABLE`
- Postgres: `information_schema.columns`
- ClickHouse: `system.columns`

**2. Compute Expected Schema**

```kotlin
override fun computeSchema(stream, columnMapping): TableSchema {
    // Map stream.schema to database types
    // Use columnUtils.toDialectType()
    // Apply column name mapping
    // Filter out Airbyte metadata columns
}
```

**3. Compare (automatic by CDK)**

```kotlin
val changeset = ColumnChangeset(
    columnsToAdd = expected - actual,
    columnsToDrop = actual - expected,
    columnsToChange = actual.filter { expected[it.key] != it.value },
)
```

**4. Apply Changes**

```kotlin
override suspend fun applyChangeset(..., changeset) {
    changeset.columnsToAdd.forEach { (name, type) ->
        execute("ALTER TABLE $table ADD COLUMN $name $type")
    }
    changeset.columnsToDrop.forEach { (name, _) ->
        execute("ALTER TABLE $table DROP COLUMN $name")
    }
    // Type changes: temp column approach or table recreation
}
```

### Type Change Strategies

**Safe (widening):**
- `INT → BIGINT`: Direct ALTER (larger range)
- `VARCHAR(50) → VARCHAR(100)`: Direct ALTER (longer)
- `NOT NULL → NULL`: Drop constraint

**Unsafe (narrowing):**
- `BIGINT → INT`: Temp column + cast + rename
- `VARCHAR → INT`: Temp column + cast + rename
- `NULL → NOT NULL`: Skip (can't enforce if nulls exist)

**Temp Column Approach (Snowflake):**

```sql
-- 1. Add temp column
ALTER TABLE t ADD COLUMN col_temp VARCHAR;

-- 2. Cast and copy
UPDATE t SET col_temp = CAST(col AS VARCHAR);

-- 3. Rename original to backup
ALTER TABLE t RENAME COLUMN col TO col_backup;

-- 4. Rename temp to original
ALTER TABLE t RENAME COLUMN col_temp TO col;

-- 5. Drop backup
ALTER TABLE t DROP COLUMN col_backup;
```

**Table Recreation (ClickHouse for PK changes):**

```sql
-- 1. Create temp with new schema
CREATE TABLE temp (...) ENGINE = ReplacingMergeTree(...);

-- 2. Copy intersection
INSERT INTO temp SELECT common_columns FROM original;

-- 3. Atomic swap
EXCHANGE TABLES original AND temp;

-- 4. Drop old
DROP TABLE temp;
```

---

## CDC Handling

**CDC = Change Data Capture (source emits deletions)**

### Detection

```kotlin
val hasCdc = stream.schema.asColumns().containsKey(CDC_DELETED_AT_COLUMN)
// CDC_DELETED_AT_COLUMN = "_ab_cdc_deleted_at"
```

### Two Modes

**1. Hard Delete (default)** - Actually delete records

```sql
MERGE INTO target
USING source
ON target.pk = source.pk
WHEN MATCHED AND source._ab_cdc_deleted_at IS NOT NULL
     AND source.cursor > target.cursor THEN DELETE
WHEN MATCHED AND source.cursor > target.cursor THEN UPDATE ...
WHEN NOT MATCHED AND source._ab_cdc_deleted_at IS NULL THEN INSERT ...
```

**2. Soft Delete** - Keep tombstone records

```sql
MERGE INTO target
USING source
ON target.pk = source.pk
-- No DELETE clause
WHEN MATCHED AND source.cursor > target.cursor THEN UPDATE ...
WHEN NOT MATCHED THEN INSERT ...
-- Deleted records upserted with _ab_cdc_deleted_at populated
```

### Implementation

```kotlin
val cdcDeleteClause = if (
    stream.schema.asColumns().containsKey(CDC_DELETED_AT_COLUMN) &&
    config.cdcDeletionMode == CdcDeletionMode.HARD_DELETE
) {
    """
    WHEN MATCHED AND new_record._ab_cdc_deleted_at IS NOT NULL
         AND $cursorComparison THEN DELETE
    """
} else {
    ""
}

val cdcSkipInsertClause = if (hasCdc && isHardDelete) {
    "AND new_record._ab_cdc_deleted_at IS NULL"
} else {
    ""
}

val mergeStatement = """
    MERGE INTO $target
    USING $source
    ON $pkMatch
    $cdcDeleteClause
    WHEN MATCHED AND $cursorComparison THEN UPDATE ...
    WHEN NOT MATCHED $cdcSkipInsertClause THEN INSERT ...
"""
```

**Key Points:**
- Only applies to **Dedupe** mode (not Append)
- DELETE clause must come **before** UPDATE
- Must check cursor (only delete if deletion is newer)
- Skip INSERT for deleted records

**Configuration:**

```kotlin
data class MyConfiguration(
    val cdcDeletionMode: CdcDeletionMode = CdcDeletionMode.HARD_DELETE,
)

enum class CdcDeletionMode(@get:JsonValue val value: String) {
    HARD_DELETE("Hard delete"),
    SOFT_DELETE("Soft delete"),
}
```

---

## Generation IDs and Resume Logic

**Purpose:** Enable detection of interrupted syncs and safe resume.

**How It Works:**

Every record includes `_airbyte_generation_id`:
- Incremental modes: minimumGenerationId = 0 (keep all generations)
- Full refresh: minimumGenerationId = generationId (replace old generations)

**Resume Detection (Truncate Mode):**

```
StreamLoader.start():
  tempGenId = getGenerationId(tempTable)   // null if doesn't exist
  realGenId = getGenerationId(realTable)   // null if doesn't exist

  case 1: tempGenId == stream.generationId
    → Resume interrupted sync (write to temp)

  case 2: realGenId == stream.generationId
    → Sync already completed, STATE lost (write to real, skip finalization)

  case 3: Neither matches
    → New sync (drop stale temp if exists, create fresh temp)
```

**Why Case 2 Matters:**

Scenario: Sync completes, SWAP succeeds, STATE emitted, but network error loses STATE.
- Platform thinks sync failed, retries
- Real table already has new data with correct generationId
- No need for temp table - write directly to real
- Avoids duplicate work and disk usage

---

## Airbyte Metadata Columns

**Always included (framework-managed):**

| Column | Type | Nullable | Purpose |
|--------|------|----------|---------|
| `_airbyte_raw_id` | UUID/String | NOT NULL | Unique record ID |
| `_airbyte_extracted_at` | Timestamp | NOT NULL | Extraction timestamp |
| `_airbyte_meta` | JSON | NOT NULL | Errors, warnings, metadata |
| `_airbyte_generation_id` | Integer | Yes | Sync generation tracking |

**Database-Specific Types:**

**Snowflake:**
```kotlin
"_AIRBYTE_RAW_ID" to "VARCHAR NOT NULL"
"_AIRBYTE_EXTRACTED_AT" to "TIMESTAMP_TZ NOT NULL"
"_AIRBYTE_META" to "VARIANT NOT NULL"
"_AIRBYTE_GENERATION_ID" to "NUMBER(38,0)"
```

**ClickHouse:**
```kotlin
"_airbyte_raw_id" to "String NOT NULL"
"_airbyte_extracted_at" to "DateTime64(3) NOT NULL"
"_airbyte_meta" to "String NOT NULL"
"_airbyte_generation_id" to "UInt32 NOT NULL"
```

**Important:**
- **Filter out** during schema discovery and computation
- Never in `ColumnChangeset` (managed separately)
- Created first in CREATE TABLE statements
- Case sensitivity varies by database (Snowflake uppercase, ClickHouse lowercase)

---

## Sync Mode Selection

**Based on `minimumGenerationId` and `importType`:**

| minimumGenerationId | importType | StreamLoader | Behavior |
|---------------------|------------|--------------|----------|
| 0 | Append | `DirectLoadTableAppendStreamLoader` | Direct insert to final table |
| 0 | Dedupe | `DirectLoadTableDedupStreamLoader` | Temp → MERGE with PK dedup |
| generationId | Append | `DirectLoadTableAppendTruncateStreamLoader` | Temp → SWAP |
| generationId | Dedupe | `DirectLoadTableDedupTruncateStreamLoader` | Temp → dedupe → SWAP |

**Pattern:**

```kotlin
override fun createStreamLoader(stream: DestinationStream): StreamLoader {
    val initialStatus = initialStatuses[stream]!!
    val tableNames = names[stream]!!.tableNames
    val columnMapping = names[stream]!!.columnNameMapping

    return when (stream.minimumGenerationId) {
        0L -> when (stream.importType) {
            is Dedupe -> DirectLoadTableDedupStreamLoader(
                stream, initialStatus, tableNames.finalTableName!!,
                tempTableNameGenerator.generate(tableNames.finalTableName!!),
                columnMapping, client, client, streamStateStore
            )
            else -> DirectLoadTableAppendStreamLoader(
                stream, initialStatus, tableNames.finalTableName!!,
                tempTableNameGenerator.generate(tableNames.finalTableName!!),
                columnMapping, client, client, streamStateStore
            )
        }
        stream.generationId -> when (stream.importType) {
            is Dedupe -> DirectLoadTableDedupTruncateStreamLoader(...)
            else -> DirectLoadTableAppendTruncateStreamLoader(...)
        }
        else -> throw SystemErrorException("Hybrid refresh not supported")
    }
}
```

---

## Common Operations Reference

### CREATE TABLE

```kotlin
fun createTable(stream: DestinationStream, tableName: TableName, ...): String {
    val columnDeclarations = stream.schema.asColumns()
        .map { (name, type) -> formatColumn(name, type) }
        .joinToString(",\n")

    return """
        CREATE TABLE ${fullyQualifiedName(tableName)} (
          ${metadataColumns}
          ${columnDeclarations}
        )
    """.trimIndent().andLog()
}
```

### UPSERT (Dedupe)

```sql
MERGE INTO final_table AS target
USING (
  SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (
      PARTITION BY primary_key
      ORDER BY _airbyte_extracted_at DESC
    ) AS rn
    FROM temp_table
  ) WHERE rn = 1
) AS source
ON target.pk = source.pk
WHEN MATCHED AND source.cursor > target.cursor THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...
```

### OVERWRITE (Truncate)

```sql
-- Option 1: SWAP (if database supports)
ALTER TABLE final SWAP WITH temp;
DROP TABLE temp;

-- Option 2: EXCHANGE (ClickHouse)
EXCHANGE TABLES final AND temp;
DROP TABLE temp;

-- Option 3: DROP + RENAME
DROP TABLE IF EXISTS final;
ALTER TABLE temp RENAME TO final;
```

### ALTER TABLE (Schema Evolution)

```sql
-- Add column
ALTER TABLE t ADD COLUMN new_col VARCHAR;

-- Drop column
ALTER TABLE t DROP COLUMN old_col;

-- Modify type (Postgres)
ALTER TABLE t ALTER COLUMN col TYPE VARCHAR USING col::VARCHAR;

-- Modify type (ClickHouse)
ALTER TABLE t MODIFY COLUMN col Nullable(String);
```

---

## Quick Reference Tables

### Typical SQL Operations

| Operation | Typical SQL | When Called |
|-----------|------------|-------------|
| Create namespace | `CREATE SCHEMA IF NOT EXISTS` | Writer.setup() |
| Create table | `CREATE TABLE (columns...)` | StreamLoader.start() |
| Drop table | `DROP TABLE IF EXISTS` | StreamLoader.close() |
| Count rows | `SELECT COUNT(*) FROM table` | Initial status gathering |
| Get generation ID | `SELECT _airbyte_generation_id FROM table LIMIT 1` | Initial status gathering |
| Copy table | `INSERT INTO target SELECT * FROM source` | Rarely (append truncate) |
| Upsert | `MERGE INTO target USING source ON pk WHEN MATCHED...` | Dedupe mode finalization |
| Overwrite | `SWAP/EXCHANGE/DROP+RENAME` | Truncate mode finalization |
| Alter table | `ALTER TABLE ADD/DROP/MODIFY COLUMN` | Schema evolution |

### Error Classification

| Error Type | When to Use | Example |
|------------|-------------|---------|
| `ConfigErrorException` | User-fixable | Bad credentials, missing permissions, invalid config |
| `TransientErrorException` | Retryable | Network timeout, DB unavailable, connection pool full |
| `SystemErrorException` | Internal | Null pointer, illegal state, unimplemented feature |

**Read Consistency During Failures:**

Guarantee: Readers always see consistent state, even during connector failures.

- Sync fails before finalization: Real table unchanged, readers see old data
- Sync fails during finalization: Database transaction rollback, readers see old data
- Sync succeeds but STATE lost: Real table has new data (correct state)

**Cleanup:** StreamLoader.close(streamCompleted=false) always drops temp tables.

### Log Levels

| Level | When to Use | Example |
|-------|-------------|---------|
| `info` | Normal operations | "Beginning insert into table...", "Finished insert of 1000 rows" |
| `warn` | Unexpected but recoverable | "CSV file path not set", "Falling back to default" |
| `error` | Will fail operation | "Unable to flush data", "Failed to execute query" |
| `debug` | Detailed diagnostics | "Table does not exist (expected)", "Connection attempt 2/3" |

---

## Implementation Checklist

### Phase 1: Core Components
- [ ] SQL Generator with all operations
- [ ] Database Client implementing both interfaces
- [ ] Insert Buffer with efficient batch writes
- [ ] Column Utilities for type mapping

### Phase 2: Configuration
- [ ] Specification class with all properties
- [ ] Configuration data class
- [ ] Configuration Factory with validation
- [ ] BeanFactory with DI setup

### Phase 3: Orchestration
- [ ] Name Generators (table, column, temp)
- [ ] Initial Status Gatherer (usually extend base)
- [ ] Writer with setup() and createStreamLoader()
- [ ] Aggregate (3-line delegation)
- [ ] AggregateFactory

### Phase 4: Validation
- [ ] Checker with connection test
- [ ] Error handling (ConfigError, TransientError, SystemError)
- [ ] Logging throughout

### Phase 5: Testing
- [ ] Unit tests for SQL generation
- [ ] Component tests (TableOperationsSuite)
- [ ] Integration tests (BasicFunctionalityIntegrationTest)
- [ ] Test all sync modes (append, dedupe, overwrite)
- [ ] Test schema evolution
- [ ] Test CDC if supported

### Phase 6: Polish
- [ ] All SQL logged
- [ ] Resources cleaned up in finally
- [ ] Error messages actionable
- [ ] Documentation complete

---

## The Three Operations

**Every connector must support three operations:**

| Operation | Trigger | Purpose | Output | Implementation |
|-----------|---------|---------|--------|----------------|
| `--spec` | CLI flag | Return connector capabilities | SPEC message with JSON schema | Automatic (via Specification class) |
| `--check` | CLI flag | Validate connection | CONNECTION_STATUS message | Implement Checker |
| `--write` | CLI flag | Execute sync | STATE messages | Implement Writer, Client, Buffer |

### Spec Operation

**Command:**
```bash
destination-{db} --spec
```

**What it does:**
- Reads your `{DB}Specification` class
- Generates JSON schema from Jackson annotations
- Adds supported sync modes from `{DB}SpecificationExtension`
- Returns SPEC message to stdout

**What you implement:**
- `{DB}Specification` class with `@JsonProperty`, `@JsonSchemaTitle`, etc.
- `{DB}SpecificationExtension` declaring supported sync modes
- `application.yml` with documentation URL (optional)

**Output example:**
```json
{
  "type": "SPEC",
  "spec": {
    "documentationUrl": "https://docs.airbyte.com/integrations/destinations/{db}",
    "connectionSpecification": {
      "$schema": "http://json-schema.org/draft-07/schema#",
      "type": "object",
      "required": ["hostname", "database", "username", "password"],
      "properties": { ... }
    },
    "supportsIncremental": true,
    "supported_destination_sync_modes": ["overwrite", "append", "append_dedup"]
  }
}
```

**Testing:**
```kotlin
// src/test-integration/kotlin/.../spec/{DB}SpecTest.kt
class {DB}SpecTest : SpecTest()

// Validates against: src/test-integration/resources/expected-spec-oss.json
```

**Covered in:** Phase 0, Steps 0.6-0.12 of step-by-step-guide.md

### Check Operation

**Command:**
```bash
destination-{db} --check --config config.json
```

**What it does:**
- Validates configuration
- Tests database connection
- Creates test table, inserts record, verifies, cleans up
- Returns CONNECTION_STATUS (SUCCEEDED or FAILED)

**What you implement:**
- `{DB}Checker` class implementing `DestinationCheckerV2`
- `check()` method that validates connection

**Output example:**
```json
{
  "type": "CONNECTION_STATUS",
  "connectionStatus": {
    "status": "SUCCEEDED"
  }
}
```

**Covered in:** Phase 5, Step 5.9 of step-by-step-guide.md

### Write Operation

**Command:**
```bash
destination-{db} --write --config config.json --catalog catalog.json < messages.jsonl
```

**What it does:**
- Reads RECORD and STATE messages from stdin
- Processes records through data pipeline
- Writes to database via your InsertBuffer
- Emits STATE messages to stdout
- Handles all sync modes (append, dedupe, overwrite)

**What you implement:**
- All 4 core components (Client, SqlGenerator, InsertBuffer, ColumnUtils)
- Writer, Aggregate, AggregateFactory
- Name generators

**Output example:**
```json
{"type":"LOG","log":{"level":"INFO","message":"Beginning sync..."}}
{"type":"LOG","log":{"level":"INFO","message":"Finished insert of 1000 rows"}}
{"type":"STATE","state":{"type":"STREAM","stream":{...},"sourceStats":{"recordCount":1000.0}}}
```

**Guarantees:**

1. **STATE Emission:** Only after database COMMIT completes
2. **Atomicity:** Finalization (MERGE/SWAP) is atomic or skipped
3. **Read Consistency:** Readers see old data or new data, never mixed/partial

**Error Recovery Scenarios:**

| Failure Point | Database State | Reader View | Recovery |
|---------------|----------------|-------------|----------|
| Before flush | No changes | Old data | Retry from last STATE |
| During flush | Partial in temp | Old data (real unchanged) | Drop temp, retry |
| Before finalization | Complete in temp | Old data (real unchanged) | Resume, complete finalization |
| During SWAP | Database rolls back | Old data | Retry SWAP |
| After SWAP, before STATE | New data committed | New data (correct!) | Platform retries, detects completion via generationId |

**Key Insight:** Temp table strategy ensures real table is never partially updated.

**Covered in:** Phases 1-11 of step-by-step-guide.md

---

## CDK Version Pinning

### Required Setup

**File:** `destination-{db}/gradle.properties`

```properties
# Always pin to a specific version for production
cdkVersion=0.1.76
```

### Pinning Strategy

**Production connectors (merged to main):**
- ✅ Must use pinned version: `cdkVersion=0.1.76`
- ❌ Never use: `cdkVersion=local`

**During CDK development:**
- Use `cdkVersion=local` for faster iteration
- Switch back to pinned version before merging

### How It Works

**The `airbyte-bulk-connector` plugin:**
1. Reads `cdkVersion` from `gradle.properties`
2. If pinned (e.g., `0.1.76`): Resolves Maven artifacts
   - `io.airbyte.bulk-cdk:bulk-cdk-core-load:0.1.76`
   - `io.airbyte.bulk-cdk:bulk-cdk-toolkits-load-db:0.1.76`
3. If `local`: Uses project references
   - `:airbyte-cdk:bulk:core:load`
   - `:airbyte-cdk:bulk:toolkits:load-db`

### Verify Pinning

```bash
./gradlew :destination-{db}:dependencies --configuration runtimeClasspath | grep bulk-cdk
```

**Expected (pinned):**
```
io.airbyte.bulk-cdk:bulk-cdk-core-load:0.1.76
```

**Wrong (local):**
```
project :airbyte-cdk:bulk:core:load
```

### Upgrade CDK Version

**Manual:**
```bash
# Edit gradle.properties
cdkVersion=0.1.76  # Update to new version
```

**Automated:**
```bash
./gradlew destination-{db}:upgradeCdk --cdkVersion=0.1.76
```

### Check Latest CDK Version

```bash
cat airbyte-cdk/bulk/version.properties
```

---

## Time Estimates

| Component | Effort | Lines | Time |
|-----------|--------|-------|------|
| SQL Generator | High | 300-500 | 1-2 days |
| Database Client | High | 400-600 | 1-2 days |
| Insert Buffer | Medium | 200-300 | 0.5-1 day |
| Column Utilities | Medium | 100-200 | 0.5 day |
| Configuration | Low | 100-150 | 0.5 day |
| Name Generators | Low | 50-100 | 0.25 day |
| Checker | Low | 50-80 | 0.25 day |
| Writer | Low | 80-120 | 0.25 day |
| Boilerplate | Minimal | 100-150 | 0.5 day |
| Testing | Medium | - | 2-3 days |
| **Total** | - | **~2000-3000** | **~1 week** |

**Critical Path:** SqlGenerator → Client → InsertBuffer → ColumnUtils
