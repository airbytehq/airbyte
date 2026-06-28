# Extract Bulk CDK Architecture

**Summary:** The Airbyte Extract Bulk CDK is a Kotlin-based framework that orchestrates source connector read operations. The JDBC and CDC toolkits provide stock implementations for all core components (configuration, metadata querier, partition factory, query generator, state management). Database connectors customize only what's needed for their specific dialect or features. The CDK handles stream orchestration, state management, concurrency, and the Airbyte protocol. Result: Extend toolkit defaults where needed, get all sync modes (full refresh, incremental cursor-based, incremental CDC) with resumability for free.

---

## Architecture Overview

### Entry Point to Data Extraction

```
main()
  → AirbyteSourceRunner.run(*args)
    → Parse CLI (--spec, --check, --discover, --read)
    → Create Micronaut context
    → Select Operation (SpecOperation, CheckOperation, DiscoverOperation, ReadOperation)
    → Execute operation
```

**Read Operation Flow:**
```
ReadOperation.execute()
  → RootReader.read()
    1. For each Feed (Global or Stream)
      → FeedReader.read()
        2. For each round (PartitionsCreatorID)
          → PartitionsCreator.create() [Your factory creates partitions]
            3. For each Partition
              → PartitionReader.run() [Your reader reads data]
              → Emit RECORD messages
              → Return checkpoint with state
          → StateManager.update() [Update state]
          → Emit STATE messages
```

**Sequential vs Concurrent Connectors:**

Connectors can operate in two modes for reading partitions:

| Mode | Within a Stream | Across Streams | Use Case |
|------|----------------|----------------|----------|
| **Sequential** | Partitions read serially (one after another) | Streams read concurrently (up to `maxConcurrency` threads) | Views, tables without PK, or databases with connection limits |
| **Concurrent** | Partitions read in parallel (up to `maxConcurrency` threads) | Streams also read concurrently | Large tables with PK, high-throughput databases |

**Key Points:**

- **Sequential connectors** read partitions of a single stream (table) serially, but can still read partitions from *different* streams concurrently up to the configured `maxConcurrency` limit.
- **Concurrent connectors** attempt to split each table into concurrent partitions. The splitting strategy varies by database:
  - **Sampling-based:** Use `SELECT FROM TABLE SAMPLE` SQL commands to estimate table size and split by PK ranges
  - **Database-specific:** Custom implementations (e.g., Postgres uses CTID/page-based splitting, MySQL uses PK range queries)
- Both modes respect the `maxConcurrency` configuration parameter to limit total concurrent operations.

**Example Flow (Sequential Connector, maxConcurrency=4):**

```
Time →
Stream A: [Partition 1] → [Partition 2] → [Partition 3]
Stream B: [Partition 1] → [Partition 2]
Stream C: [Partition 1] → [Partition 2] → [Partition 3] → [Partition 4]
Stream D: [Partition 1]

All 4 streams run concurrently, but within each stream, partitions are serial.
```

**Example Flow (Concurrent Connector, maxConcurrency=4):**

```
Time →
Stream A: [Partition 1, 2, 3] ← all run concurrently
Stream B: [Partition 1, 2] ← both run concurrently

With maxConcurrency=4, Stream A might run 3 partitions + Stream B runs 1 partition = 4 concurrent operations
```

### Data Flow Pipeline

**Database → Airbyte Platform:**

```
Database                  Connector Pipeline                Airbyte Platform
    |                            |                                  |
    |<-- SELECT query ----------|                                  |
    |                            |                                  |
    |-- ResultSet ------------->|                                  |
    |                      Parse JDBC types                         |
    |                      Convert to AirbyteValue                  |
    |                      Accumulate records                       |
    |                            |                                  |
    |                      PartitionReader                          |
    |                            |                                  |
    |                      [Batching]                               |
    |                            |                                  |
    |                      StreamRecordConsumer.accept()            |
    |                            |                                  |
    |                      Emit RECORD messages ------------------>|
    |                            |                                  |
    |                      [Checkpoint reached]                     |
    |                            |                                  |
    |                      Return PartitionReadCheckpoint           |
    |                      StateManager.checkpoint()                |
    |                            |                                  |
    |                      Emit STATE message -------------------->|
    |                            |                                  |
```

**Key Insight:** Your `PartitionReader` reads batches and returns checkpoints. The framework handles state serialization, message emission, and protocol compliance.

---

## Core Abstractions

### Feed (CDK-Provided Enum)

**Purpose:** Represents a data source - either a single Stream or Global (for CDC)

**Two Types:**

| Feed Type | Represents | Use Case |
|-----------|------------|----------|
| `Stream` | Individual table/stream | Cursor-based incremental, Full Refresh |
| `Global` | All streams together | CDC (change events span multiple tables) |

**Key Properties:**

```kotlin
sealed interface Feed {
    val id: FeedID
    val label: String
}

data class Stream(
    val name: String,
    val namespace: String?,
    val fields: List<Field>,
    val configuredSyncMode: ConfiguredSyncMode,  // FULL_REFRESH or INCREMENTAL
    val configuredPrimaryKey: List<List<String>>,
    val configuredCursor: List<String>?
) : Feed
```

### PartitionsCreatorFactory (Implement Only as Needed)

**Purpose:** Create `PartitionsCreator` instances for a feed

**When to Implement:**

Most connectors can use the stock JDBC toolkit implementations directly. Only implement a custom factory when you need:
- Custom partition decision logic
- Database-specific partition types (like CTID, XMIN)
- Special handling for CDC vs non-CDC modes

**Your Implementation (Pattern):**

```kotlin
@Singleton
class MySourceJdbcPartitionsCreatorFactory(
    private val config: MySourceConfiguration,
    private val operations: MySourceOperations,
) : PartitionsCreatorFactory {

    override fun make(
        feedBootstrap: FeedBootstrap
    ): PartitionsCreator {
        // For JDBC sources, typically delegate to toolkit
        return when (feedBootstrap.feed) {
            is Global -> CdcPartitionsCreator(...)  // CDC toolkit
            is Stream -> JdbcPartitionsCreator(...)  // JDBC toolkit
        }
    }
}
```

**Note:** For standard JDBC connectors, the toolkit provides a default factory that works out-of-the-box.

### PartitionsCreator (Toolkit or You Implement)

**Purpose:** Break down a feed into zero or more partitions for reading

**Lifecycle:**

```kotlin
interface PartitionsCreator {
    // Called multiple times in "rounds" until empty list returned
    suspend fun tryAcquireResources(): ResourceAcquisition
    suspend fun run(): List<PartitionReader>
    suspend fun releaseResources()
}
```

**Key Behavior:**
- **Round-based execution:** Called repeatedly, creates partitions each round
- **Returns empty list:** When done (no more partitions to create)
- **Resource management:** Acquires DB connections, releases after round completes
- **Concurrency control:** Toolkit implementations handle concurrent vs sequential

**JDBC Toolkit Implementations:**

| Implementation | Strategy | Use Case |
|----------------|----------|----------|
| `JdbcSequentialPartitionsCreator` | One partition per round | Serial reading with resumability |
| `JdbcConcurrentPartitionsCreator` | Multiple partitions per round | Parallel reading for large tables |

### Partition (Core Concept)

**Purpose:** Represents a discrete read operation targeting all or part of a table

A partition is the fundamental unit of work in the bulk extraction model. It encapsulates:
- **What to read:** Which portion of a table (entire table, PK range, cursor range, page range)
- **How to read it:** Query structure, parameters, ordering requirements
- **Progress tracking:** State values for checkpointing and resumability

**Concrete Examples:**

| Source Type | Partition Abstraction | Underlying Operation |
|-------------|----------------------|---------------------|
| **JDBC** | SELECT query with boundaries | `SELECT * FROM table WHERE pk >= ? AND pk < ? ORDER BY pk LIMIT ?` |
| **CDC** | Change event stream segment | Debezium consumer reading from LSN/binlog position |
| **API** | Paginated request | HTTP request with page token or offset |
| **File** | File chunk or byte range | Read from byte offset to byte offset |

For JDBC sources specifically, a partition translates directly to a SELECT query with:
- **WHERE clauses** defining boundaries (PK ranges, cursor ranges, CTID ranges)
- **ORDER BY clauses** ensuring consistent ordering
- **LIMIT clauses** enabling resumability (for resumable partitions)

The partition abstraction allows the CDK to:
- **Split work** across multiple concurrent operations
- **Track progress** independently for each unit of work
- **Resume** from any checkpoint if interrupted
- **Apply backpressure** by controlling partition creation rate

### PartitionReader (You Implement)

**Purpose:** Read records from a partition and return checkpoint state

**Your Implementation:**

```kotlin
class MyPartitionReader(
    private val partition: MyPartition,
    private val operations: MyOperations,
) : PartitionReader {

    override suspend fun run(): PartitionReadCheckpoint {
        // Acquire resources (connection, output consumer)
        val connection = resources.connection
        val consumer = resources.recordConsumer

        // Execute query
        val resultSet = connection.executeQuery(partition.query)

        var recordCount = 0L
        while (resultSet.next() && !isTimedOut()) {
            // Convert ResultSet row to record
            val record = operations.toRecord(resultSet)

            // Emit via consumer
            consumer.accept(record)
            recordCount++
        }

        // Return checkpoint
        return PartitionReadCheckpoint(
            opaqueStateValue = partition.currentState(),
            numRecords = recordCount
        )
    }
}
```

**Partition Types:**

- **Resumable:** Can be interrupted and resumed (tracks position in state)
- **Non-Resumable:** Must complete in one execution (no mid-partition checkpoints)
- **Time-Limited:** Subject to timeout (most partition readers)
- **Unlimited:** No timeout (CDC streaming)

### StateManager (CDK-Provided)

**Purpose:** Track sync progress for resumability

**Two Implementations:**

| StateManager | For Feeds | State Scope |
|--------------|-----------|-------------|
| `GlobalStateManager` | `Global` (CDC) | Single shared state + per-stream nested states |
| `NonGlobalStreamStateManager` | `Stream` (non-CDC) | Independent per-stream states |

**Key Methods:**

```kotlin
interface StateManager {
    // Update state after partition completes
    fun scoped(feed: Feed).set(
        opaqueStateValue: OpaqueStateValue,
        numRecords: Long
    )

    // Emit state messages for changed feeds
    fun checkpoint(): List<AirbyteStateMessage>
}
```

**State Format:**

- **OpaqueStateValue:** JsonNode, connector defines structure
- **Framework agnostic:** CDK doesn't parse state internals
- **Example structures:**
  - Cursor-based: `{"cursor_field": ["updated_at"], "cursor": "2024-01-15T10:30:00Z"}`
  - CDC: `{"lsn": "0/12345678"}`
  - CTID-based: `{"ctid": "(1000,1)", "filenode": "16384"}`

### Configuration (You Implement)

**Purpose:** Parse and validate user-provided configuration

**Two Parts:**

1. **Specification** - JSON Schema for UI form (POJO with Jackson annotations)
2. **Configuration** - Runtime config object implementing `SourceConfiguration`

**Specification Example:**

```kotlin
@JsonSchemaTitle("MySQL Source Configuration")
class MySqlSourceConfigurationSpecification {
    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    lateinit var host: String

    @JsonProperty("port")
    @JsonSchemaTitle("Port")
    var port: Int = 3306

    @JsonProperty("database")
    @JsonSchemaTitle("Database")
    lateinit var database: String

    @JsonProperty("replication_method")
    @JsonSchemaTitle("Replication Method")
    var replicationMethod: ReplicationMethodConfig? = null
}

sealed interface ReplicationMethodConfig {
    data object Standard : ReplicationMethodConfig  // Cursor-based
    data class CDC(...) : ReplicationMethodConfig   // Change Data Capture
}
```

**Configuration Example:**

```kotlin
data class MySqlSourceConfiguration(
    val realHost: String,
    val realPort: Int,
    val jdbcUrlFmt: String,
    val incrementalConfiguration: IncrementalConfiguration,
    override val maxConcurrency: Int,
    override val checkpointTargetInterval: Duration,
) : JdbcSourceConfiguration, CdcSourceConfiguration {

    override val global: Boolean =
        incrementalConfiguration is CdcIncrementalConfiguration

    fun jdbcUrl(): String = jdbcUrlFmt.format(realHost, realPort)
}
```

**Factory Pattern:**

```kotlin
@Singleton
class MySqlSourceConfigurationFactory :
    SourceConfigurationFactory<MySqlSourceConfigurationSpecification, MySqlSourceConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: MySqlSourceConfigurationSpecification
    ): MySqlSourceConfiguration {
        // Parse specification, validate, construct configuration
        return MySqlSourceConfiguration(...)
    }
}
```

### MetadataQuerier (You Implement)

**Purpose:** Discover database schema (tables, columns, primary keys)

**Key Methods:**

```kotlin
interface MetadataQuerier {
    // Discover available namespaces (schemas/databases)
    fun streamNamespaces(): List<String>

    // Discover streams in a namespace
    fun streamNames(streamNamespace: String?): List<String>

    // Get fields (columns) for a stream
    fun fields(
        streamName: String,
        streamNamespace: String?
    ): List<Field>

    // Get primary key columns
    fun primaryKey(
        streamName: String,
        streamNamespace: String?
    ): List<List<String>>

    // Optional: Extra validation checks
    fun extraChecks() {}
}
```

**JDBC Toolkit Pattern:**

```kotlin
@Singleton
class MySqlSourceMetadataQuerier(
    private val base: JdbcMetadataQuerier,  // Toolkit default
    private val config: MySqlSourceConfiguration,
) : MetadataQuerier by base {

    override fun extraChecks() {
        if (config.global) {
            // Validate CDC prerequisites
            validateBinlogEnabled()
            validateReplicationPrivileges()
        }
    }

    private fun validateBinlogEnabled() {
        val binlogEnabled = querySingleValue(
            "SHOW VARIABLES LIKE 'log_bin'",
            { rs -> rs.getString(2) }
        )
        if (binlogEnabled != "ON") {
            throw ConfigErrorException("Binary logging must be enabled for CDC")
        }
    }
}
```

---

## JDBC Toolkit Deep Dive

The JDBC toolkit (`airbyte-cdk/bulk/toolkits/extract-jdbc/`) provides stock implementations for relational database sources.

### JdbcPartition (Core Concept)

**Purpose:** Represents a unit of work for reading data from a stream

A partition defines:
- **What data to read:** Table/stream, columns, WHERE clause
- **How to read it:** Query parameters, ordering, limits
- **How to track progress:** State values for resumability

**Stock Partition Types:**

The toolkit provides standard partition types that cover most use cases:

| Partition Type | Use Case | Resumable | Query Pattern |
|----------------|----------|-----------|---------------|
| **SnapshotPartition** | Full refresh with PK | ✅ | `SELECT * FROM t WHERE pk > ? ORDER BY pk LIMIT ?` |
| **NonResumableSnapshotPartition** | Views, no PK tables | ❌ | `SELECT * FROM t` |
| **SnapshotWithCursorPartition** | Incremental cold start | ✅ | `SELECT * FROM t WHERE pk > ? AND cursor <= ? ORDER BY pk` |
| **CursorIncrementalPartition** | Incremental warm start | ✅ | `SELECT * FROM t WHERE cursor > ? AND cursor <= ? ORDER BY cursor` |

**Key Properties:**

```kotlin
interface JdbcPartition {
    val stream: Stream
    val completeState: OpaqueStateValue      // State when partition is done
    fun incompleteState(): OpaqueStateValue  // State for mid-partition checkpoint

    // Partition lifecycle
    fun isSplittable(): Boolean              // Can this be split for concurrency?
    fun isResumable(): Boolean               // Can this be interrupted and resumed?
}
```

**Resumable vs Non-Resumable:**

- **Resumable partitions** use LIMIT clauses with adaptive sizing, can checkpoint mid-read
- **Non-resumable partitions** must complete in one execution, suitable for small tables/views

**Splittable vs Non-Splittable:**

- **Splittable partitions** can be divided into multiple concurrent partitions (by PK ranges, page numbers, etc.)
- **Non-splittable partitions** must be read as a single unit

**Custom Partition Types (Only if Needed):**

Extend for database-specific features:

```kotlin
// Example: Postgres CTID-based partition
class CtidBasedSnapshotPartition(
    override val stream: Stream,
    val lowerBound: Ctid?,
    val upperBound: Ctid?,
    val filenode: Filenode
) : JdbcPartition {

    override fun isSplittable() = true
    override fun isResumable() = true

    override val completeState = OpaqueStateValue(
        JsonObject(
            "ctid" to upperBound.toString(),
            "filenode" to filenode.toString(),
            "completed" to true
        )
    )
}
```

### JdbcPartitionFactory (Stock Implementation Provided)

**Purpose:** Create and split partitions based on sync mode and state

**Stock Implementation:**

The JDBC toolkit provides a complete `JdbcPartitionFactory` implementation that handles standard partition creation logic. Most connectors use this implementation directly without customization.

**Key Responsibilities (Handled by Toolkit):**

1. **Partition Creation:** Automatically decides partition type based on:
   - Sync mode (FULL_REFRESH or INCREMENTAL)
   - State presence (cold start vs warm start)
   - Primary key availability
   - Cursor field configuration
   - CDC mode

2. **Partition Splitting:** Automatically breaks large partitions into smaller chunks for concurrent reading

3. **State Management:** Tracks per-stream state (cursor values, PK checkpoints, etc.)

**When to Extend:**

Only extend `JdbcPartitionFactory` if you need:
- **Custom partition types** (e.g., CTID-based for Postgres, XMIN for Postgres)
- **Database-specific split logic** (e.g., page-based splitting instead of PK-based)
- **Special state validation** (e.g., filenode tracking for Postgres)

**Extension Pattern (Only if Needed):**

```kotlin
@Singleton
class PostgresSourceJdbcPartitionFactory(
    override val sharedState: JdbcSharedState,
    val operations: PostgresSourceOperations,
    val config: PostgresSourceConfiguration,
) : JdbcPartitionFactory<JdbcSharedState, PostgresStreamState, PostgresJdbcPartition> {

    override fun create(streamFeedBootstrap: StreamFeedBootstrap): PostgresJdbcPartition? {
        val stream = streamFeedBootstrap.feed as Stream
        val state = streamFeedBootstrap.currentState

        // Cold start (no previous state)
        if (state == null) {
            return when {
                // Postgres-specific: prefer CTID-based partitioning if available
                hasFilenode(stream) ->
                    CtidBasedSnapshotPartition(stream, filenode)

                // Fall back to standard PK-based
                stream.configuredPrimaryKey.isNotEmpty() ->
                    PkBasedSnapshotPartition(stream)

                else -> NonResumableSnapshotPartition(stream)
            }
        }

        // Warm start: validate and resume
        return resumeFromState(stream, state)
    }

    override fun split(
        unsplitPartition: PostgresJdbcPartition,
        opaqueStateValues: List<OpaqueStateValue>
    ): List<PostgresJdbcPartition> {
        return when (unsplitPartition) {
            // CTID-based splitting (Postgres-specific)
            is CtidBasedPartition -> splitByPageNumbers(unsplitPartition)

            // Standard PK-based splitting (toolkit default)
            else -> super.split(unsplitPartition, opaqueStateValues)
        }
    }
}
```

**For Standard Databases:**

Most SQL databases (MySQL, MSSQL, etc.) work perfectly with the stock `JdbcPartitionFactory` and don't need any customization.

### Partition Decision Tree

**MySQL/MSSQL Pattern:**

```
Cold Start:
  FULL_REFRESH?
    Yes → Has PK?
            Yes → RfrSnapshotPartition (resumable)
            No → NonResumableSnapshotPartition
    No (INCREMENTAL) → CDC Mode?
            Yes → Has PK?
                    Yes → CdcSnapshotPartition
                    No → NonResumableSnapshotPartition (then CDC streaming)
            No (Cursor) → Has PK?
                    Yes → SnapshotWithCursorPartition (PK-based scan)
                    No → NonResumableSnapshotWithCursorPartition

Warm Start:
  Parse state type:
    "primary_key" → Continue PK-based scan or transition to cursor
    "cursor_based" → CursorIncrementalPartition
    CDC state → Resume CDC streaming
```

**Postgres Unique Pattern:**

```
Cold Start:
  FULL_REFRESH?
    Yes → Has Filenode? (Postgres 14+ feature)
            Yes → SplittableSnapshotPartition (CTID-based)
            No (view) → UnsplittableSnapshotPartition
    No (INCREMENTAL) → Mode?
            CDC → SplittableSnapshotPartition + CdcStreamingPartition
            XMIN → XminIncrementalPartition (unique to Postgres)
            Cursor → SplittableSnapshotWithCursorPartition

Warm Start:
  Parse state:
    Has "ctid"? → Resume CTID-based partition
    Has "xmin"? → Resume XMIN incremental
    Has "cursor"? → Resume cursor incremental
```

### JdbcPartitionsCreator (Toolkit-Provided)

**Purpose:** Execute partitions with sampling, splitting, and concurrency

**Two Implementations:**

| Creator | Strategy | Query Pattern |
|---------|----------|---------------|
| `JdbcSequentialPartitionsCreator` | One partition per round | Full table scan with LIMIT-based resumability |
| `JdbcConcurrentPartitionsCreator` | Multiple partitions in one round | Splits table by PK ranges for parallel reads |

**Sequential Creator Flow:**

```kotlin
JdbcSequentialPartitionsCreator.run() {
    1. Sample table (estimate row byte size)
    2. Calculate fetch size
    3. Create single partition reader (resumable)
    4. Return list of [partitionReader]
}

// Example query:
// SELECT * FROM table WHERE pk > ? ORDER BY pk LIMIT 10000
```

**Concurrent Creator Flow:**

```kotlin
JdbcConcurrentPartitionsCreator.run() {
    1. Ensure cursor upper bound known (if cursor-based)
    2. Sample table (row byte sizes)
    3. Calculate fetch size
    4. Estimate table size (from information_schema or pg_total_relation_size)
    5. Determine number of partitions needed
    6. Call factory.split(partition, numPartitions)
    7. Create partition reader for each split
    8. Return list of [reader1, reader2, ..., readerN]
}

// Example queries (3 partitions):
// Partition 1: SELECT * FROM table WHERE pk >= 1 AND pk < 1000
// Partition 2: SELECT * FROM table WHERE pk >= 1000 AND pk < 2000
// Partition 3: SELECT * FROM table WHERE pk >= 2000 AND pk <= 3000
```

**Sampling Logic:**

```kotlin
// Collect sample records to estimate row size
val sample: List<Pair<ObjectNode, Long>> = collectSample { record ->
    val estimatedByteSize = rowByteSizeEstimator.apply(record)
    record to estimatedByteSize
}

// Calculate optimal fetch size
val fetchSize = jdbcFetchSizeEstimator.apply(rowByteSizeSample)

// MySQL example: 1MB / avgRowByteSize = fetchSize
// Postgres example: similar, but considers block_size
```

**Splitting Algorithms:**

The toolkit provides intelligent splitting for different data types:

**Numeric Splitting (Long, Int, Double):**
```kotlin
// Linear interpolation
val step = (upperBound - lowerBound) / numPartitions
val boundaries = (1..numPartitions).map { i ->
    lowerBound + (step * i)
}
```

**String Splitting:**
```kotlin
// Unicode code point interpolation
// For "aaa" to "zzz" split into 3:
//   ["aaa", "i55", "r@@", "zzz"]

// For GUIDs: special GUID-aware splitting
```

**Temporal Splitting (OffsetDateTime, LocalDate):**
```kotlin
// Time-based interpolation
val totalSeconds = Duration.between(start, end).toSeconds()
val step = totalSeconds / numPartitions
```

**CTID Splitting (Postgres-specific):**
```kotlin
// Physical page-based splitting
data class Ctid(val page: Long, val tuple: Long)

// Split by page numbers
val totalPages = relationSize / blockSize
val pagesPerPartition = totalPages / numPartitions
```

### SelectQueryGenerator (You Implement)

**Purpose:** Generate SQL SELECT queries for your database dialect

**Key Methods:**

```kotlin
interface SelectQueryGenerator {
    // Generate query for a partition
    fun generate(partition: JdbcPartition<*>): SelectQuery

    // Column reference formatting
    fun sqlName(id: FieldOrMetaFieldID): String

    // Table reference formatting
    fun sqlName(stream: Stream): String
}
```

**Example Implementation (MySQL):**

```kotlin
class MySqlSourceOperations : SelectQueryGenerator {

    override fun generate(partition: MySqlSourceJdbcPartition): SelectQuery {
        val columns = partition.allColumns.joinToString { sqlName(it.id) }
        val table = sqlName(partition.stream)

        return when (partition) {
            is RfrSnapshotPartition -> SelectQuery(
                sql = """
                    SELECT $columns
                    FROM $table
                    WHERE ${pkCondition(partition)}
                    ORDER BY ${orderBy(partition)}
                    LIMIT ?
                """,
                parameters = listOf(
                    partition.lowerBound,
                    partition.limitValue
                )
            )

            is CursorIncrementalPartition -> SelectQuery(
                sql = """
                    SELECT $columns
                    FROM $table
                    WHERE ${cursorCondition(partition)}
                    ORDER BY ${sqlName(partition.cursor.id)}
                    LIMIT ?
                """,
                parameters = listOf(
                    partition.cursorLowerBound,
                    partition.cursorUpperBound,
                    partition.limitValue
                )
            )

            // ... other partition types
        }
    }

    override fun sqlName(id: FieldOrMetaFieldID): String = "`$id`"

    override fun sqlName(stream: Stream): String =
        "`${stream.namespace}`.`${stream.name}`"
}
```

**Database-Specific Syntax Examples:**

| Database | Quoting | Limit | Special Features |
|----------|---------|-------|------------------|
| MySQL | \`backticks\` | `LIMIT N` | `TABLESAMPLE` custom |
| MSSQL | `[brackets]` | `TOP N` | `TABLESAMPLE (10) PERCENT`, `NEWID()` |
| Postgres | `"quotes"` | `LIMIT N` | `CTID`, `XMIN`, `::tid`, `::text::bigint` |

**Postgres Special Cases:**

```kotlin
// CTID query
SELECT ctid::text, *
FROM "schema"."table"
WHERE ctid >= '(100,1)'::tid AND ctid <= '(200,0)'::tid

// XMIN query
SELECT *
FROM "schema"."table"
WHERE xmin::text::bigint >= 1000 AND xmin::text::bigint <= 2000

// HierarchyID (MSSQL)
SELECT [column].ToString() AS [column], ...
FROM [schema].[table]
```

### JdbcPartitionReader (Toolkit-Provided)

**Purpose:** Execute query and stream results

**Two Implementations:**

| Reader | Resumability | Use Case |
|--------|-------------|----------|
| `JdbcResumablePartitionReader` | Can be interrupted | Large tables, time-limited partitions |
| `JdbcNonResumablePartitionReader` | Must complete | Small tables, views, non-PK tables |

**Resumable Reader Flow:**

```kotlin
JdbcResumablePartitionReader.run() {
    var currentLimit = partition.initialLimit  // e.g., 10000
    var recordsRead = 0L

    while (true) {
        // Execute query with current limit
        val resultSet = executeQuery(partition.query(currentLimit))

        // Read rows
        var rowsThisBatch = 0
        while (resultSet.next()) {
            if (isTimedOut()) {
                // Interrupted! Return checkpoint with current state
                return PartitionReadCheckpoint(
                    opaqueStateValue = partition.incompleteState(lastRecord),
                    numRecords = recordsRead
                )
            }

            emitRecord(resultSet)
            rowsThisBatch++
            recordsRead++
        }

        // If fewer rows than limit, we're done
        if (rowsThisBatch < currentLimit) {
            return PartitionReadCheckpoint(
                opaqueStateValue = partition.completeState,
                numRecords = recordsRead
            )
        }

        // Otherwise, double limit and continue
        currentLimit = min(currentLimit * 2, maxLimit)
    }
}
```

**Adaptive Limit Algorithm:**

1. **Initial limit:** Small (e.g., 10,000 rows)
2. **On timeout:** Return checkpoint with last PK value
3. **On completion:** Double limit for next iteration
4. **Benefits:**
   - Fast resumability for interrupted syncs
   - Efficient for completed syncs (fewer round-trips)
   - Handles variable row sizes gracefully

---

## CDC Toolkit Deep Dive

The CDC toolkit (`airbyte-cdk/bulk/toolkits/extract-cdc/`) provides Debezium-based change data capture.

### CdcPartitionsCreator (Toolkit-Provided)

**Purpose:** Manage Debezium engine lifecycle for CDC streaming

**Flow:**

```kotlin
CdcPartitionsCreator.run() {
    // First call: return snapshot partitions (handled by JDBC)
    if (!snapshotComplete) {
        return emptyList()  // JDBC handles snapshot
    }

    // After snapshot: create CDC partition reader
    return listOf(CdcPartitionReader(
        debeziumEngine = createDebeziumEngine(),
        operations = yourCdcOperations
    ))
}
```

**Key Features:**

- **Debezium engine wrapper:** Manages embedded Debezium connector
- **State file management:** Persists Debezium offsets and schema history
- **Position tracking:** Converts Debezium offsets to Airbyte state
- **Snapshot coordination:** Waits for snapshot to complete before streaming

### CdcPartitionReader (Toolkit-Provided)

**Purpose:** Read change events from Debezium and emit Airbyte records

**Flow:**

```kotlin
CdcPartitionReader.run() {
    val engine = debeziumEngine.start()

    var recordsRead = 0L
    var lastPosition: CdcPosition? = null

    while (true) {
        val changeEvent = engine.poll(timeout)
        if (changeEvent == null) continue

        // Deserialize using your operations
        val (stream, record) = operations.deserializeRecord(changeEvent)

        // Emit record
        consumer.accept(stream, record)
        recordsRead++

        // Track position
        lastPosition = operations.position(changeEvent)

        // Checkpoint periodically
        if (shouldCheckpoint()) {
            return PartitionReadCheckpoint(
                opaqueStateValue = operations.serializeState(lastPosition),
                numRecords = recordsRead
            )
        }
    }
}
```

**Key Features:**

- **Unbounded execution:** CDC reader never completes (unlimited time)
- **Heartbeat handling:** Detects idle databases
- **Schema evolution:** Tracks Debezium schema history
- **Position comparison:** Validates saved state is still valid

### DebeziumOperations (You Implement)

**Purpose:** Database-specific CDC configuration and record handling

**Key Methods:**

```kotlin
interface CdcPartitionsCreatorDebeziumOperations {
    // Cold start: generate initial Debezium offset
    fun generateColdStartOffset(): DebeziumOffset

    // Warm start: deserialize and validate saved state
    fun deserializeState(opaqueStateValue: OpaqueStateValue): DebeziumWarmStartState

    // Serialize Debezium offset back to Airbyte state
    fun serializeState(
        offset: DebeziumOffset,
        schemaHistory: DebeziumSchemaHistory?
    ): OpaqueStateValue

    // Build Debezium properties
    fun debeziumProperties(): Properties
}

interface CdcPartitionReaderDebeziumOperations {
    // Extract CDC position from change event
    fun position(record: DebeziumRecord): CdcPosition

    // Deserialize change event to Airbyte record
    fun deserializeRecord(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
        stream: Stream
    ): DeserializedRecord
}
```

**MySQL CDC Example:**

```kotlin
class MySqlSourceDebeziumOperations :
    CdcPartitionsCreatorDebeziumOperations,
    CdcPartitionReaderDebeziumOperations {

    override fun generateColdStartOffset(): DebeziumOffset {
        // Query current binlog position
        val (fileName, position, gtidSet) = queryMasterStatus()

        // Create synthetic Debezium offset
        return DebeziumOffset(
            mapOf(
                "file" to fileName,
                "pos" to position.toString(),
                "gtid" to gtidSet
            )
        )
    }

    override fun deserializeState(
        opaqueStateValue: OpaqueStateValue
    ): DebeziumWarmStartState {
        val saved = parseSavedState(opaqueStateValue)

        // Validate binlog file still exists
        val availableFiles = queryBinaryLogFiles()
        if (!availableFiles.contains(saved.fileName)) {
            return DebeziumWarmStartState.Invalid(
                "Binlog file ${saved.fileName} no longer available"
            )
        }

        // Validate GTIDs still available
        if (!gtidSetStillAvailable(saved.gtidSet)) {
            return DebeziumWarmStartState.Invalid(
                "GTID set purged from server"
            )
        }

        return DebeziumWarmStartState.Valid(saved.offset, saved.schemaHistory)
    }

    override fun position(record: DebeziumRecord): MySqlCdcPosition {
        val source = record.source()
        return MySqlCdcPosition(
            fileName = source["file"].asText(),
            position = source["pos"].asLong()
        )
    }

    override fun deserializeRecord(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
        stream: Stream
    ): DeserializedRecord {
        val after = value.after
        val before = value.before
        val isDelete = after.isNull

        // Build record with CDC meta-fields
        val record = buildRecord(if (isDelete) before else after)
        record[CDC_LOG_FILE.id] = value.source()["file"].asText()
        record[CDC_LOG_POS.id] = value.source()["pos"].asLong()
        record[CDC_DELETED_AT.id] = if (isDelete) timestamp else null

        return DeserializedRecord(record, changes = emptyMap())
    }

    override fun debeziumProperties(): Properties {
        return Properties().apply {
            put("connector.class", "io.debezium.connector.mysql.MySqlConnector")
            put("database.hostname", config.host)
            put("database.port", config.port.toString())
            put("database.user", config.username)
            put("database.password", config.password)
            put("snapshot.mode", "when_needed")
            put("snapshot.locking.mode", "none")
            put("binary.handling.mode", "base64")
            put("decimal.handling.mode", "string")
            put("include.schema.changes", "false")
        }
    }
}
```

**MSSQL CDC Example:**

```kotlin
class MsSqlServerDebeziumOperations {

    override fun generateColdStartOffset(): DebeziumOffset {
        // Query current LSN
        val currentLsn = queryCurrentLsn()

        return DebeziumOffset(
            mapOf(
                "change_lsn" to currentLsn.toString(),
                "commit_lsn" to currentLsn.toString()
            )
        )
    }

    private fun queryCurrentLsn(): Lsn {
        val lsnHex = querySingleValue(
            "SELECT sys.fn_cdc_get_max_lsn() AS max_lsn",
            { rs -> rs.getBytes(1) }
        )
        return Lsn.valueOf(lsnHex)
    }

    override fun deserializeState(
        opaqueStateValue: OpaqueStateValue
    ): DebeziumWarmStartState {
        val saved = parseSavedState(opaqueStateValue)

        // Check if LSN still available
        val minLsn = queryMinLsn()
        if (saved.lsn < minLsn) {
            return when (config.invalidCdcCursorBehavior) {
                FAIL_SYNC -> DebeziumWarmStartState.Invalid(
                    "LSN ${saved.lsn} purged, min LSN is $minLsn"
                )
                RESET_SYNC -> DebeziumWarmStartState.ColdStart
            }
        }

        return DebeziumWarmStartState.Valid(saved.offset, saved.schemaHistory)
    }

    override fun deserializeRecord(...): DeserializedRecord {
        // Similar to MySQL, but with LSN fields
        record[CDC_LSN.id] = value.source()["change_lsn"]
        record[CDC_EVENT_SERIAL_NO.id] = value.source()["event_serial_no"]
        // ...
    }
}
```

**Postgres CDC Example:**

```kotlin
class PostgresSourceDebeziumOperations {

    override fun generateColdStartOffset(): DebeziumOffset {
        // Query current LSN
        val currentLsn = queryCurrentLsn()

        return DebeziumOffset(
            mapOf("lsn" to currentLsn.toString())
        )
    }

    private fun queryCurrentLsn(): Long {
        return querySingleValue(
            "SELECT pg_current_wal_lsn()",
            { rs -> parseLsn(rs.getString(1)) }
        )
    }

    override fun debeziumProperties(): Properties {
        return Properties().apply {
            put("connector.class", "io.debezium.connector.postgresql.PostgresConnector")
            put("plugin.name", "pgoutput")
            put("slot.name", config.replicationSlot)
            put("publication.name", config.publication)
            // ...
        }
    }
}
```

### CDC State Validation

**Critical Feature:** Validating that saved CDC position is still available

**Why Important:**

- **Binlog/WAL retention:** Logs can be purged by database
- **Recovery time:** Long downtimes may invalidate saved position
- **Graceful degradation:** Decide to fail or reset sync

**Validation Patterns:**

| Database | Position Type | Validation Query | Behavior on Invalid |
|----------|---------------|------------------|---------------------|
| MySQL | Binlog file + position | `SHOW BINARY LOGS` | Fail or full refresh |
| MSSQL | LSN | `sys.fn_cdc_get_min_lsn()` | Configurable: fail or reset |
| Postgres | LSN | Check replication slot lag | Fail or full refresh |

---

## What the CDK Provides

### Automatic Services

| Component | Responsibilities | Your Interaction |
|-----------|-----------------|------------------|
| **AirbyteSourceRunner** | CLI parsing, operation routing | None - runs automatically |
| **RootReader** | Feed orchestration, coroutine management | None - uses your factories |
| **FeedReader** | Per-feed reading, round management | None - calls your PartitionsCreator |
| **StateManager** | State tracking, checkpoint emission | Update via `scoped().set()` |
| **Output Handling** | Message serialization (RECORD, STATE, LOG, TRACE) | Emit via StreamRecordConsumer |
| **Resource Management** | Connection pooling, concurrency limits | Acquire via ResourceAcquisition |
| **Exception Classification** | ConfigError vs TransientError vs SystemError | Throw appropriate exceptions |

### JDBC Toolkit Provides

| Component | Responsibilities | Customization |
|-----------|-----------------|---------------|
| **JdbcMetadataQuerier** | Schema discovery via JDBC DatabaseMetaData | Override methods if needed |
| **JdbcPartitionsCreator** | Sequential/concurrent partition execution | Use as-is |
| **JdbcPartitionReader** | Query execution, ResultSet streaming | Use as-is |
| **JdbcFetchSizeEstimator** | Calculate optimal fetch size from samples | Use as-is |
| **Row byte size estimation** | Estimate memory usage per row | Override if special types |
| **Splitting algorithms** | PK range splitting for numeric/string/temporal | Use as-is or override |

### CDC Toolkit Provides

| Component | Responsibilities | Customization |
|-----------|-----------------|---------------|
| **CdcPartitionsCreator** | Debezium engine lifecycle | Implement your DebeziumOperations |
| **CdcPartitionReader** | CDC event consumption | Implement deserialization |
| **DebeziumPropertiesBuilder** | Build Debezium config | Override properties |
| **State file management** | Persist Debezium offsets | Use as-is |
| **Heartbeat handling** | Idle database detection | Configure interval |

---

## What You Implement

**Important:** The JDBC and CDC toolkits already provide stock implementations for all components. You only customize what's specific to your database dialect or unique features.

### Core Components (Customize as Needed)

| Component | Stock Implementation | When to Customize | Typical Effort |
|-----------|---------------------|-------------------|----------------|
| **Configuration** | Generic spec template | Always (database-specific params) | 150-250 LOC |
| **Metadata Querier** | `JdbcMetadataQuerier` | Only if non-standard catalog API | 0-200 LOC (usually extend base) |
| **Partition Factory** | Generic JDBC factory | Customize for PK vs CTID vs custom strategy | 100-500 LOC |
| **Partition Types** | Standard partitions provided | Only if unique partition requirements | 0-400 LOC (often reuse) |
| **Query Generator** | Default SQL generator | Customize for dialect (quoting, LIMIT syntax) | 100-300 LOC |
| **Field Type Mapper** | Common type mappings | Add database-specific types | 50-200 LOC |

### Optional Customizations

| Component | Stock Implementation | When to Customize | Typical Effort |
|-----------|---------------------|-------------------|----------------|
| **CDC Operations** | Debezium framework | Always if CDC needed (DB-specific) | 300-500 LOC |
| **Custom PartitionsCreator** | Sequential + Concurrent creators | Only for advanced partition strategies | 0-300 LOC |
| **Custom SelectQuerier** | Standard JDBC ResultSet handling | Only for special types or performance | 0-200 LOC |
| **State Migration** | N/A | Only when upgrading from legacy | 100-200 LOC |
| **Custom Field Types** | Common types (String, Int, etc.) | For DB-specific types (hstore, geometry) | 50-150 LOC per type |

### Typical Implementation Patterns

**Minimal Connector (Standard SQL Database):**
- Extend `JdbcMetadataQuerier` as-is
- Customize `Configuration` for connection params
- Override `Query Generator` for identifier quoting
- Add `Field Type Mapper` for any unique types
- **Total:** ~300-500 lines of code

**Standard Connector (MySQL-like):**
- All minimal components
- Customize `Partition Factory` for PK-based partitioning
- Add partition types for snapshot + incremental
- **Total:** ~800-1200 lines of code

**Advanced Connector (Postgres-like):**
- All standard components
- Add CTID/XMIN partition types
- Implement filenode tracking
- Add custom field types (arrays, geometric types)
- **Total:** ~1500-2500 lines of code

**With CDC:**
- Add any of above + CDC Operations
- **Additional:** ~300-500 lines of code

---

## Common Patterns Across Implementations

### Pattern 1: Partition Hierarchy

**All implementations follow:**

```
AbstractPartition
├── UnsplittablePartition (views, no PK)
│   └── NonResumableSnapshot
└── SplittablePartition (has PK or CTID)
    ├── RfrSnapshot
    ├── SnapshotWithCursor
    └── CursorIncremental
```

### Pattern 2: Two-Phase Incremental

**All cursor-based implementations:**

1. **Phase 1 (Snapshot):** Read entire table using PK ordering
   - Capture cursor upper bound at start
   - More efficient than cursor ORDER BY for full scan
   - State tracks PK position
2. **Phase 2 (Incremental):** Read only new/updated rows
   - Use cursor WHERE clause and ORDER BY
   - State tracks cursor value

### Pattern 3: State Versioning

**All implementations:**

```kotlin
data class StreamStateValue(
    val version: Int = 3,  // Increment on breaking changes
    // ... state fields
)
```

**Migration support:**

```kotlin
fun migrateState(oldState: JsonNode): StreamStateValue {
    return when (oldState["version"]?.asInt()) {
        null, 1 -> migrateFromV1(oldState)
        2 -> migrateFromV2(oldState)
        3 -> deserializeV3(oldState)
        else -> throw IllegalStateException("Unknown state version")
    }
}
```

---

## Database-Specific Features

### MySQL

**Unique Features:**

- **Binlog-based CDC:** `SHOW MASTER STATUS` for position
- **GTID support:** Global Transaction IDs for multi-source replication
- **Binlog validation:** Check if file exists, GTID set available

**Key Queries:**

```sql
-- Current binlog position
SHOW MASTER STATUS;
-- or (MySQL 8.4+)
SHOW BINARY LOG STATUS;

-- Available binlog files
SHOW BINARY LOGS;

-- GTID executed set
SELECT @@GLOBAL.GTID_EXECUTED;
```

**CDC Prerequisites:**

- `log_bin = ON`
- `binlog_format = ROW`
- `binlog_row_image = FULL`
- `REPLICATION CLIENT` privilege

### MSSQL

**Unique Features:**

- **LSN-based CDC:** `sys.fn_cdc_get_max_lsn()` for position
- **Clustered index preference:** Prefers clustered index over PK
- **SQL Server Agent:** Required for CDC (except Azure SQL)
- **Heartbeat sanitization:** Fixes Debezium heartbeat bug

**Key Queries:**

```sql
-- Current LSN
SELECT sys.fn_cdc_get_max_lsn() AS max_lsn;

-- Min LSN (retention)
SELECT sys.fn_cdc_get_min_lsn('dbo_table_CT') AS min_lsn;

-- Check CDC enabled
SELECT is_cdc_enabled FROM sys.databases WHERE name = 'mydb';

-- Get clustered index
SELECT c.name FROM sys.indexes i
JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE i.type_desc = 'CLUSTERED' AND i.object_id = OBJECT_ID('dbo.table');
```

**CDC Prerequisites:**

- SQL Server Agent running (except Azure SQL)
- Database CDC enabled: `EXEC sys.sp_cdc_enable_db`
- Table CDC enabled: `EXEC sys.sp_cdc_enable_table`

**SQL Dialect:**

- Use `TOP N` instead of `LIMIT`
- Use `[brackets]` for identifiers
- Use `TABLESAMPLE (10) PERCENT` for sampling
- Use `ORDER BY NEWID()` for randomization

### Postgres

**Unique Features:**

- **CTID-based partitioning:** Physical row addresses for splitting
- **XMIN-based incremental:** Transaction ID tracking
- **Filenode tracking:** Detect VACUUM FULL
- **pgoutput plugin:** Native logical replication for CDC
- **Rich type system:** hstore, geometric types, arrays

**Key Queries:**

```sql
-- Current LSN
SELECT pg_current_wal_lsn();

-- Current XMIN
SELECT CASE
    WHEN pg_is_in_recovery()
    THEN txid_snapshot_xmin(txid_current_snapshot())
    ELSE txid_current()
END AS current_xmin;

-- Filenode
SELECT pg_relation_filenode('schema.table'::regclass);

-- Table size
SELECT pg_total_relation_size('schema.table'::regclass);

-- Block size
SELECT current_setting('block_size')::int;

-- XMIN wraparound check
SELECT (txid_snapshot_xmin(txid_current_snapshot()) >> 32) AS num_wraparound;
```

**CDC Prerequisites:**

- `wal_level = logical`
- Replication slot created: `SELECT pg_create_logical_replication_slot('slot_name', 'pgoutput')`
- Publication created: `CREATE PUBLICATION pub_name FOR ALL TABLES`
- `REPLICATION` privilege

**CTID Queries:**

```sql
-- CTID-based partition
SELECT ctid::text, * FROM table
WHERE ctid >= '(100,1)'::tid AND ctid <= '(200,0)'::tid;

-- Max CTID (not reliable for upper bound, use relation size instead)
SELECT ctid FROM table ORDER BY ctid DESC LIMIT 1;
```

**XMIN Queries:**

```sql
-- XMIN-based incremental
SELECT * FROM table
WHERE xmin::text::bigint >= 1000 AND xmin::text::bigint <= 2000;
```

---

## Implementation Checklist

### Phase 1: Foundation (Check + Discover)

- [ ] Configuration spec (JSON schema POJO)
- [ ] Configuration factory
- [ ] Metadata querier (or extend JdbcMetadataQuerier)
- [ ] Field type mapper (database types → FieldTypes)
- [ ] Check operation (connection validation)
- [ ] Exception classifier

### Phase 2: Full Refresh

- [ ] Query generator (SELECT queries)
- [ ] Partition factory (decision logic)
- [ ] Partition types (NonResumableSnapshot, RfrSnapshot)
- [ ] Stream state structure
- [ ] Integration test (full refresh mode)

### Phase 3: Incremental (Cursor-Based)

- [ ] Cursor partition types (SnapshotWithCursor, CursorIncremental)
- [ ] Cursor upper bound queries
- [ ] State transitions (PK phase → cursor phase)
- [ ] Integration test (incremental mode)

### Phase 4: CDC (Optional)

- [ ] Debezium operations (cold start, warm start, deserialize)
- [ ] CDC position type
- [ ] CDC meta-fields
- [ ] State validation (LSN/binlog availability)
- [ ] Integration test (CDC mode)

### Phase 5: Optimization

- [ ] Concurrent partitioning (if large tables)
- [ ] Partition splitting logic
- [ ] Sampling and fetch size calculation
- [ ] Performance tuning (indexes, query optimization)

### Phase 6: Polish

- [ ] Comprehensive error handling
- [ ] State migration (if upgrading from legacy)
- [ ] Logging and observability
- [ ] Edge case handling (views, very large tables, etc.)
- [ ] Documentation

---

## Comparison with Destination Bulk CDK

**Similarities:**

- Both use Micronaut framework
- Both use coroutines for concurrency
- Both have state management
- Both have toolkit pattern (JDBC, CDC)
- Both handle protocol compliance automatically

**Key Differences:**

| Aspect | Extract (Source) | Load (Destination) |
|--------|-----------------|-------------------|
| **Core abstraction** | PartitionReader | StreamLoader |
| **Data direction** | Database → Airbyte | Airbyte → Database |
| **Concurrency** | Read partitions in parallel | Write streams in parallel |
| **State** | OpaqueStateValue per stream | Internal state per stream |
| **Toolkit focus** | Query generation, sampling | SQL generation, table lifecycle |
| **Resumability** | Checkpoint on timeout | Atomic finalization (MERGE/SWAP) |
| **Key challenge** | Splitting large tables | Managing temp tables |
| **CDC** | Debezium consumer | N/A |
| **Schema evolution** | Discovery only | Automatic ALTER TABLE |

---

## Summary

**The Development Model:**

The Extract Bulk CDK uses a **toolkit-first approach**. The JDBC and CDC toolkits provide stock implementations. You extend and customize only what's specific to your database.

**What the CDK Core provides (automatic):**

- ✅ Source Runner (CLI, operation dispatch)
- ✅ RootReader (feed orchestration, coroutines)
- ✅ FeedReader (partition execution, state management)
- ✅ StateManager (checkpoint tracking, emission)
- ✅ Output handling (message serialization)
- ✅ Resource management (connections, concurrency limits)
- ✅ Exception handling framework

**What JDBC Toolkit provides (stock implementations):**

- ✅ JdbcMetadataQuerier (JDBC-based discovery)
- ✅ JdbcPartitionsCreator (sequential/concurrent execution)
- ✅ JdbcPartitionReader (query execution, ResultSet streaming)
- ✅ Standard partition types (snapshot, cursor, PK-based)
- ✅ Sampling and fetch size calculation
- ✅ Partition splitting algorithms (numeric, string, temporal)
- ✅ Default query generator (standard SQL)
- ✅ Common field types (String, Int, Long, Boolean, etc.)

**What CDC Toolkit provides (stock implementations):**

- ✅ CdcPartitionsCreator (Debezium engine lifecycle)
- ✅ CdcPartitionReader (CDC event consumption)
- ✅ State file management (Debezium offsets, schema history)
- ✅ Heartbeat handling
- ✅ Debezium configuration framework

**What you customize (only as needed):**

- 🔧 Configuration (always - your database connection params)
- 🔧 Query Generator (customize for SQL dialect: quoting, LIMIT syntax)
- 🔧 Field Type Mapper (add database-specific types)
- 🔧 Metadata Querier (extend if non-standard catalog API)
- 🔧 Partition Factory (customize if special partitioning strategy)
- 🔧 Partition Types (add if unique requirements like CTID, XMIN)
- 🔧 CDC Operations (implement if CDC support needed)
- 🔧 Custom Field Types (for hstore, geometry, arrays, etc.)

**Out-of-the-box capabilities:**

- ✅ Full Refresh (with resumability if PK exists)
- ✅ Incremental cursor-based (two-phase: snapshot → incremental)
- ✅ CDC streaming (with Debezium)
- ✅ State tracking and resumability
- ✅ Automatic error classification
- ✅ Concurrent reads for large tables
- ✅ Adaptive fetch sizing
- ✅ PK-based partition splitting

**Typical implementation effort:**

- **Minimal connector** (standard SQL, use all defaults): ~300-500 LOC, 2-3 days
- **Standard connector** (MySQL-like, customize partitioning): ~800-1200 LOC, 1 week
- **Advanced connector** (Postgres-like, custom types + partitions): ~1500-2500 LOC, 1-2 weeks
- **With CDC** (add to any above): +300-500 LOC, +3-5 days
