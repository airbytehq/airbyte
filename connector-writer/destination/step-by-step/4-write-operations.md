# Write Operations: Core Sync Functionality

**Prerequisites:** Complete [3-write-infrastructure.md](./3-write-infrastructure.md) - Your DI setup must be complete and you must understand test contexts.

**What You'll Build:** After completing this guide, you'll have a working connector with:
- InsertBuffer with efficient batch writes
- Aggregate and AggregateFactory
- Writer orchestration
- Append mode (direct insert)
- Overwrite mode (temp table + atomic swap)
- Generation ID tracking
- `--write` operation working for basic syncs

---

## Write Phase 1: Writer & Append Mode (Business Logic)

**Goal:** Implement actual data writing (Writer, Aggregate, InsertBuffer)

**Checkpoint:** Can write one record end-to-end

**📋 Dependency Context:** Now that infrastructure exists (Phases 6-7), add business logic:
- InsertBuffer (accumulates and flushes records to database)
- Aggregate (processes transformed records)
- AggregateFactory (creates Aggregate instances)
- Writer (orchestrates setup and creates StreamLoaders)

**Key insight:** Infrastructure DI (Phase 7) is separate from business logic DI (Phase 8).
Phase 7 validates "can we start?" Phase 8 validates "can we write data?"

### Write Step 1: Create InsertBuffer

**File:** `write/load/{DB}InsertBuffer.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.{db}.client.{DB}AirbyteClient
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}

/**
 * Accumulates records and flushes to database in batches.
 *
 * NOT a @Singleton - created per-stream by AggregateFactory
 */
class {DB}InsertBuffer(
    private val tableName: TableName,
    private val client: {DB}AirbyteClient,
    private val flushLimit: Int = 1000,
) {
    private val buffer = mutableListOf<Map<String, AirbyteValue>>()
    private var recordCount = 0

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        buffer.add(recordFields)
        recordCount++

        if (recordCount >= flushLimit) {
            kotlinx.coroutines.runBlocking { flush() }
        }
    }

    suspend fun flush() {
        if (buffer.isEmpty()) return

        try {
            log.info { "Flushing $recordCount records to ${tableName}..." }

            // Simple multi-row INSERT for now
            // (Optimize in Phase 15: CSV staging, COPY, bulk APIs)
            buffer.forEach { record ->
                insertRecord(tableName, record)
            }

            log.info { "Finished flushing $recordCount records" }
        } finally {
            buffer.clear()
            recordCount = 0
        }
    }

    private suspend fun insertRecord(
        tableName: TableName,
        record: Map<String, AirbyteValue>
    ) {
        val columns = record.keys.joinToString(", ") { "\"$it\"" }
        val placeholders = record.keys.joinToString(", ") { "?" }
        val sql = """
            INSERT INTO "${tableName.namespace}"."${tableName.name}" ($columns)
            VALUES ($placeholders)
        """

        client.executeInsert(sql, record.values.toList())
    }
}
```

**Key points:**
- **NOT @Singleton** - one buffer per stream
- Simple implementation: single-row inserts
- Phase 15 (Optimization) replaces with bulk loading

**Why not @Singleton?**
- Each stream needs its own buffer
- Buffers hold stream-specific state (table name, accumulated records)
- AggregateFactory creates one buffer per stream

### Write Step 2: Add executeInsert() to Client

**File:** Update `client/{DB}AirbyteClient.kt`

```kotlin
// Add this method to {DB}AirbyteClient
fun executeInsert(sql: String, values: List<AirbyteValue>) {
    dataSource.connection.use { connection ->
        connection.prepareStatement(sql).use { statement ->
            values.forEachIndexed { index, value ->
                setParameter(statement, index + 1, value)
            }
            statement.executeUpdate()
        }
    }
}

private fun setParameter(statement: PreparedStatement, index: Int, value: AirbyteValue) {
    when (value) {
        is StringValue -> statement.setString(index, value.value)
        is IntegerValue -> statement.setLong(index, value.value)
        is NumberValue -> statement.setBigDecimal(index, value.value)
        is BooleanValue -> statement.setBoolean(index, value.value)
        is TimestampValue -> statement.setTimestamp(index, Timestamp.from(value.value))
        is DateValue -> statement.setDate(index, Date.valueOf(value.value))
        is TimeValue -> statement.setTime(index, Time.valueOf(value.value.toLocalTime()))
        is ObjectValue -> statement.setString(index, value.toJson())  // JSON as string
        is ArrayValue -> statement.setString(index, value.toJson())   // JSON as string
        is NullValue -> statement.setNull(index, Types.VARCHAR)
        else -> statement.setString(index, value.toString())
    }
}
```

**Note:** For non-JDBC databases, use native client APIs (e.g., MongoDB insertOne, ClickHouse native client)

### Write Step 3: Create Aggregate

**File:** `dataflow/{DB}Aggregate.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.integrations.destination.{db}.write.load.{DB}InsertBuffer

/**
 * Processes transformed records for a single stream.
 *
 * Dataflow pipeline: Raw record → Transform → RecordDTO → Aggregate.accept() → InsertBuffer
 *
 * NOT a @Singleton - created per-stream by AggregateFactory
 */
class {DB}Aggregate(
    private val buffer: {DB}InsertBuffer,
) : Aggregate {

    override fun accept(record: RecordDTO) {
        buffer.accumulate(record.fields)
    }

    override suspend fun flush() {
        buffer.flush()
    }
}
```

**What this does:**
- Receives transformed records from CDK dataflow pipeline
- Delegates to InsertBuffer for accumulation
- Implements flush() for end-of-stream flushing

**Dataflow pipeline:**
```
Platform → JSONL records
  ↓
AirbyteMessageDeserializer (CDK)
  ↓
RecordTransformer (CDK, uses ColumnNameMapper from Phase 7)
  ↓
RecordDTO (transformed record with mapped column names)
  ↓
Aggregate.accept()  ← YOUR CODE STARTS HERE
  ↓
InsertBuffer.accumulate()
  ↓
Database
```

### Write Step 4: Create AggregateFactory

**File:** `dataflow/{DB}AggregateFactory.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.orchestration.db.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.state.StoreKey
import io.airbyte.cdk.load.state.StreamStateStore
import io.airbyte.integrations.destination.{db}.client.{DB}AirbyteClient
import io.airbyte.integrations.destination.{db}.write.load.{DB}InsertBuffer
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Singleton

@Factory
class {DB}AggregateFactory(
    private val client: {DB}AirbyteClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
) : AggregateFactory {

    @Singleton
    override fun create(key: StoreKey): Aggregate {
        // StreamStateStore contains execution config for each stream
        // Config includes table name, column mapping, etc.
        val tableName = streamStateStore.get(key)!!.tableName

        val buffer = {DB}InsertBuffer(
            tableName = tableName,
            client = client,
        )

        return {DB}Aggregate(buffer)
    }
}
```

**What this does:**
- @Factory class provides factory method for creating Aggregates
- create() called once per stream at start of sync
- StreamStateStore provides table name for the stream
- Creates InsertBuffer → Aggregate chain

**Why factory pattern?**
- Aggregate needs per-stream state (table name)
- Can't use constructor injection (dynamic stream list)
- Factory receives StoreKey, looks up stream config, creates Aggregate

### Write Step 5: Create Writer

**File:** `write/{DB}Writer.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.*
import io.airbyte.cdk.load.state.StreamStateStore
import io.airbyte.cdk.load.table.TableCatalog
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.{db}.client.{DB}AirbyteClient
import io.micronaut.context.annotation.Singleton

@Singleton
class {DB}Writer(
    private val names: TableCatalog,
    private val stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val client: {DB}AirbyteClient,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DestinationWriter {

    private lateinit var initialStatuses: Map<DestinationStream, DirectLoadInitialStatus>

    override suspend fun setup() {
        // Create all namespaces
        names.values
            .map { it.tableNames.finalTableName!!.namespace }
            .toSet()
            .forEach { client.createNamespace(it) }

        // Gather initial state (which tables exist, generation IDs, etc.)
        initialStatuses = stateGatherer.gatherInitialStatus(names)
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        // Defensive: Handle streams not in catalog (for test compatibility)
        val initialStatus = if (::initialStatuses.isInitialized) {
            initialStatuses[stream] ?: DirectLoadInitialStatus(null, null)
        } else {
            DirectLoadInitialStatus(null, null)
        }

        val tableNameInfo = names[stream]
        val (realTableName, tempTableName, columnNameMapping) = if (tableNameInfo != null) {
            // Stream in catalog - use configured names
            Triple(
                tableNameInfo.tableNames.finalTableName!!,
                tempTableNameGenerator.generate(tableNameInfo.tableNames.finalTableName!!),
                tableNameInfo.columnNameMapping
            )
        } else {
            // Dynamic stream (test-generated) - use descriptor names directly
            val tableName = TableName(
                namespace = stream.mappedDescriptor.namespace ?: "test",
                name = stream.mappedDescriptor.name
            )
            Triple(tableName, tempTableNameGenerator.generate(tableName), ColumnNameMapping(emptyMap()))
        }

        // Phase 8: Append mode only
        // Phase 10: Add truncate mode (minimumGenerationId = generationId)
        // Phase 13: Add dedupe mode (importType is Dedupe)
        return DirectLoadTableAppendStreamLoader(
            stream,
            initialStatus,
            realTableName,
            tempTableName,
            columnNameMapping,
            client,  // TableOperationsClient
            client,  // TableSchemaEvolutionClient
            streamStateStore,
        )
    }
}
```

**What this does:**
- **setup()**: Creates namespaces, gathers initial table state
- **createStreamLoader()**: Creates StreamLoader for each stream
  - AppendStreamLoader: Just insert records (this phase)
  - TruncateStreamLoader: Overwrite table (Phase 10)
  - DedupStreamLoader: Upsert with primary key (Phase 13)

**Defensive pattern (lines 27-52):**
- Handles ConnectorWiringSuite creating dynamic test streams
- Test streams not in TableCatalog → use descriptor names directly
- Prevents NullPointerException in tests

**StreamLoader responsibilities:**
- start(): Create/prepare table
- accept(): Add record to buffer
- complete(): Flush and finalize

**CDK provides implementations:**
- DirectLoadTableAppendStreamLoader
- DirectLoadTableAppendTruncateStreamLoader
- DirectLoadTableDedupStreamLoader
- DirectLoadTableDedupTruncateStreamLoader

### Write Step 6: Create ConnectorWiringSuite Test

**File:** `src/test-integration/kotlin/.../component/{DB}WiringTest.kt`

```kotlin
package io.airbyte.integrations.destination.{db}.component

import io.airbyte.cdk.load.component.ConnectorWiringSuite
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.write.DestinationWriter
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["component"])
class {DB}WiringTest(
    override val writer: DestinationWriter,
    override val client: TableOperationsClient,
    override val aggregateFactory: AggregateFactory,
) : ConnectorWiringSuite {

    // Optional: Override test namespace if different from "test"
    // override val testNamespace = "my_database"

    @Test
    override fun `all beans are injectable`() {
        super.`all beans are injectable`()
    }

    @Test
    override fun `writer setup completes`() {
        super.`writer setup completes`()
    }

    @Test
    override fun `can create append stream loader`() {
        super.`can create append stream loader`()
    }

    @Test
    override fun `can write one record`() {
        super.`can write one record`()
    }
}
```

**What ConnectorWiringSuite does:**

**Test 1: `all beans are injectable`**
- Validates all DI beans exist
- Catches missing @Singleton annotations
- Catches circular dependencies

**Test 2: `writer setup completes`**
- Calls Writer.setup()
- Validates namespace creation works
- Catches database connection errors

**Test 3: `can create append stream loader`**
- Calls Writer.createStreamLoader()
- Validates StreamLoader instantiation
- Catches missing StreamLoader dependencies

**Test 4: `can write one record`** ← MOST IMPORTANT
- Creates test stream
- Calls StreamLoader.start() → creates table
- Calls Aggregate.accept() → buffers record
- Calls Aggregate.flush() → writes to database
- Validates record appears in database
- **END-TO-END validation of full write path!**

**Test context:**
- Uses MockDestinationCatalog (fast, no real catalog parsing)
- Uses Testcontainers database
- Component test (not integration test)

**Why MockDestinationCatalog?**
- Fast iteration (no catalog JSON parsing)
- Creates dynamic test streams
- Focuses on write logic, not catalog parsing

### Write Step 7: Validate ConnectorWiringSuite

**Validate:**
```bash
$ ./gradlew :destination-{db}:testComponentAllBeansAreInjectable \
             :destination-{db}:testComponentWriterSetupCompletes \
             :destination-{db}:testComponentCanCreateAppendStreamLoader \
             :destination-{db}:testComponentCanWriteOneRecord  # 4 tests should pass
$ ./gradlew :destination-{db}:componentTest  # 9 tests should pass
$ ./gradlew :destination-{db}:integrationTest  # 3 tests should pass
```

**If `can write one record` FAILS:**

**DI errors:**
→ Check Phase 7 infrastructure (WriteOperationV2, DatabaseInitialStatusGatherer, ColumnNameMapper)
→ Check Phase 6 name generators all have @Singleton

**Table creation errors:**
→ Check TableOperationsClient.createTable() implementation (Phase 4)
→ Check SqlGenerator.createTable() SQL syntax

**Insert errors:**
→ Check InsertBuffer.insertRecord() implementation
→ Check client.executeInsert() and setParameter() logic
→ Check column name mapping

**Record not found in database:**
→ Check buffer.flush() is called
→ Check SQL INSERT statement is correct
→ Query database directly to debug

✅ **Checkpoint:** First working sync + all previous phases still work

---

---

## Write Phase 2: Generation ID Support

**Goal:** Track sync generations for refresh handling

**Checkpoint:** Can retrieve generation IDs

**📋 What's a Generation ID?**
- Unique identifier for each sync run
- Used to distinguish "old data" from "new data" during refreshes
- Stored in `_airbyte_generation_id` column

**When used:**
- Full refresh: minimumGenerationId = generationId (replace all data)
- Incremental: minimumGenerationId = 0 (keep all data)

### Write Step 1: Enable Generation ID Test

**File:** Update `src/test-integration/kotlin/.../component/{DB}TableOperationsTest.kt`

```kotlin
@Test
override fun `get generation id`() {
    super.`get generation id`()
}
```

**What this tests:**
- TableOperationsClient.getGenerationId() returns correct value
- Returns 0L for tables without generation ID
- Returns actual generation ID from `_airbyte_generation_id` column

### Write Step 2: Validate

**Validate:**
```bash
$ ./gradlew :destination-{db}:testComponentGetGenerationId  # 1 test should pass
$ ./gradlew :destination-{db}:componentTest  # 10 tests should pass
```

✅ **Checkpoint:** Generation ID tracking works + all previous phases still work

---

---

## Write Phase 3: Overwrite Mode

**Goal:** Support full refresh (replace all data)

**Checkpoint:** Can replace table contents atomically

**📋 How Overwrite Works:**
1. Write new data to temp table
2. Atomically swap temp table with final table
3. Drop old table

**Sync modes:**
- **Append** (Phase 8): INSERT into existing table
- **Overwrite** (Phase 10): SWAP temp table with final table

### Write Step 1: Implement overwriteTable() in SQL Generator

**File:** Update `client/{DB}SqlGenerator.kt`

```kotlin
fun overwriteTable(source: TableName, target: TableName): List<String> {
    // Option 1: SWAP (Snowflake)
    return listOf(
        "ALTER TABLE ${fullyQualifiedName(target)} SWAP WITH ${fullyQualifiedName(source)}".andLog(),
        "DROP TABLE IF EXISTS ${fullyQualifiedName(source)}".andLog(),
    )

    // Option 2: EXCHANGE (ClickHouse)
    return listOf(
        "EXCHANGE TABLES ${fullyQualifiedName(target)} AND ${fullyQualifiedName(source)}".andLog(),
        "DROP TABLE IF EXISTS ${fullyQualifiedName(source)}".andLog(),
    )

    // Option 3: DROP + RENAME (fallback for most databases)
    return listOf(
        "DROP TABLE IF EXISTS ${fullyQualifiedName(target)}".andLog(),
        "ALTER TABLE ${fullyQualifiedName(source)} RENAME TO ${target.name.quote()}".andLog(),
    )

    // Option 4: BEGIN TRANSACTION + DROP + RENAME + COMMIT (for ACID guarantees)
    return listOf(
        "BEGIN TRANSACTION".andLog(),
        "DROP TABLE IF EXISTS ${fullyQualifiedName(target)}".andLog(),
        "ALTER TABLE ${fullyQualifiedName(source)} RENAME TO ${target.name.quote()}".andLog(),
        "COMMIT".andLog(),
    )
}
```

**Database-specific notes:**
- **Snowflake**: SWAP is atomic and instant (metadata operation)
- **ClickHouse**: EXCHANGE is atomic
- **Postgres/MySQL**: DROP + RENAME requires transaction for atomicity
- **BigQuery**: CREATE OR REPLACE TABLE (different pattern)

### Write Step 2: Implement overwriteTable() in Client

**File:** Update `client/{DB}AirbyteClient.kt`

```kotlin
override suspend fun overwriteTable(
    sourceTableName: TableName,
    targetTableName: TableName
) {
    val statements = sqlGenerator.overwriteTable(sourceTableName, targetTableName)
    statements.forEach { execute(it) }
}
```

### Write Step 3: Update Writer for Truncate Mode

**File:** Update `write/{DB}Writer.kt`

```kotlin
override fun createStreamLoader(stream: DestinationStream): StreamLoader {
    // Defensive: Handle streams not in catalog (for test compatibility)
    val initialStatus = if (::initialStatuses.isInitialized) {
        initialStatuses[stream] ?: DirectLoadInitialStatus(null, null)
    } else {
        DirectLoadInitialStatus(null, null)
    }

    val tableNameInfo = names[stream]
    val (realTableName, tempTableName, columnNameMapping) = if (tableNameInfo != null) {
        Triple(
            tableNameInfo.tableNames.finalTableName!!,
            tempTableNameGenerator.generate(tableNameInfo.tableNames.finalTableName!!),
            tableNameInfo.columnNameMapping
        )
    } else {
        val tableName = TableName(
            namespace = stream.mappedDescriptor.namespace ?: "test",
            name = stream.mappedDescriptor.name
        )
        Triple(tableName, tempTableNameGenerator.generate(tableName), ColumnNameMapping(emptyMap()))
    }

    // Choose StreamLoader based on sync mode
    return when (stream.minimumGenerationId) {
        0L -> DirectLoadTableAppendStreamLoader(
            stream, initialStatus, realTableName, tempTableName,
            columnNameMapping, client, client, streamStateStore
        )
        stream.generationId -> DirectLoadTableAppendTruncateStreamLoader(
            stream, initialStatus, realTableName, tempTableName,
            columnNameMapping, client, client, streamStateStore
        )
        else -> throw SystemErrorException("Hybrid refresh not supported")
    }
}
```

**What changed:**
- Added `when` statement to choose StreamLoader based on `minimumGenerationId`
- `minimumGenerationId = 0`: Append mode (keep old data)
- `minimumGenerationId = generationId`: Truncate mode (replace old data)

**StreamLoader behavior:**
- **AppendStreamLoader**: Writes directly to final table
- **AppendTruncateStreamLoader**: Writes to temp table, then swaps

### Write Step 4: Enable Tests

**File:** Update `src/test-integration/kotlin/.../component/{DB}TableOperationsTest.kt`

```kotlin
@Test
override fun `overwrite tables`() {
    super.`overwrite tables`()
}
```

### Write Step 5: Validate

**Validate:**
```bash
$ ./gradlew :destination-{db}:testComponentOverwriteTables  # 1 test should pass
$ ./gradlew :destination-{db}:componentTest  # 11 tests should pass
$ ./gradlew :destination-{db}:integrationTest  # 3 tests should pass
```

✅ **Checkpoint:** Full refresh mode works + all previous phases still work

---

---

## Write Phase 4: Copy Operation

**Goal:** Support table copying (used internally by some modes)

**Checkpoint:** Can copy data between tables

**📋 When Copy is Used:**
- Dedupe mode: Copy deduplicated data from temp to final
- Some overwrite implementations: Copy instead of swap
- Schema evolution: Copy to new schema

### Write Step 1: Implement copyTable() in SQL Generator

**File:** Update `client/{DB}SqlGenerator.kt`

```kotlin
fun copyTable(
    columnMapping: ColumnNameMapping,
    source: TableName,
    target: TableName
): String {
    val columnList = columnMapping.values.joinToString(", ") { "\"$it\"" }

    return """
        INSERT INTO ${fullyQualifiedName(target)} ($columnList)
        SELECT $columnList
        FROM ${fullyQualifiedName(source)}
    """.trimIndent().andLog()
}
```

**What this does:**
- Copies all rows from source to target
- Only copies mapped columns (not all columns)
- Preserves data types (SELECT → INSERT)

**Alternative: Include Airbyte metadata columns explicitly:**
```kotlin
fun copyTable(
    columnMapping: ColumnNameMapping,
    source: TableName,
    target: TableName
): String {
    // Include Airbyte metadata + user columns
    val allColumns = listOf(
        "_airbyte_raw_id",
        "_airbyte_extracted_at",
        "_airbyte_meta",
        "_airbyte_generation_id"
    ) + columnMapping.values

    val columnList = allColumns.joinToString(", ") { "\"$it\"" }

    return """
        INSERT INTO ${fullyQualifiedName(target)} ($columnList)
        SELECT $columnList
        FROM ${fullyQualifiedName(source)}
    """.trimIndent().andLog()
}
```

### Write Step 2: Implement copyTable() in Client

**File:** Update `client/{DB}AirbyteClient.kt`

```kotlin
override suspend fun copyTable(
    columnNameMapping: ColumnNameMapping,
    sourceTableName: TableName,
    targetTableName: TableName
) {
    execute(sqlGenerator.copyTable(columnNameMapping, sourceTableName, targetTableName))
}
```

### Write Step 3: Enable Test

**File:** Update `src/test-integration/kotlin/.../component/{DB}TableOperationsTest.kt`

```kotlin
@Test
override fun `copy tables`() {
    super.`copy tables`()
}
```

### Write Step 4: Validate

**Validate:**
```bash
$ ./gradlew :destination-{db}:testComponentCopyTables  # 1 test should pass
$ ./gradlew :destination-{db}:componentTest  # 12 tests should pass
$ ./gradlew :destination-{db}:integrationTest  # 3 tests should pass
```

✅ **Checkpoint:** Copy operation works + all previous phases still work

---

---

## Next Steps

**Next:** Your connector now works for basic use cases! Continue to [5-advanced-features.md](./5-advanced-features.md) for production-ready features, or jump to [6-testing.md](./6-testing.md) to run the full test suite.
