# Dataflow CDK Architecture

**Summary:** The Airbyte Dataflow CDK is a framework that orchestrates destination connector write operations. You implement 4 database-specific components (SQL generator, client, insert buffer, column utilities). The CDK handles message parsing, data flow, table lifecycle, state management, and error handling. Result: Write ~4 custom components, get all sync modes (append, dedupe, overwrite) for free.

---

## Architecture Overview

### Entry Point to Database

```
main()
  → AirbyteDestinationRunner.run(*args)
    → Parse CLI (--spec, --check, --write)
    → Create Micronaut context
    → Select Operation (SpecOperation, CheckOperation, WriteOperationV2)
    → Execute operation
```

**Write Operation Flow:**
```
WriteOperationV2.execute()
  → DestinationLifecycle.run()
    1. Writer.setup()              [Create namespaces]
    2. Initialize streams          [Create StreamLoaders]
    3. runDataPipeline()           [Process messages]
    4. Finalize streams            [MERGE/SWAP/cleanup]
    5. Teardown                    [Close connections]
```

### Data Flow Pipeline

**stdin → Database:**

```
Airbyte Platform          Connector Pipeline              Database
      |                          |                            |
      |-- RECORD messages ------>|                            |
      |-- STATE messages -------->|                            |
      |                          |                            |
      |                      Parse JSON                       |
      |                      Transform types                  |
      |                      Map column names                 |
      |                      Batch records                    |
      |                          |                            |
      |                    Aggregate.accept()                 |
      |                          ↓                            |
      |                  InsertBuffer.accumulate()            |
      |                          |                            |
      |                    [Buffering]                        |
      |                          |                            |
      |                    Aggregate.flush()                  |
      |                          ↓                            |
      |                  InsertBuffer.flush() --------------->| Write batch
      |                          |                            |
      |                      [Repeat]                         |
      |                          |                            |
      |                 StreamLoader.close()                  |
      |                          ↓                            |
      |                    MERGE/SWAP/nothing -------------->| Finalize
      |<----- STATE emitted -----|                            |
```

**Key Insight:** Your `InsertBuffer` only writes batches. The framework handles message parsing, batching triggers, and finalization strategy (MERGE vs SWAP vs direct).

---

## Core Abstractions

### StreamLoader (CDK-Provided)

**Purpose:** Orchestrates per-stream write lifecycle

**You don't implement** - you instantiate the right one based on sync mode

**4 Variants:**

| StreamLoader | Mode | Strategy | Use Case |
|--------------|------|----------|----------|
| `DirectLoadTableAppendStreamLoader` | Append | Direct write to final table | Logs, append-only data |
| `DirectLoadTableDedupStreamLoader` | Dedupe | Temp table → MERGE with PK dedup | Incremental sync with PK |
| `DirectLoadTableAppendTruncateStreamLoader` | Overwrite | Temp table → SWAP | Full refresh without PK |
| `DirectLoadTableDedupTruncateStreamLoader` | Dedupe + Overwrite | Temp table → dedupe → SWAP | Full refresh with PK |

**Lifecycle:**

```kotlin
StreamLoader.start() {
  - Check if final table exists
  - Create/evolve final table
  - Create temp table if needed (dedupe/truncate)
  - Store target table name in state
}

[Records flow through pipeline → your InsertBuffer writes to table]

StreamLoader.close(streamCompleted) {
  if (streamCompleted) {
    // Dedupe: MERGE temp → final
    // Truncate: SWAP temp ↔ final
    // Append: nothing (already in final)
  }
  // Always cleanup temp tables
}
```

**Selection Pattern:**

```kotlin
override fun createStreamLoader(stream: DestinationStream): StreamLoader {
    return when (stream.minimumGenerationId) {
        0L -> when (stream.importType) {
            is Dedupe -> DirectLoadTableDedupStreamLoader(...)
            else -> DirectLoadTableAppendStreamLoader(...)
        }
        stream.generationId -> when (stream.importType) {
            is Dedupe -> DirectLoadTableDedupTruncateStreamLoader(...)
            else -> DirectLoadTableAppendTruncateStreamLoader(...)
        }
        else -> throw SystemErrorException("Hybrid refresh not supported")
    }
}
```

### Aggregate (Pattern-Based)

**Purpose:** Accumulates records, triggers flushing

**Your Implementation (3 lines):**

```kotlin
class MyAggregate(private val buffer: MyInsertBuffer) : Aggregate {
    override fun accept(record: RecordDTO) {
        buffer.accumulate(record.fields)
    }

    override suspend fun flush() {
        buffer.flush()
    }
}
```

**Created by:** `AggregateFactory` per stream

```kotlin
@Factory
class MyAggregateFactory(
    private val client: MyAirbyteClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
) : AggregateFactory {
    override fun create(key: StoreKey): Aggregate {
        // Get table name set by StreamLoader
        val tableName = streamStateStore.get(key)!!.tableName

        val buffer = MyInsertBuffer(tableName, client)
        return MyAggregate(buffer)
    }
}
```

### TableOperationsClient (You Implement)

**Purpose:** Database primitive operations

**Key Methods:**

```kotlin
interface TableOperationsClient {
    suspend fun createNamespace(namespace: String)
    suspend fun namespaceExists(namespace: String): Boolean
    suspend fun createTable(stream, tableName, columnMapping, replace)
    suspend fun tableExists(table: TableName): Boolean
    suspend fun dropTable(tableName: TableName)
    suspend fun countTable(tableName: TableName): Long?
    suspend fun getGenerationId(tableName: TableName): Long
    suspend fun overwriteTable(source, target)  // For truncate mode
    suspend fun copyTable(columnMapping, source, target)
    suspend fun upsertTable(stream, columnMapping, source, target)  // For dedupe
}
```

**Pattern:**

```kotlin
@Singleton
class MyAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: MySqlGenerator,
) : TableOperationsClient, TableSchemaEvolutionClient {

    override suspend fun createTable(...) {
        execute(sqlGenerator.createTable(...))
    }

    override suspend fun upsertTable(...) {
        execute(sqlGenerator.upsertTable(...))  // MERGE statement
    }

    private suspend fun execute(sql: String) {
        dataSource.connection.use { conn ->
            conn.createStatement().use { stmt ->
                stmt.executeQuery(sql)
            }
        }
    }
}
```

**Separation:** Client executes SQL, SqlGenerator generates SQL

### TableSchemaEvolutionClient (You Implement)

**Purpose:** Automatic schema adaptation

**4-Step Process:**

```kotlin
// 1. Discover current schema from database
suspend fun discoverSchema(tableName): TableSchema

// 2. Compute expected schema from stream
fun computeSchema(stream, columnMapping): TableSchema

// 3. Compare (automatic by CDK)
val changeset = ColumnChangeset(
    columnsToAdd = ...,
    columnsToDrop = ...,
    columnsToChange = ...,
)

// 4. Apply changes
suspend fun applyChangeset(..., changeset)
```

**When Called:** Automatically by `StreamLoader.start()` if table exists

**Operations:**
- **Add column:** `ALTER TABLE ADD COLUMN`
- **Drop column:** `ALTER TABLE DROP COLUMN`
- **Widen type:** `ALTER TABLE ALTER COLUMN TYPE` (safe)
- **Narrow type:** Temp column + cast + rename (complex)

### DestinationWriter (Pattern-Based)

**Purpose:** Orchestration layer

**Your Implementation:**

```kotlin
@Singleton
class MyWriter(
    private val names: TableCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val client: MyAirbyteClient,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DestinationWriter {
    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>

    override suspend fun setup() {
        // Create all namespaces
        names.values
            .map { it.tableNames.finalTableName!!.namespace }
            .toSet()
            .forEach { client.createNamespace(it) }

        // Gather initial state (table exists? gen ID? columns?)
        initialStatuses = stateGatherer.gatherInitialStatus(names)
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val initialStatus = initialStatuses[stream]!!
        val tableNames = names[stream]!!.tableNames
        val columnMapping = names[stream]!!.columnNameMapping

        return /* Select appropriate StreamLoader */
    }
}
```

**Key Responsibilities:**
- Create namespaces (schema/database)
- Gather initial table state
- Select correct StreamLoader for each stream
- **Does NOT:** Create tables, write data, perform schema evolution (StreamLoader does)

---

## What the CDK Provides

### Automatic Services

| Component | Responsibilities | Your Interaction |
|-----------|-----------------|------------------|
| **DestinationLifecycle** | Overall orchestration | None - runs automatically |
| **Data Pipeline** | Parse messages, transform types, batch records | Configure via ColumnUtils |
| **4 StreamLoaders** | Table lifecycle, finalization strategy | Instantiate the right one |
| **StreamStateStore** | Coordinate InsertBuffer ↔ StreamLoader | Read from in AggregateFactory |
| **TableCatalog** | Column name mapping (logical → physical) | Query for mapped column names |
| **State Management** | Track checkpoints, emit STATE messages | Automatic after successful flush |
| **Error Handling** | Classify errors, emit TRACE messages | Throw ConfigError/SystemError |

### Base Classes with Defaults

| Base Class | Purpose | Customization Needed |
|------------|---------|---------------------|
| `BaseDirectLoadInitialStatusGatherer` | Gather table state before sync | Usually none - just extend |
| `DefaultTempTableNameGenerator` | Generate temp table names | Usually none - use as-is |

---

## What You Implement

### 4 Core Custom Components

| Component | Effort | Purpose | Lines of Code |
|-----------|--------|---------|---------------|
| **SQL Generator** | High | Generate DB-specific SQL | 300-500 |
| **Database Client** | High | Execute SQL, handle errors | 400-600 |
| **Insert Buffer** | Medium | Efficient batch writes | 200-300 |
| **Column Utilities** | Medium | Type mapping, column declarations | 100-200 |

### Pattern-Based Components

| Component | Effort | Purpose | Lines of Code |
|-----------|--------|---------|---------------|
| **Configuration** | Low | Config spec, factory, validation | 100-150 |
| **Name Generators** | Low | Table/column name formatting | 50-100 |
| **Checker** | Low | Connection validation | 50-80 |
| **Writer** | Low | Orchestration (setup, select loaders) | 80-120 |

### Boilerplate Components

| Component | Effort | Purpose | Lines of Code |
|-----------|--------|---------|---------------|
| **Aggregate** | Minimal | Delegate to buffer | 10-15 |
| **AggregateFactory** | Minimal | Create aggregate per stream | 20-30 |
| **WriteOperationV2** | Minimal | Entry point for write operation | 10-15 |
| **BeanFactory** | Low | Micronaut DI setup | 50-100 |

**Total:** ~20 components, ~2000-3000 lines of code

**Critical Path:** SqlGenerator → Client → InsertBuffer → ColumnUtils

---

## Key Concepts

### Temp Tables Strategy

**Why?**
- **Atomic semantics:** All-or-nothing commit
- **Isolation:** Transform without affecting final table
- **Easy rollback:** Just drop temp on failure
- **Performance:** Write without locks/constraints

**When?**
- **Dedupe mode:** Temp table → dedupe via MERGE → final table
- **Truncate mode:** Temp table → SWAP with final table
- **Append mode:** No temp table (direct write)

**Naming:** `_airbyte_tmp_{uuid}_{timestamp}` in internal schema

**Lifecycle:**
```
StreamLoader.start() → createTable(tempTable)
Records written to tempTable via InsertBuffer
StreamLoader.close() → finalize from tempTable → dropTable(tempTable)
```

### Zero Downtime Architecture

**Key Guarantee:** Readers never see empty or partial tables during sync.

**How:** Temp table + atomic swap pattern
- Write new data to temp table (readers see old data)
- Atomic SWAP/EXCHANGE operation (milliseconds)
- Readers instantly see new data

**Why Atomic:**
- SWAP/EXCHANGE are metadata operations (not data copying)
- Database guarantees atomicity
- Old data visible until swap completes

**Traditional ETL comparison:**
- DROP TABLE → CREATE TABLE = downtime (table doesn't exist)
- TRUNCATE → INSERT = downtime (empty table visible)
- Temp → SWAP = zero downtime (always consistent snapshot)

**Use Cases:**
- 24/7 dashboards (cannot tolerate "table not found")
- Production APIs (empty results = outage)
- Long-running syncs (old data available until completion)

### Sync Modes Mapping

| User Setting | minimumGenerationId | importType | StreamLoader |
|--------------|---------------------|------------|--------------|
| Incremental | 0 | Append | `DirectLoadTableAppendStreamLoader` |
| Incremental | 0 | Dedupe | `DirectLoadTableDedupStreamLoader` |
| Full Refresh (Append) | generationId | Append | `DirectLoadTableAppendTruncateStreamLoader` |
| Full Refresh (Overwrite) | generationId | Dedupe | `DirectLoadTableDedupTruncateStreamLoader` |

**Generation IDs:**
- `minimumGenerationId = 0`: Keep all existing data (incremental)
- `minimumGenerationId = generationId`: Replace all data (full refresh)
- `minimumGenerationId != 0 and != generationId`: Hybrid refresh (NOT SUPPORTED)

**Resume Logic (Truncate Mode):**

When StreamLoader.start() is called:
1. If tempTable exists AND tempTable.generationId == stream.generationId → Resume interrupted sync (write to temp)
2. If realTable exists AND realTable.generationId == stream.generationId → Sync already completed (write to real)
3. Otherwise → New sync (drop stale temp if exists, create fresh temp)

**Generation ID Purpose:**
- Uniquely identifies each sync attempt
- Written to `_airbyte_generation_id` column in every record
- Enables detection of interrupted syncs vs completed syncs
- Allows safe resume without duplicate work

### Deduplication Logic

**Dedupe StreamLoader uses window function:**

```sql
WITH deduped AS (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY primary_key
    ORDER BY _airbyte_extracted_at DESC
  ) AS rn
  FROM temp_table
)
SELECT * FROM deduped WHERE rn = 1
```

**Then MERGE into final:**

```sql
MERGE INTO final_table AS target
USING deduped AS source
ON target.pk = source.pk
WHEN MATCHED AND source.cursor > target.cursor THEN UPDATE ...
WHEN NOT MATCHED THEN INSERT ...
```

**CDC Handling (if enabled):**

```sql
MERGE INTO final_table AS target
USING deduped AS source
ON target.pk = source.pk
WHEN MATCHED AND source._ab_cdc_deleted_at IS NOT NULL THEN DELETE  -- Hard delete
WHEN MATCHED AND source.cursor > target.cursor THEN UPDATE ...
WHEN NOT MATCHED AND source._ab_cdc_deleted_at IS NULL THEN INSERT ...
```

### State Management

**Critical Guarantee:** STATE only emitted after data persisted to database.

**Flow:**
```
RECORD messages → buffer
STATE message → flush buffers → database COMMIT → emit STATE
```

**Timing:**
- STATE boundaries = commit points
- InsertBuffer.flush() must complete before STATE emitted
- StreamLoader.close() finalization completes before final STATE

**Recovery on Failure:**
- Platform retries from last emitted STATE
- Records after last STATE are re-sent
- Destination must be idempotent (generation IDs help)

### Airbyte Metadata Columns

**Always included (managed by framework):**

| Column | Type | Purpose |
|--------|------|---------|
| `_airbyte_raw_id` | UUID/String | Unique record identifier |
| `_airbyte_extracted_at` | Timestamp | Extraction timestamp |
| `_airbyte_meta` | JSON | Errors, warnings, transformations |
| `_airbyte_generation_id` | Integer | Sync generation tracking |

**Filtered out** during schema discovery and computation - never in ColumnChangeset

---

## Data Transformation

### Type Conversion

**AirbyteValue → Database Format:**

```
Pipeline receives: JSON message
  ↓ Deserialize
AirbyteValue (StringValue, IntegerValue, etc.)
  ↓ Transform
Database-specific format (via ColumnUtils)
  ↓ Buffer
InsertBuffer accumulates
  ↓ Format
CSV, binary, JSON, etc.
  ↓ Write
Database client writes batch
```

**Example:**

```json
// Source
{"id": 123, "name": "Alice", "created_at": "2024-01-01T12:00:00Z"}

// After transformation (RecordDTO.fields)
{
  "id": IntegerValue(123),
  "name": StringValue("Alice"),
  "created_at": TimestampValue("2024-01-01T12:00:00Z"),
  "_airbyte_raw_id": StringValue("uuid..."),
  "_airbyte_extracted_at": TimestampValue("2024-01-01T12:00:00Z"),
  "_airbyte_meta": ObjectValue(...),
  "_airbyte_generation_id": IntegerValue(42)
}

// InsertBuffer formats for database
CSV: "123,Alice,2024-01-01 12:00:00,uuid...,2024-01-01 12:00:00,{},42"
Binary: [0x7B, 0x00, ...] (database-specific format)
```

### Column Name Mapping

**Logical → Physical:**

```
Stream schema:     {"field_name": StringType}
                          ↓
ColumnNameGenerator:  "field_name" → "FIELD_NAME" (Snowflake)
                                   → "field_name" (ClickHouse)
                          ↓
TableCatalog stores:  {"field_name": "FIELD_NAME"}
                          ↓
Your code queries:    columnMapping["field_name"] → "FIELD_NAME"
```

**Use TableCatalog, don't implement manually**

---

## Error Handling

### Exception Types

| Exception | When to Use | Platform Action |
|-----------|-------------|-----------------|
| `ConfigErrorException` | User-fixable (bad creds, permissions, invalid config) | NO RETRY - notify user |
| `TransientErrorException` | Temporary (network timeout, DB unavailable) | RETRY with backoff |
| `SystemErrorException` | Internal errors, bugs | LIMITED RETRY - likely bug |

**Pattern:**

```kotlin
try {
    connection.executeQuery(sql)
} catch (e: SQLException) {
    when {
        e.message?.contains("permission") == true ->
            throw ConfigErrorException("Permission denied. Grant privileges.", e)
        e.message?.contains("timeout") == true ->
            throw TransientErrorException("Network timeout. Will retry.", e)
        else ->
            throw SystemErrorException("Unexpected SQL error", e)
    }
}
```

### Graceful Degradation

**On Failure:**

```kotlin
StreamLoader.close(streamCompleted = false) {
    // Skip finalization (no MERGE/SWAP)
    // Drop temp tables (cleanup)
    // Final table unchanged
}
```

**Result:**
- Final table untouched (atomicity preserved)
- Temp tables cleaned up
- Platform retries from last STATE checkpoint

---

## Integration Points

**Where framework calls your code:**

| Phase | Framework Calls | Your Code Executes |
|-------|----------------|-------------------|
| **Setup** | `Writer.setup()` | Create namespaces, gather initial state |
| **Stream Init** | `Writer.createStreamLoader()` | Select appropriate StreamLoader |
| | `StreamLoader.start()` | `createTable()`, `ensureSchemaMatches()` |
| | `AggregateFactory.create()` | Create InsertBuffer with target table |
| **Data Flow** | `Aggregate.accept()` | `InsertBuffer.accumulate()` |
| | `Aggregate.flush()` | `InsertBuffer.flush()` → write batch |
| **Finalize** | `StreamLoader.close()` | `upsertTable()` or `overwriteTable()` |
| | Always | `dropTable(tempTable)` |

**Key Insight:** Framework orchestrates when to call what. You implement the "what" (database operations), framework handles the "when" and "how".

---

## Common Questions

### Why separate SqlGenerator and Client?

**Separation of concerns:**
- SqlGenerator: Pure functions, testable, no side effects
- Client: I/O operations, error handling, resource management

**Benefits:**
- Test SQL generation without database
- Reuse SQL across multiple execution contexts
- Easier to debug (separate SQL bugs from execution bugs)

### When is schema evolution triggered?

**Automatically during `StreamLoader.start()` if:**
- Final table exists
- Stream schema has changed since last sync

**Never triggered if:**
- Table doesn't exist (fresh create)
- Append mode to temp table
- Schema unchanged

### What if my database doesn't support MERGE?

**Options:**

1. **Use temp table + window function + INSERT:**
```sql
-- Dedupe in temp
CREATE TABLE deduped AS SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY pk ORDER BY cursor DESC) AS rn
  FROM temp
) WHERE rn = 1;

-- DELETE + INSERT
DELETE FROM final WHERE pk IN (SELECT pk FROM deduped);
INSERT INTO final SELECT * FROM deduped;
```

2. **Use UPDATE + INSERT (slower):**
```sql
-- Update existing
UPDATE final SET col1 = temp.col1, ... FROM temp WHERE final.pk = temp.pk;

-- Insert new
INSERT INTO final SELECT * FROM temp WHERE pk NOT IN (SELECT pk FROM final);
```

3. **Use database-specific upsert:**
```sql
-- Postgres: INSERT ... ON CONFLICT
INSERT INTO final SELECT * FROM temp
ON CONFLICT (pk) DO UPDATE SET col1 = EXCLUDED.col1, ...;

-- MySQL: INSERT ... ON DUPLICATE KEY UPDATE
INSERT INTO final SELECT * FROM temp
ON DUPLICATE KEY UPDATE col1 = VALUES(col1), ...;
```

### How do I test my implementation?

**Levels:**

1. **Unit tests:** SqlGenerator (no database needed)
2. **Component tests:** TableOperationsSuite (basic operations)
3. **Integration tests:** BasicFunctionalityIntegrationTest (full sync)

**BasicFunctionalityIntegrationTest provides:**
- Append mode test
- Dedupe mode test
- Overwrite mode test
- Schema evolution test
- CDC test

**Use Testcontainers** for reproducible, isolated tests

---

## Performance Considerations

### Batching

**Framework triggers flush at:**
- Time interval (default: 60s)
- Buffer size threshold (configurable)
- State message boundary
- End of stream

**Your InsertBuffer can add:**
- Record count threshold (e.g., 1000 records)
- Byte size threshold (e.g., 10MB)
- File size threshold (for staging)

### Parallelism

**Framework parallelizes:**
- Multiple streams (configurable: `num-open-stream-workers`)
- Task execution (setup, write, finalize)

**Your code should:**
- Be thread-safe in `@Singleton` components
- Use connection pooling (HikariCP)
- Avoid blocking operations in suspend functions

### Memory Management

**Framework provides:**
- Memory reservation system (backpressure)
- Configurable buffer limits
- Automatic pause/resume based on memory

**Your InsertBuffer should:**
- Write to temp files for large batches (not all in memory)
- Stream data to database (don't load entire batch at once)
- Clean up resources in `finally` blocks

---

## CDK Version Pinning

**All production connectors must pin to a specific CDK version:**

**File:** `destination-{db}/gradle.properties`
```properties
cdkVersion=0.1.76  # Pin to specific version
```

**Never use in production:**
```properties
cdkVersion=local  # Only for CDK development
```

**The `airbyte-bulk-connector` plugin:**
- Reads `cdkVersion` from `gradle.properties`
- Resolves Maven artifacts: `io.airbyte.bulk-cdk:bulk-cdk-core-load:0.1.76`
- Or uses local project references if `cdkVersion=local`

**Verify pinning:**
```bash
./gradlew :destination-{db}:dependencies --configuration runtimeClasspath | grep bulk-cdk
```

**Expected:** `io.airbyte.bulk-cdk:bulk-cdk-core-load:0.1.76` (not `project :airbyte-cdk:bulk:...`)

**Upgrade CDK:**
```bash
./gradlew destination-{db}:upgradeCdk --cdkVersion=0.1.76
```

---

## Summary Checklist

**What you must provide:**
- [ ] CDK version pinned in `gradle.properties`
- [ ] SQL Generator with all operations
- [ ] Database Client implementing TableOperationsClient + TableSchemaEvolutionClient
- [ ] InsertBuffer with efficient batch writes
- [ ] Column Utilities for type mapping
- [ ] Configuration (spec, factory)
- [ ] Name Generators (table, column)
- [ ] Checker for connection validation
- [ ] Writer for orchestration
- [ ] Aggregate (3-line delegation)
- [ ] AggregateFactory (create buffer)
- [ ] BeanFactory (Micronaut DI)

**What the CDK provides:**
- [ ] 4 StreamLoader implementations (you just instantiate)
- [ ] Data pipeline (parse, transform, batch)
- [ ] State management (checkpointing)
- [ ] Error handling (classify, emit TRACE)
- [ ] TableCatalog (column name mapping)
- [ ] StreamStateStore (coordinate buffer ↔ loader)

**Result:**
- [ ] All sync modes work (append, dedupe, overwrite)
- [ ] Schema evolution automatic
- [ ] CDC support (if configured)
- [ ] State management automatic
- [ ] Error recovery automatic

**Effort:** ~1 week for experienced developer (4 core components + patterns + testing)
