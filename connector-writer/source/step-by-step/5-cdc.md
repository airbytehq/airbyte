# CDC: Change Data Capture with Debezium

**Prerequisites:** Complete [4-incremental.md](./4-incremental.md)

**Summary:** Implement Change Data Capture (CDC) using Debezium. After this guide, your connector can capture inserts, updates, and deletes by reading the database's replication log.

---

## CDC Phase 1: Understanding CDC

**Goal:** Understand how CDC works with Debezium

### How CDC Works

1. **Database writes changes to replication log**
   - MySQL: Binary Log (binlog)
   - PostgreSQL: Write-Ahead Log (WAL)
   - SQL Server: Transaction Log

2. **Debezium reads replication log**
   - Connects as a replication client
   - Receives change events in real-time

3. **Connector converts events to Airbyte records**
   - Extracts before/after row data
   - Adds CDC metadata fields
   - Tracks replication position

### CDC vs Cursor-Based Incremental

| Aspect | Cursor-Based | CDC |
|--------|--------------|-----|
| Detects inserts | Yes | Yes |
| Detects updates | Yes (if cursor updated) | Yes |
| Detects deletes | No | Yes |
| Query load | Higher (SELECT queries) | Lower (reads log) |
| Setup complexity | Low | Higher (DB config needed) |
| Latency | Higher (polling) | Lower (streaming) |

### CDC State Structure

CDC uses **global state** (shared across all streams):

```json
{
  "type": "GLOBAL",
  "global": {
    "shared_state": {
      "state": {
        "mysql_cdc_offset": { ... },
        "mysql_db_history": "..."
      }
    },
    "stream_states": [
      {
        "stream_descriptor": {"name": "users", "namespace": "mydb"},
        "stream_state": {"pk_val": "1000"}
      }
    ]
  }
}
```

---

## CDC Phase 2: Prerequisites

**Goal:** Configure database for CDC

### Step 1: Enable Replication (Database Side)

**MySQL:**
```sql
-- my.cnf / mysqld.cnf
[mysqld]
server-id = 1
log_bin = mysql-bin
binlog_format = ROW
binlog_row_image = FULL
expire_logs_days = 7

-- Grant privileges
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'airbyte'@'%';
GRANT SELECT ON *.* TO 'airbyte'@'%';
```

**PostgreSQL:**
```sql
-- postgresql.conf
wal_level = logical
max_replication_slots = 10
max_wal_senders = 10

-- Create publication and replication slot
CREATE PUBLICATION airbyte_publication FOR ALL TABLES;
SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');

-- Grant privileges
GRANT USAGE ON SCHEMA public TO airbyte;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO airbyte;
ALTER USER airbyte WITH REPLICATION;
```

### Step 2: Add CDC Toolkit to Build

**File:** Update `build.gradle`

```groovy
airbyteBulkConnector {
    core = 'extract'
    toolkits = ['extract-jdbc', 'extract-cdc']  // Add extract-cdc
}

dependencies {
    implementation 'your.database:jdbc-driver:version'
    implementation 'io.debezium:debezium-connector-{db}'  // Add Debezium connector
}
```

### Step 3: Update Configuration for CDC

**File:** Update `{DB}SourceConfiguration.kt`

```kotlin
import io.airbyte.cdk.command.CdcSourceConfiguration

data class {DB}SourceConfiguration(
    // ... existing fields ...
    val incrementalConfiguration: IncrementalConfiguration,
    override val debeziumHeartbeatInterval: Duration = Duration.ofSeconds(10),
) : JdbcSourceConfiguration, CdcSourceConfiguration {  // Add CdcSourceConfiguration

    // True when CDC mode is enabled
    override val global: Boolean
        get() = incrementalConfiguration is CdcIncrementalConfiguration

    // Max time for initial snapshot before switching to streaming
    override val maxSnapshotReadDuration: Duration?
        get() = (incrementalConfiguration as? CdcIncrementalConfiguration)?.initialLoadTimeout
}

sealed interface IncrementalConfiguration

data object UserDefinedCursorIncrementalConfiguration : IncrementalConfiguration

data class CdcIncrementalConfiguration(
    val initialLoadTimeout: Duration,
    val serverTimezone: String?,
    val invalidCdcCursorPositionBehavior: InvalidCdcCursorPositionBehavior,
) : IncrementalConfiguration

enum class InvalidCdcCursorPositionBehavior {
    FAIL_SYNC,   // Fail if saved position is no longer available
    RESET_SYNC,  // Reset and re-sync from beginning
}
```

---

## CDC Phase 3: CDC Position

**Goal:** Define replication position data structure

### Step 1: Create Position Class

**File:** `src/main/kotlin/io/airbyte/integrations/source/{db}/{DB}SourceCdcPosition.kt`

```kotlin
package io.airbyte.integrations.source.{db}

/**
 * Represents a position in the database's replication log.
 *
 * For MySQL: binlog file name + position
 * For PostgreSQL: LSN (Log Sequence Number)
 * For SQL Server: LSN
 */
data class {DB}SourceCdcPosition(
    val fileName: String,   // e.g., "mysql-bin.000003"
    val position: Long,     // e.g., 154
) : Comparable<{DB}SourceCdcPosition> {

    /**
     * Extract file sequence number from filename.
     * MySQL binlog files are named like: mysql-bin.000001, mysql-bin.000002
     */
    val fileSequence: Int
        get() = fileName.substringAfterLast('.').toIntOrNull() ?: 0

    /**
     * Cursor value for deduplication.
     * Combines file sequence and position into a single comparable value.
     */
    val cursorValue: Long
        get() = (fileSequence.toLong() shl Int.SIZE_BITS) or position

    override fun compareTo(other: {DB}SourceCdcPosition): Int =
        cursorValue.compareTo(other.cursorValue)
}
```

**For PostgreSQL (LSN-based):**
```kotlin
data class PostgresCdcPosition(
    val lsn: Long,  // Log Sequence Number
) : Comparable<PostgresCdcPosition> {

    val cursorValue: Long get() = lsn

    override fun compareTo(other: PostgresCdcPosition): Int =
        lsn.compareTo(other.lsn)
}
```

---

## CDC Phase 4: CDC Meta Fields

**Goal:** Define metadata fields added to CDC records

### Step 1: Create Meta Fields Enum

**File:** `src/main/kotlin/io/airbyte/integrations/source/{db}/{DB}SourceCdcMetaFields.kt`

```kotlin
package io.airbyte.integrations.source.{db}

import io.airbyte.cdk.discover.CdcIntegerMetaFieldType
import io.airbyte.cdk.discover.CdcNumberMetaFieldType
import io.airbyte.cdk.discover.CdcStringMetaFieldType
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.MetaField

/**
 * CDC metadata fields added to each record.
 * These appear as columns prefixed with "_ab_cdc_".
 */
enum class {DB}SourceCdcMetaFields(
    override val type: FieldType,
) : MetaField {

    /** Monotonically increasing cursor for deduplication. */
    CDC_CURSOR(CdcIntegerMetaFieldType),

    /** Binlog/WAL file name. */
    CDC_LOG_FILE(CdcStringMetaFieldType),

    /** Position within the log file. */
    CDC_LOG_POS(CdcNumberMetaFieldType),
    ;

    override val id: String
        get() = MetaField.META_PREFIX + name.lowercase()
        // Results in: _ab_cdc_cursor, _ab_cdc_log_file, _ab_cdc_log_pos
}
```

### Step 2: Register Meta Fields in Source Operations

**File:** Update `{DB}SourceOperations.kt`

```kotlin
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.MetaField

@Singleton
@Primary
class {DB}SourceOperations :
    JdbcMetadataQuerier.FieldTypeMapper,
    SelectQueryGenerator,
    JdbcAirbyteStreamFactory {  // Add this interface

    /** The primary cursor field for CDC mode. */
    override val globalCursor: MetaField = {DB}SourceCdcMetaFields.CDC_CURSOR

    /** All CDC metadata fields to add to streams. */
    override val globalMetaFields: Set<MetaField> = setOf(
        {DB}SourceCdcMetaFields.CDC_CURSOR,
        CommonMetaField.CDC_UPDATED_AT,    // _ab_cdc_updated_at
        CommonMetaField.CDC_DELETED_AT,    // _ab_cdc_deleted_at
        {DB}SourceCdcMetaFields.CDC_LOG_FILE,
        {DB}SourceCdcMetaFields.CDC_LOG_POS,
    )

    // ... existing code ...
}
```

---

## CDC Phase 5: Debezium Operations

**Goal:** Implement Debezium integration

### Step 1: Create Debezium Operations Class

**File:** `src/main/kotlin/io/airbyte/integrations/source/{db}/{DB}SourceDebeziumOperations.kt`

```kotlin
package io.airbyte.integrations.source.{db}

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.*
import io.airbyte.cdk.util.Jsons
import io.debezium.connector.mysql.MySqlConnector  // Or your DB's connector
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.ResultSet
import java.sql.Statement
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneOffset
import kotlin.random.Random
import org.apache.kafka.connect.source.SourceRecord

private val log = KotlinLogging.logger {}

@Singleton
class {DB}SourceDebeziumOperations(
    val jdbcConnectionFactory: JdbcConnectionFactory,
    val configuration: {DB}SourceConfiguration,
) : CdcPartitionsCreatorDebeziumOperations<{DB}SourceCdcPosition>,
    CdcPartitionReaderDebeziumOperations<{DB}SourceCdcPosition> {

    private val databaseName: String = configuration.namespaces.first()

    // Random server ID for MySQL (each consumer needs unique ID)
    private val serverId: Int = Random.nextInt(5400, 6400)

    // =========================================================================
    // Position Extraction
    // =========================================================================

    /**
     * Extract position from Debezium offset (stored state).
     */
    override fun position(offset: DebeziumOffset): {DB}SourceCdcPosition {
        val offsetValue = offset.wrapped.values.first() as ObjectNode
        return {DB}SourceCdcPosition(
            fileName = offsetValue["file"].asText(),
            position = offsetValue["pos"].asLong(),
        )
    }

    /**
     * Extract position from Debezium record value.
     */
    override fun position(recordValue: DebeziumRecordValue): {DB}SourceCdcPosition? {
        val source = recordValue.source
        val file = source["file"]?.takeIf { it.isTextual }?.asText() ?: return null
        val pos = source["pos"]?.takeIf { it.isIntegralNumber }?.asLong() ?: return null
        return {DB}SourceCdcPosition(file, pos)
    }

    /**
     * Extract position from Kafka SourceRecord.
     */
    override fun position(sourceRecord: SourceRecord): {DB}SourceCdcPosition? {
        val offset = sourceRecord.sourceOffset()
        val file = offset["file"]?.toString() ?: return null
        val pos = offset["pos"] as? Long ?: return null
        return {DB}SourceCdcPosition(file, pos)
    }

    // =========================================================================
    // Stream Identification
    // =========================================================================

    override fun findStreamNamespace(key: DebeziumRecordKey, value: DebeziumRecordValue): String? =
        value.source["db"]?.asText()  // MySQL: database name
        // PostgreSQL: value.source["schema"]?.asText()

    override fun findStreamName(key: DebeziumRecordKey, value: DebeziumRecordValue): String? =
        value.source["table"]?.asText()

    // =========================================================================
    // Record Deserialization
    // =========================================================================

    /**
     * Convert Debezium change event to Airbyte record.
     */
    override fun deserializeRecord(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
        stream: Stream,
    ): DeserializedRecord {
        val before = value.before
        val after = value.after
        val source = value.source
        val isDelete = after.isNull

        // Use 'before' for deletes, 'after' for inserts/updates
        val data = (if (isDelete) before else after) as ObjectNode

        // Build result record
        val resultRow: NativeRecordPayload = mutableMapOf()

        // Copy data fields
        for (field in stream.schema) {
            val fieldValue = data[field.id]
            if (fieldValue != null && !fieldValue.isNull) {
                resultRow[field.id] = FieldValueEncoder(
                    field.type.jsonEncoder.decode(fieldValue),
                    field.type.jsonEncoder
                )
            }
        }

        // Add CDC metadata fields
        val transactionMillis = source["ts_ms"].asLong()
        val transactionTime = OffsetDateTime.ofInstant(
            Instant.ofEpochMilli(transactionMillis),
            ZoneOffset.UTC
        )

        // _ab_cdc_updated_at
        resultRow[CommonMetaField.CDC_UPDATED_AT.id] = FieldValueEncoder(
            transactionTime,
            CommonMetaField.CDC_UPDATED_AT.type.jsonEncoder
        )

        // _ab_cdc_deleted_at (only for deletes)
        resultRow[CommonMetaField.CDC_DELETED_AT.id] = FieldValueEncoder(
            if (isDelete) transactionTime else null,
            if (isDelete) CommonMetaField.CDC_DELETED_AT.type.jsonEncoder else NullCodec
        )

        // Database-specific CDC fields
        val position = {DB}SourceCdcPosition(
            source["file"].asText(),
            source["pos"].asLong()
        )

        resultRow[{DB}SourceCdcMetaFields.CDC_LOG_FILE.id] = FieldValueEncoder(
            position.fileName,
            {DB}SourceCdcMetaFields.CDC_LOG_FILE.type.jsonEncoder
        )

        resultRow[{DB}SourceCdcMetaFields.CDC_LOG_POS.id] = FieldValueEncoder(
            position.position.toDouble(),
            {DB}SourceCdcMetaFields.CDC_LOG_POS.type.jsonEncoder
        )

        resultRow[{DB}SourceCdcMetaFields.CDC_CURSOR.id] = FieldValueEncoder(
            position.cursorValue,
            {DB}SourceCdcMetaFields.CDC_CURSOR.type.jsonEncoder
        )

        return DeserializedRecord(resultRow, emptyMap())
    }

    // =========================================================================
    // Cold Start (No Saved State)
    // =========================================================================

    /**
     * Generate initial offset by querying current replication position.
     */
    override fun generateColdStartOffset(): DebeziumOffset {
        val (position, gtidSet) = queryCurrentPosition()
        val topicPrefix = DebeziumPropertiesBuilder.sanitizeTopicPrefix(databaseName)
        val timestamp = Instant.now()

        val key = Jsons.arrayNode().apply {
            add(databaseName)
            add(Jsons.objectNode().apply { put("server", topicPrefix) })
        }

        val value = Jsons.objectNode().apply {
            put("ts_sec", timestamp.epochSecond)
            put("file", position.fileName)
            put("pos", position.position)
            gtidSet?.let { put("gtids", it) }
        }

        val offset = DebeziumOffset(mapOf(key to value))
        log.info { "Generated cold start offset: $offset" }
        return offset
    }

    /**
     * Query current binlog position from database.
     */
    private fun queryCurrentPosition(): Pair<{DB}SourceCdcPosition, String?> {
        jdbcConnectionFactory.get().use { connection ->
            connection.createStatement().use { stmt ->
                // MySQL: SHOW MASTER STATUS (or SHOW BINARY LOG STATUS for 8.4+)
                val rs = stmt.executeQuery("SHOW MASTER STATUS")
                if (!rs.next()) {
                    throw ConfigErrorException("Cannot get binlog position")
                }

                val position = {DB}SourceCdcPosition(
                    fileName = rs.getString("File"),
                    position = rs.getLong("Position"),
                )

                // GTID set (if available)
                val gtidSet = try {
                    rs.getString("Executed_Gtid_Set")?.takeIf { it.isNotBlank() }
                } catch (e: Exception) {
                    null
                }

                return position to gtidSet
            }
        }
    }

    /**
     * Debezium properties for cold start (initial snapshot).
     */
    override fun generateColdStartProperties(streams: List<Stream>): Map<String, String> =
        DebeziumPropertiesBuilder()
            .with(commonProperties)
            .with("snapshot.mode", "recovery")  // Build schema history
            .buildMap()

    // =========================================================================
    // Warm Start (Resume from Saved State)
    // =========================================================================

    /**
     * Deserialize and validate saved CDC state.
     */
    override fun deserializeState(opaqueStateValue: OpaqueStateValue): DebeziumWarmStartState {
        return try {
            val (offset, schemaHistory) = deserializeStateInternal(opaqueStateValue)

            // Validate saved position is still available
            if (validatePosition(offset)) {
                ValidDebeziumWarmStartState(offset, schemaHistory)
            } else {
                handleInvalidPosition()
            }
        } catch (e: Exception) {
            log.error(e) { "Error deserializing CDC state" }
            AbortDebeziumWarmStartState("Error deserializing state: ${e.message}")
        }
    }

    /**
     * Validate that saved position is still available in database.
     */
    private fun validatePosition(offset: DebeziumOffset): Boolean {
        val savedPosition = position(offset)

        // Check if binlog file still exists
        val existingFiles = getBinaryLogFiles()
        if (savedPosition.fileName !in existingFiles) {
            log.warn { "Binlog file ${savedPosition.fileName} no longer exists" }
            return false
        }

        return true
    }

    private fun getBinaryLogFiles(): List<String> {
        jdbcConnectionFactory.get().use { connection ->
            connection.createStatement().use { stmt ->
                val rs = stmt.executeQuery("SHOW BINARY LOGS")
                return generateSequence {
                    if (rs.next()) rs.getString(1) else null
                }.toList()
            }
        }
    }

    private fun handleInvalidPosition(): InvalidDebeziumWarmStartState {
        val config = configuration.incrementalConfiguration as CdcIncrementalConfiguration
        return when (config.invalidCdcCursorPositionBehavior) {
            InvalidCdcCursorPositionBehavior.FAIL_SYNC ->
                AbortDebeziumWarmStartState(
                    "Saved binlog position no longer available. " +
                    "Increase binlog retention or sync more frequently."
                )
            InvalidCdcCursorPositionBehavior.RESET_SYNC ->
                ResetDebeziumWarmStartState(
                    "Saved binlog position no longer available. Resetting sync."
                )
        }
    }

    /**
     * Debezium properties for warm start (resume streaming).
     */
    override fun generateWarmStartProperties(streams: List<Stream>): Map<String, String> =
        DebeziumPropertiesBuilder()
            .with(commonProperties)
            .withStreams(streams)
            .buildMap()

    // =========================================================================
    // State Serialization
    // =========================================================================

    /**
     * Serialize CDC state for checkpointing.
     */
    override fun serializeState(
        offset: DebeziumOffset,
        schemaHistory: DebeziumSchemaHistory?,
    ): OpaqueStateValue {
        val stateNode = Jsons.objectNode()

        // Serialize offset
        val offsetNode = Jsons.objectNode()
        for ((k, v) in offset.wrapped) {
            offsetNode.put(Jsons.writeValueAsString(k), Jsons.writeValueAsString(v))
        }
        stateNode.set<JsonNode>("{db}_cdc_offset", offsetNode)

        // Serialize schema history (if present)
        if (schemaHistory != null) {
            val historyString = schemaHistory.wrapped.joinToString("\n") {
                DocumentWriter.defaultWriter().write(it.document())
            }
            // Compress if large
            if (historyString.length > 1024 * 1024) {
                stateNode.put("{db}_db_history", compressHistory(historyString))
                stateNode.put("is_compressed", true)
            } else {
                stateNode.put("{db}_db_history", historyString)
            }
        }

        return Jsons.objectNode().apply {
            set<JsonNode>("state", stateNode)
        }
    }

    // =========================================================================
    // Common Debezium Properties
    // =========================================================================

    private val commonProperties: Map<String, String> by lazy {
        DebeziumPropertiesBuilder()
            .withDefault()
            .withConnector(MySqlConnector::class.java)  // Your DB's connector
            .withDebeziumName(databaseName)
            .withHeartbeats(configuration.debeziumHeartbeatInterval)
            // Binary data as base64
            .with("binary.handling.mode", "base64")
            // Numbers as strings (preserves precision)
            .with("decimal.handling.mode", "string")
            // Temporal precision
            .with("time.precision.mode", "adaptive_time_microseconds")
            // Snapshot settings
            .with("snapshot.mode", "when_needed")
            .with("snapshot.locking.mode", "none")
            .with("include.schema.changes", "false")
            // Database connection
            .withDatabase(configuration.jdbcProperties)
            .withDatabase("hostname", configuration.realHost)
            .withDatabase("port", configuration.realPort.toString())
            .withDatabase("dbname", databaseName)
            .withDatabase("server.id", serverId.toString())  // MySQL specific
            .withDatabase("include.list", databaseName)
            // Offset and schema storage
            .withOffset()
            .withSchemaHistory()
            .buildMap()
    }

    // Helper functions for state deserialization
    private fun deserializeStateInternal(
        state: OpaqueStateValue
    ): Pair<DebeziumOffset, DebeziumSchemaHistory?> {
        val stateNode = state["state"] as ObjectNode
        val offsetNode = stateNode["{db}_cdc_offset"] as ObjectNode

        val offsetMap = offsetNode.fields().asSequence()
            .map { (k, v) -> Jsons.readTree(k) to Jsons.readTree(v.textValue()) }
            .toMap()

        val offset = DebeziumOffset(offsetMap)

        val historyNode = stateNode["{db}_db_history"]
        val schemaHistory = if (historyNode != null) {
            val isCompressed = stateNode["is_compressed"]?.asBoolean() ?: false
            val historyString = if (isCompressed) {
                decompressHistory(historyNode.textValue())
            } else {
                historyNode.textValue()
            }
            val records = historyString.lines()
                .filter { it.isNotBlank() }
                .map { HistoryRecord(DocumentReader.defaultReader().read(it)) }
            DebeziumSchemaHistory(records)
        } else {
            null
        }

        return offset to schemaHistory
    }

    private fun compressHistory(input: String): String {
        val baos = ByteArrayOutputStream()
        GZIPOutputStream(baos).writer().use { it.write(input) }
        return "\"${Base64.encodeBase64(baos.toByteArray())}\""
    }

    private fun decompressHistory(input: String): String {
        val trimmed = input.trim('"')
        val decoded = Base64.decodeBase64(trimmed.toByteArray())
        return GZIPInputStream(ByteArrayInputStream(decoded)).reader().readText()
    }
}
```

---

## CDC Phase 6: CDC Partitions

**Goal:** Add CDC partition types to partition factory

### Step 1: Add CDC Snapshot Partition

**File:** Update `{DB}SourceJdbcPartition.kt`

```kotlin
/**
 * CDC initial snapshot partition.
 * Reads entire table during initial CDC sync.
 */
class {DB}SourceJdbcCdcSnapshotPartition(
    val selectQueryGenerator: {DB}SourceOperations,
    override val streamState: DefaultJdbcStreamState,
    override val checkpointColumns: List<Field>,  // Primary key
    override val lowerBound: List<JsonNode>?,
) : {DB}SourceJdbcPartition,
    JdbcResumableSnapshotPartition<DefaultJdbcStreamState> {

    override val stream: Stream get() = streamState.stream
    override val cursorUpperBound: JsonNode? = null

    override fun querySpec(): SelectQuerySpec {
        val columns = SelectColumns(stream.fields)
        val from = From(stream.name, stream.namespace)

        val where = if (lowerBound != null) {
            Where(Greater(checkpointColumns[0], lowerBound[0]))
        } else {
            NoWhere
        }

        val orderBy = OrderBy(checkpointColumns)
        return SelectQuerySpec(columns, from, where, orderBy)
    }

    /**
     * State during CDC snapshot - track PK for resumability.
     */
    override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue {
        val pkValue = lastRecord.get(checkpointColumns[0].id)?.asText()
        return Jsons.jsonNode({DB}SourceCdcInitialSnapshotStateValue(
            pkName = checkpointColumns[0].id,
            pkVal = pkValue,
        ))
    }

    /**
     * When snapshot completes, return state indicating snapshot done.
     * CDC streaming will take over from here.
     */
    override fun completeState(): OpaqueStateValue =
        Jsons.jsonNode({DB}SourceCdcInitialSnapshotStateValue(
            pkName = null,  // null indicates snapshot complete
            pkVal = null,
        ))
}
```

### Step 2: Add CDC State Value

**File:** `src/main/kotlin/io/airbyte/integrations/source/{db}/{DB}SourceCdcInitialSnapshotStateValue.kt`

```kotlin
package io.airbyte.integrations.source.{db}

import com.fasterxml.jackson.annotation.JsonProperty

/**
 * State value for CDC initial snapshot.
 * Tracks primary key checkpoint during initial table scan.
 */
data class {DB}SourceCdcInitialSnapshotStateValue(
    @JsonProperty("pk_name")
    val pkName: String?,  // null when snapshot complete

    @JsonProperty("pk_val")
    val pkVal: String?,
)
```

### Step 3: Update Partition Factory for CDC

**File:** Update `{DB}SourceJdbcPartitionFactory.kt`

```kotlin
private fun coldStart(streamState: DefaultJdbcStreamState): {DB}SourceJdbcPartition {
    val stream = streamState.stream
    val pkColumns = stream.configuredPrimaryKey ?: emptyList()

    // Full refresh mode
    if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
        // ... existing full refresh logic ...
    }

    // CDC mode (global = true)
    if (sharedState.configuration.global) {
        return if (pkColumns.isEmpty()) {
            // No PK - non-resumable CDC snapshot
            {DB}SourceJdbcNonResumableSnapshotPartition(selectQueryGenerator, streamState)
        } else {
            // Has PK - resumable CDC snapshot
            {DB}SourceJdbcCdcSnapshotPartition(
                selectQueryGenerator, streamState, pkColumns,
                lowerBound = null,
            )
        }
    }

    // Cursor-based incremental (existing code)
    // ...
}

private fun warmStart(
    streamState: DefaultJdbcStreamState,
    state: OpaqueStateValue,
): {DB}SourceJdbcPartition? {
    val stream = streamState.stream
    val pkColumns = stream.configuredPrimaryKey ?: emptyList()

    // CDC mode
    if (sharedState.configuration.global) {
        val sv = Jsons.treeToValue(state, {DB}SourceCdcInitialSnapshotStateValue::class.java)

        // Check if snapshot is complete (pkName is null)
        if (sv.pkName == null) {
            // Snapshot complete - CDC streaming handled by CdcPartitionFactory
            return null
        }

        // Resume snapshot from last PK
        val pkLowerBound = sv.pkVal?.let {
            stateValueToJsonNode(pkColumns[0], it)
        }

        return {DB}SourceJdbcCdcSnapshotPartition(
            selectQueryGenerator, streamState, pkColumns,
            lowerBound = pkLowerBound?.let { listOf(it) },
        )
    }

    // Cursor-based incremental (existing code)
    // ...
}
```

---

## CDC Phase 7: Validate CDC Prerequisites

**Goal:** Check CDC prerequisites during check operation

### Update Metadata Querier

**File:** Update `{DB}SourceMetadataQuerier.kt`

```kotlin
override fun extraChecks() {
    base.extraChecks()

    // Only check CDC prerequisites when in CDC mode
    if (!base.config.global) return

    log.info { "Validating CDC prerequisites..." }

    // MySQL-specific checks
    validateVariable("log_bin", "ON", "Binary logging must be enabled for CDC")
    validateVariable("binlog_format", "ROW", "binlog_format must be ROW for CDC")
    validateVariable("binlog_row_image", "FULL", "binlog_row_image must be FULL for CDC")

    // Check replication privileges
    validateReplicationPrivileges()

    log.info { "CDC prerequisites validated successfully" }
}

private fun validateVariable(variable: String, expectedValue: String, errorMessage: String) {
    val sql = "SHOW VARIABLES WHERE Variable_name = '$variable'"
    base.conn.createStatement().use { stmt ->
        stmt.executeQuery(sql).use { rs ->
            if (!rs.next()) {
                throw ConfigErrorException("Could not query variable '$variable'")
            }
            val actualValue = rs.getString("Value")
            if (!actualValue.equals(expectedValue, ignoreCase = true)) {
                throw ConfigErrorException(
                    "$errorMessage. Current value: '$actualValue', expected: '$expectedValue'"
                )
            }
        }
    }
}

private fun validateReplicationPrivileges() {
    try {
        base.conn.createStatement().use { stmt ->
            // Try MySQL 8.4+ syntax first
            try {
                stmt.execute("SHOW BINARY LOG STATUS")
            } catch (e: SQLException) {
                // Fall back to older syntax
                stmt.execute("SHOW MASTER STATUS")
            }
        }
    } catch (e: SQLException) {
        throw ConfigErrorException(
            "Missing REPLICATION CLIENT privilege. " +
            "Grant with: GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'user'@'%';"
        )
    }
}
```

---

## CDC Phase 8: Testing CDC

**Goal:** Verify CDC sync works

### Step 1: Enable CDC in Test Database

**Docker Compose for MySQL with CDC:**
```yaml
version: '3'
services:
  mysql:
    image: mysql:8.0
    command: --server-id=1 --log-bin=mysql-bin --binlog-format=ROW --binlog-row-image=FULL
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: testdb
      MYSQL_USER: testuser
      MYSQL_PASSWORD: testpass
    ports:
      - "3306:3306"
```

### Step 2: Create Test Config with CDC

**File:** `secrets/config-cdc.json`

```json
{
  "host": "localhost",
  "port": 3306,
  "database": "testdb",
  "username": "root",
  "password": "root",
  "replication_method": {
    "method": "CDC",
    "initial_load_timeout_hours": 8,
    "invalid_cdc_cursor_position_behavior": "Fail sync"
  }
}
```

### Step 3: Test CDC Sync

```bash
# Initial CDC sync (snapshot + streaming start)
./gradlew :airbyte-integrations:connectors:source-{db}:run \
  --args='read --config secrets/config-cdc.json --catalog secrets/catalog.json' \
  > cdc_sync.txt

# Insert new data
mysql -u root -proot testdb -e "INSERT INTO users (name) VALUES ('CDC User');"

# Update existing data
mysql -u root -proot testdb -e "UPDATE users SET name = 'Updated' WHERE id = 1;"

# Delete data
mysql -u root -proot testdb -e "DELETE FROM users WHERE id = 2;"

# Run incremental CDC sync
./gradlew :airbyte-integrations:connectors:source-{db}:run \
  --args='read --config secrets/config-cdc.json --catalog secrets/catalog.json --state secrets/state.json'
```

**Expected:** Records with `_ab_cdc_deleted_at` populated for deletes

---

## Summary

**What you've built:**
- CDC mode with Debezium integration
- Replication position tracking
- CDC metadata fields
- CDC state serialization
- Initial snapshot + streaming support

**Files created:**
- `{DB}SourceCdcPosition.kt` - Replication position
- `{DB}SourceCdcMetaFields.kt` - CDC metadata fields
- `{DB}SourceDebeziumOperations.kt` - Debezium integration
- `{DB}SourceCdcInitialSnapshotStateValue.kt` - CDC snapshot state

**Key interfaces implemented:**
- `CdcPartitionsCreatorDebeziumOperations` - Cold start, warm start
- `CdcPartitionReaderDebeziumOperations` - Record deserialization
- `JdbcAirbyteStreamFactory` - Meta field registration

**CDC Flow:**
1. **Initial sync:** Snapshot (read all data) → Save binlog position
2. **Incremental sync:** Stream from binlog → Emit changes → Update position
3. **Resume:** Validate position → Continue streaming

**Next:** [6-troubleshooting.md](./6-troubleshooting.md) for debugging CDC issues
