# Source Connector CDK Architecture

**Summary:** The Airbyte Source CDK provides a framework for building JDBC-based source connectors. You implement database-specific components (Source Operations, Metadata Querier, Configuration, State Management). The CDK handles stream orchestration, message serialization, state checkpointing, and the Airbyte protocol. Result: Implement ~6 custom components, get full refresh, incremental, and CDC sync modes.

---

## Architecture Overview

### Entry Point to Data Extraction

```
main()
  -> AirbyteSourceRunner.run(*args)  [Kotlin/Bulk CDK]
  or
  -> IntegrationRunner.run(source)   [Java/Legacy CDK]
    -> Parse CLI (--spec, --check, --discover, --read)
    -> Create application context
    -> Execute operation
```

**Read Operation Flow (Bulk CDK - MySQL style):**
```
Source.read()
  -> PartitionFactory.create(stream, state)
    1. Determine sync mode (full refresh, incremental, CDC)
    2. Create appropriate Partition(s)
  -> For each Partition:
    -> Partition.read() yields records
    -> Transform to AirbyteRecordMessage
    -> Emit STATE at checkpoints
```

**Read Operation Flow (Legacy CDK - Postgres style):**
```
AbstractJdbcSource.read()
  -> discoverInternal()              [Get catalog]
  -> For each stream:
    1. Select handler based on sync mode
    2. Handler creates iterator
    3. Iterator yields records
    4. Transform via SourceOperations
    5. Emit STATE at checkpoints
```

### Data Flow Pipeline

**Database -> stdout:**

```
Database                    Connector Pipeline                  Airbyte Platform
    |                              |                                   |
    |<-- SELECT query -------------|                                   |
    |                              |                                   |
    |-- ResultSet --------------->|                                   |
    |                           Parse JDBC types                       |
    |                           Convert to AirbyteValue                |
    |                           Build AirbyteRecordMessage             |
    |                              |                                   |
    |                         [Buffering]                              |
    |                              |                                   |
    |                      Emit RECORD message ----------------------->|
    |                              |                                   |
    |                         [Checkpoint]                             |
    |                              |                                   |
    |                      Emit STATE message ------------------------>|
    |                              |                                   |
```

**Key Insight:** Your `SourceOperations` converts JDBC ResultSet to Airbyte messages. The framework handles protocol serialization and state management.

---

## Core Abstractions

### Source (Entry Point)

**Purpose:** Main connector class implementing Airbyte Source interface

**Key Methods:**

```kotlin
interface Source {
    fun spec(): ConnectorSpecification
    fun check(config: JsonNode): AirbyteConnectionStatus
    fun discover(config: JsonNode): AirbyteCatalog
    fun read(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        state: JsonNode?
    ): Iterator<AirbyteMessage>
}
```

**Legacy CDK Pattern (Postgres):**
```java
public class PostgresSource extends AbstractJdbcSource<PostgresType>
    implements Source {

    public static void main(String[] args) {
        new IntegrationRunner(new PostgresSource()).run(args);
    }

    @Override
    public JsonNode toDatabaseConfig(JsonNode config) {
        // Convert Airbyte config to JDBC properties
    }
}
```

**Bulk CDK Pattern (MySQL):**
```kotlin
class MySqlSource {
    companion object {
        @JvmStatic
        fun main(args: Array<String>) {
            AirbyteSourceRunner.run(*args)
        }
    }
}
```

### Source Operations (You Implement)

**Purpose:** Database-specific type conversions and query generation

**Key Responsibilities:**

```kotlin
interface SourceOperations<ResultSetType, DatabaseType> {
    // Map database type to Airbyte JSON Schema type
    fun getAirbyteType(databaseType: DatabaseType): JsonSchemaType

    // Extract value from ResultSet and set on JSON node
    fun setJsonField(record: ObjectNode, rs: ResultSetType, columnName: String)

    // Convert database type to string representation
    fun toAirbyteValue(value: Any?, type: DatabaseType): AirbyteValue
}
```

**Example (Postgres):**
```java
public class PostgresSourceOperations
    extends AbstractJdbcCompatibleSourceOperations<PostgresType> {

    @Override
    public void setJsonField(ObjectNode o, ResultSet rs, String name) {
        PostgresType type = getColumnType(rs, name);
        switch (type) {
            case BOOLEAN -> o.put(name, rs.getBoolean(name));
            case INTEGER -> o.put(name, rs.getInt(name));
            case BIGINT -> o.put(name, rs.getLong(name));
            case JSONB -> o.set(name, parseJson(rs.getString(name)));
            case TIMESTAMP_WITH_TIMEZONE ->
                o.put(name, formatTimestamp(rs.getTimestamp(name)));
            // ... other types
        }
    }
}
```

### Metadata Querier (You Implement)

**Purpose:** Schema discovery from database catalog

**Key Methods:**

```kotlin
interface MetadataQuerier {
    // List available tables
    fun listTables(): List<TableName>

    // Get columns for a table
    fun getColumns(table: TableName): List<Column>

    // Get primary key columns
    fun getPrimaryKeys(table: TableName): List<String>

    // CDC-specific: validate replication prerequisites
    fun validateCdcPrerequisites()  // Optional
}
```

**Example (MySQL):**
```kotlin
class MySqlSourceMetadataQuerier(
    private val base: JdbcMetadataQuerier,
    private val config: MySqlSourceConfiguration,
) : MetadataQuerier {

    override fun getColumns(table: TableName): List<Column> {
        val columns = base.getColumns(table)
        // Add CDC meta-fields if CDC enabled
        if (config.isCdcEnabled()) {
            return columns + cdcMetaFields()
        }
        return columns
    }

    override fun validateCdcPrerequisites() {
        // Check binlog enabled, user has REPLICATION privileges, etc.
    }
}
```

### Configuration (You Implement)

**Purpose:** Parse and validate user-provided configuration

**Two Parts:**

1. **Specification** - JSON Schema for UI form
2. **Configuration** - Runtime config object

**Specification Example:**
```kotlin
@JsonSchemaTitle("MySQL Source Configuration")
class MySqlSourceConfigurationSpecification : ConfigurationSpecification {
    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    lateinit var host: String

    @JsonProperty("port")
    @JsonSchemaTitle("Port")
    var port: Int = 3306

    @JsonProperty("database")
    @JsonSchemaTitle("Database")
    lateinit var database: String

    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    lateinit var username: String

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonSchemaFormat("password")
    var password: String? = null

    @JsonProperty("replication_method")
    @JsonSchemaTitle("Replication Method")
    var replicationMethod: ReplicationMethod = ReplicationMethod.STANDARD
}

enum class ReplicationMethod {
    STANDARD,  // Cursor-based incremental
    CDC        // Change Data Capture
}
```

**Configuration Example:**
```kotlin
data class MySqlSourceConfiguration(
    override val host: String,
    override val port: Int,
    override val database: String,
    override val username: String,
    override val password: String?,
    val sslMode: SslMode,
    val replicationMethod: ReplicationMethod,
    val cursorConfig: CursorConfig?,
    val cdcConfig: CdcConfig?,
) : JdbcSourceConfiguration, CdcSourceConfiguration {

    fun isCdcEnabled(): Boolean = replicationMethod == ReplicationMethod.CDC

    override fun jdbcUrl(): String =
        "jdbc:mysql://$host:$port/$database"
}
```

### Partition Factory (Bulk CDK)

**Purpose:** Create data partitions based on sync mode and state

**Key Logic:**

```kotlin
class MySqlSourceJdbcPartitionFactory(
    private val config: MySqlSourceConfiguration,
    private val operations: MySqlSourceOperations,
) : JdbcPartitionFactory {

    override fun create(
        stream: Stream,
        state: StreamState?,
    ): List<Partition> {
        return when {
            // CDC mode
            config.isCdcEnabled() -> createCdcPartitions(stream, state)

            // Incremental with state (warm start)
            state != null && stream.syncMode == INCREMENTAL ->
                listOf(CursorBasedPartition(stream, state, operations))

            // Incremental without state (cold start) or Full Refresh
            else -> listOf(FullRefreshPartition(stream, operations))
        }
    }

    private fun createCdcPartitions(stream: Stream, state: StreamState?): List<Partition> {
        return if (state == null) {
            // Initial snapshot + CDC streaming
            listOf(
                CdcSnapshotPartition(stream),
                CdcStreamingPartition(stream)
            )
        } else {
            // Resume CDC streaming from saved position
            listOf(CdcStreamingPartition(stream, state))
        }
    }
}
```

### State Management (You Implement)

**Purpose:** Track sync progress for resumability

**Types of State:**

1. **Cursor-Based State** - Track last cursor value per stream
2. **CDC State** - Track replication position (LSN, binlog, GTID)
3. **CTID State** - Track physical row position (Postgres-specific)

**Cursor State Example:**
```kotlin
data class MySqlSourceJdbcStreamStateValue(
    val cursorField: String,
    val cursorValue: String?,
    val stateType: StateType,  // PRIMARY_KEY or CURSOR_BASED
    val pkName: String?,
    val pkValue: String?,
)

enum class StateType {
    PRIMARY_KEY,    // Initial snapshot using PK ranges
    CURSOR_BASED,   // Incremental using cursor column
}
```

**CDC State Example:**
```kotlin
data class MySqlSourceCdcPosition(
    val fileName: String,   // e.g., "mysql-bin.000003"
    val position: Long,     // e.g., 154
    val gtidSet: String?,   // e.g., "uuid:1-5" (if GTID enabled)
)
```

---

## Sync Mode Implementations

### Full Refresh

**Behavior:** Read entire table from start

**Query Pattern:**
```sql
SELECT * FROM schema.table ORDER BY pk_columns
```

**Chunking Strategies:**

1. **Simple Full Scan** - Single query, all rows
2. **PK-Based Chunking** - Split by primary key ranges
3. **CTID-Based** (Postgres) - Split by physical row location

**CTID Example (Postgres):**
```java
public class CtidStateManager implements SourceStateMessageProducer<AirbyteMessageWithCtid> {

    public String getCtidQuery(TableName table, Ctid lastCtid) {
        return String.format(
            "SELECT ctid, * FROM %s WHERE ctid > '%s' ORDER BY ctid LIMIT %d",
            table.fullName(), lastCtid.toString(), CHUNK_SIZE
        );
    }
}
```

### Incremental (Cursor-Based)

**Behavior:** Read rows where cursor > last_saved_value

**Query Pattern:**
```sql
SELECT * FROM schema.table
WHERE cursor_column > :last_cursor_value
ORDER BY cursor_column ASC
```

**State Tracking:**
```kotlin
// After processing batch, update state
fun emitState(lastRecord: Record): AirbyteStateMessage {
    return AirbyteStateMessage(
        type = STREAM,
        stream = StreamState(
            streamDescriptor = stream.descriptor,
            streamState = JsonObject(
                "cursor_field" to cursorField,
                "cursor" to lastRecord.get(cursorField)
            )
        )
    )
}
```

**Cursor Types Supported:**
- Timestamp columns (`updated_at`, `created_at`)
- Auto-increment integers (`id`)
- Composite cursors (multiple columns)

### CDC (Change Data Capture)

**Behavior:** Stream changes from database replication log

**Two Phases:**

1. **Initial Snapshot** - Full table read (same as full refresh)
2. **Streaming** - Read changes from replication log

**Debezium Integration:**

```kotlin
class MySqlSourceDebeziumOperations : CdcPartitionsCreatorDebeziumOperations {

    override fun position(record: DebeziumRecord): CdcPosition {
        val source = record.source()
        return MySqlSourceCdcPosition(
            fileName = source.getString("file"),
            position = source.getLong("pos"),
            gtidSet = source.getString("gtid")
        )
    }

    override fun coldStartProperties(): Properties {
        return Properties().apply {
            put("connector.class", "io.debezium.connector.mysql.MySqlConnector")
            put("database.hostname", config.host)
            put("database.port", config.port.toString())
            put("database.user", config.username)
            put("database.password", config.password)
            put("database.server.id", generateServerId())
            put("snapshot.mode", "initial")
        }
    }
}
```

**CDC Meta-Fields:**
```kotlin
enum class MySqlSourceCdcMetaFields(val fieldName: String, val type: FieldType) {
    CDC_CURSOR("_ab_cdc_cursor", IntegerType),
    CDC_LOG_FILE("_ab_cdc_log_file", StringType),
    CDC_LOG_POS("_ab_cdc_log_pos", IntegerType),
}
```

---

## What the CDK Provides

### Automatic Services

| Component | Responsibilities | Your Interaction |
|-----------|-----------------|------------------|
| **Source Runner** | CLI parsing, operation dispatch | None - runs automatically |
| **Protocol Handling** | Message serialization (RECORD, STATE, LOG) | Return AirbyteMessage |
| **JDBC Framework** | Connection pooling, query execution | Configure DataSource |
| **Debezium Integration** | CDC engine, position tracking | Implement operations interface |
| **State Checkpointing** | Periodic state emission | Return state values |

### Base Classes

| Base Class | Purpose | Extend When |
|------------|---------|-------------|
| `AbstractJdbcSource<T>` | JDBC source with type system | Legacy Java connector |
| `AbstractJdbcCompatibleSourceOperations<T>` | Type conversion base | Legacy Java connector |
| `JdbcSourceConfiguration` | JDBC config interface | Bulk CDK connector |
| `CdcSourceConfiguration` | CDC config interface | CDC-enabled connector |
| `JdbcPartitionFactory` | Partition creation | Bulk CDK connector |

---

## What You Implement

### Core Custom Components

| Component | Effort | Purpose | Lines of Code |
|-----------|--------|---------|---------------|
| **Source Operations** | High | Type mapping, value extraction | 200-400 |
| **Metadata Querier** | Medium | Schema discovery | 100-200 |
| **Configuration** | Medium | Config spec + factory | 150-250 |
| **State Management** | Medium | Cursor/CDC state tracking | 100-200 |
| **Exception Handler** | Low | Error classification | 50-100 |
| **CDC Operations** | High | Debezium integration (if CDC) | 200-300 |

### Supporting Components

| Component | Effort | Purpose | Lines of Code |
|-----------|--------|---------|---------------|
| **Database Type Enum** | Low | Map DB types to enum | 50-100 |
| **Query Utils** | Low | Query building helpers | 50-100 |
| **Partition Factory** | Medium | Sync mode selection | 100-150 |

**Total:** ~10 components, ~1000-1500 lines of code (non-CDC)
**With CDC:** ~15 components, ~1500-2500 lines of code

---

## Sync Mode Selection Logic

### Decision Tree

```
User selects sync mode
         |
         v
    Full Refresh? ----YES----> FullRefreshPartition
         |                          |
         NO                    Read all rows
         |                     No state saved
         v
    CDC Enabled? -----YES----> CdcPartitions
         |                          |
         NO                    Debezium streaming
         |                     Track LSN/binlog
         v
    Has Cursor? -----YES----> CursorBasedPartition
         |                          |
         NO                    WHERE cursor > ?
         |                     Track cursor value
         v
    FullRefreshPartition
    (Incremental without cursor = full refresh)
```

### Partition Types

| Partition Type | Sync Mode | Query Pattern | State |
|----------------|-----------|---------------|-------|
| `FullRefreshPartition` | Full Refresh | `SELECT * FROM t` | None |
| `CursorBasedPartition` | Incremental | `SELECT * FROM t WHERE c > ?` | Cursor value |
| `CtidPartition` | Full Refresh (Postgres) | `SELECT * FROM t WHERE ctid > ?` | CTID position |
| `CdcSnapshotPartition` | CDC (initial) | `SELECT * FROM t` | None |
| `CdcStreamingPartition` | CDC (ongoing) | Debezium consumer | CDC position |

---

## State Management Patterns

### Per-Stream State (Cursor-Based)

```json
{
  "type": "STREAM",
  "stream": {
    "stream_descriptor": {
      "name": "users",
      "namespace": "public"
    },
    "stream_state": {
      "cursor_field": ["updated_at"],
      "cursor": "2024-01-15T10:30:00Z"
    }
  }
}
```

### Global State (CDC)

```json
{
  "type": "GLOBAL",
  "global": {
    "shared_state": {
      "cdc_state": {
        "file": "mysql-bin.000003",
        "pos": 154,
        "gtid": "uuid:1-5"
      }
    },
    "stream_states": [
      {
        "stream_descriptor": {"name": "users", "namespace": "mydb"},
        "stream_state": {"pk_checkpoint": {"id": 1000}}
      }
    ]
  }
}
```

### State Emission Timing

```
Records read from partition
         |
         v
    Batch complete? (e.g., 10000 records)
         |
        YES -----> Emit STATE with current position
         |
         v
    Continue reading
         |
         v
    Partition complete?
         |
        YES -----> Emit final STATE
```

---

## CDC Architecture

### Debezium Integration Flow

```
Database Replication Log
         |
         v
    Debezium Connector
    (MySQL/Postgres/etc)
         |
         v
    DebeziumRecord
    (change event)
         |
         v
    Your CdcOperations.position(record)
    (extract position)
         |
         v
    Your CdcOperations.toAirbyteMessage(record)
    (convert to Airbyte format)
         |
         v
    AirbyteRecordMessage
    + AirbyteStateMessage (periodically)
```

### CDC State Types

**Postgres (LSN-based):**
```kotlin
data class PostgresCdcPosition(
    val lsn: Long,              // Log Sequence Number
    val transactionId: Long?,   // Optional txn ID
)
```

**MySQL (Binlog-based):**
```kotlin
data class MySqlCdcPosition(
    val fileName: String,       // mysql-bin.000003
    val position: Long,         // 154
    val gtidSet: String?,       // GTID set if enabled
)
```

### CDC Meta-Fields Added to Records

| Field | Purpose |
|-------|---------|
| `_ab_cdc_cursor` | Deduplication cursor (position as integer) |
| `_ab_cdc_deleted_at` | Deletion timestamp (for DELETE events) |
| `_ab_cdc_log_file` | Binlog file (MySQL) |
| `_ab_cdc_log_pos` | Position in log file |
| `_ab_cdc_lsn` | Log Sequence Number (Postgres) |

---

## Error Handling

### Exception Classification

| Exception Type | When to Use | Platform Action |
|----------------|-------------|-----------------|
| `ConfigErrorException` | Invalid config, bad credentials, missing permissions | NO RETRY - notify user |
| `TransientErrorException` | Network timeout, temp DB unavailable | RETRY with backoff |
| `SystemErrorException` | Internal errors, bugs | LIMITED RETRY |

### Error Handler Pattern

```kotlin
class MySqlSourceExceptionHandler : ExceptionHandler {
    override fun handle(e: Exception): AirbyteException {
        return when {
            e.message?.contains("Access denied") == true ->
                ConfigErrorException(
                    "Access denied. Check username and password.",
                    e
                )

            e.message?.contains("Communications link failure") == true ->
                TransientErrorException(
                    "Connection lost. Will retry.",
                    e
                )

            e is SQLException && e.sqlState?.startsWith("08") == true ->
                TransientErrorException(
                    "Connection error: ${e.message}",
                    e
                )

            else -> SystemErrorException("Unexpected error", e)
        }
    }
}
```

---

## The Four Operations

Every source connector must support four operations:

| Operation | Trigger | Purpose | Output |
|-----------|---------|---------|--------|
| `--spec` | CLI flag | Return connector capabilities | SPEC message |
| `--check` | CLI flag | Validate connection | CONNECTION_STATUS |
| `--discover` | CLI flag | Return available streams | CATALOG |
| `--read` | CLI flag | Extract data | RECORD + STATE messages |

### Spec Operation

Returns JSON Schema defining configuration options.

### Check Operation

Validates connection by:
1. Establishing database connection
2. Executing simple query (`SELECT 1`)
3. Optionally validating CDC prerequisites

### Discover Operation

Returns catalog by:
1. Querying schema catalog for tables
2. Querying columns for each table
3. Identifying primary keys
4. Building AirbyteCatalog with streams

### Read Operation

Extracts data by:
1. Parsing configured catalog
2. Creating partitions per stream
3. Executing queries and yielding records
4. Emitting state at checkpoints

---

## Performance Considerations

### Memory Management

- **Streaming ResultSets:** Set `fetchSize` to avoid loading entire table
- **Batch Processing:** Process records in batches, emit state periodically
- **Connection Pooling:** Reuse connections for multiple streams

```kotlin
// Enable streaming results
statement.fetchSize = 1000  // Fetch 1000 rows at a time

// Process in batches
var recordCount = 0
while (resultSet.next()) {
    emit(toAirbyteRecord(resultSet))
    recordCount++
    if (recordCount % 10000 == 0) {
        emitState(currentPosition)
    }
}
```

### Parallelism

- **Multiple Streams:** Can read streams in parallel
- **Partitioned Tables:** Split large tables by PK ranges
- **CDC + Snapshot:** Snapshot and streaming can overlap

### Query Optimization

- **Indexed Cursors:** Ensure cursor columns are indexed
- **Projection:** Only SELECT needed columns
- **Ordered Reads:** ORDER BY cursor for consistent pagination

---

## Implementation Checklist

### Phase 1: Basic Connectivity
- [ ] Configuration spec and factory
- [ ] JDBC connection setup
- [ ] Check operation (connection test)
- [ ] Exception handler

### Phase 2: Schema Discovery
- [ ] Metadata querier (tables, columns, PKs)
- [ ] Database type enum
- [ ] Discover operation

### Phase 3: Full Refresh
- [ ] Source operations (type mapping)
- [ ] Full refresh partition
- [ ] Read operation (basic)

### Phase 4: Incremental
- [ ] Cursor-based partition
- [ ] State management (cursor tracking)
- [ ] State emission

### Phase 5: CDC (Optional)
- [ ] Debezium operations
- [ ] CDC state management
- [ ] CDC meta-fields
- [ ] Snapshot + streaming coordination

### Phase 6: Polish
- [ ] Comprehensive error handling
- [ ] Logging
- [ ] Performance tuning
- [ ] Testing (unit + integration)

---

## Summary

**What you must provide:**
- [ ] Configuration (spec + factory)
- [ ] Source Operations (type mapping)
- [ ] Metadata Querier (schema discovery)
- [ ] State Management (cursor/CDC tracking)
- [ ] Exception Handler
- [ ] Database Type Enum
- [ ] CDC Operations (if CDC enabled)

**What the CDK provides:**
- [ ] Source Runner (CLI, operation dispatch)
- [ ] Protocol handling (message serialization)
- [ ] JDBC framework (connection pooling)
- [ ] Debezium integration (CDC engine)
- [ ] State checkpointing

**Result:**
- [ ] Full Refresh works
- [ ] Incremental (cursor-based) works
- [ ] CDC works (if implemented)
- [ ] State is tracked for resumability
- [ ] Errors are properly classified
