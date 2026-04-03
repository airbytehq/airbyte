# Full Refresh: Read Operation

**Prerequisites:** Complete [2-schema-discovery.md](./2-schema-discovery.md)

**Summary:** Implement the `read` operation for full refresh sync mode. After this guide, your connector can read entire tables and emit records.

---

## Read Phase 1: Query Generation

**Goal:** Complete SQL query generation

**Checkpoint:** SelectQueryGenerator produces valid SQL

### Step 1: Understand Query Generation

The CDK uses an AST (Abstract Syntax Tree) for queries:

```kotlin
SelectQuerySpec(
    select = SelectColumns(listOf(field1, field2)),
    from = From(tableName, namespace),
    where = Where(Greater(cursorField, cursorValue)),
    orderBy = OrderBy(listOf(cursorField)),
    limit = Limit(1000)
)
```

Your `SelectQueryGenerator` converts this to database-specific SQL.

### Step 2: Complete Source Operations

**File:** Update `{DB}SourceOperations.kt`

```kotlin
package io.airbyte.integrations.source.{db}

import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.*
import io.airbyte.cdk.read.*
import io.airbyte.cdk.util.Jsons
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

@Singleton
@Primary
class {DB}SourceOperations : JdbcMetadataQuerier.FieldTypeMapper, SelectQueryGenerator {

    // ... toFieldType() and leafType() from previous guide ...

    /**
     * Generate SQL query from AST specification.
     */
    override fun generate(ast: SelectQuerySpec): SelectQuery =
        SelectQuery(ast.sql(), ast.select.columns, ast.bindings())

    /**
     * Build complete SQL string from query spec.
     */
    private fun SelectQuerySpec.sql(): String {
        val components = listOf(
            select.sql(),
            from.sql(),
            where.sql(),
            orderBy.sql()
        )
        val sqlWithoutLimit = components.filter { it.isNotBlank() }.joinToString(" ")

        return when (limit) {
            NoLimit -> sqlWithoutLimit
            Limit(0) -> "$sqlWithoutLimit LIMIT 0"
            is Limit -> "$sqlWithoutLimit LIMIT ?"
        }
    }

    /**
     * Generate SELECT clause.
     */
    private fun SelectNode.sql(): String = "SELECT " + when (this) {
        is SelectColumns -> columns.joinToString(", ") { it.sql() }
        is SelectColumnMaxValue -> "MAX(${column.sql()})"
    }

    /**
     * Quote column identifier.
     * Adjust quoting character for your database:
     * - MySQL: backticks `column`
     * - PostgreSQL/SQL Server: double quotes "column"
     * - Oracle: double quotes "column"
     */
    private fun Field.sql(): String = "`$id`"  // MySQL style

    /**
     * Generate FROM clause.
     */
    private fun FromNode.sql(): String = when (this) {
        NoFrom -> ""
        is From -> {
            val quotedTable = "`$name`"
            if (namespace == null) "FROM $quotedTable"
            else "FROM `$namespace`.$quotedTable"
        }
        is FromSample -> From(name, namespace).sql()  // Treat sample as regular FROM
    }

    /**
     * Generate WHERE clause.
     */
    private fun WhereNode.sql(): String = when (this) {
        NoWhere -> ""
        is Where -> "WHERE ${clause.sql()}"
    }

    /**
     * Generate WHERE clause conditions.
     */
    private fun WhereClauseNode.sql(): String = when (this) {
        is And -> conj.joinToString(") AND (", "(", ")") { it.sql() }
        is Or -> disj.joinToString(") OR (", "(", ")") { it.sql() }
        is Equal -> "${column.sql()} = ?"
        is Greater -> "${column.sql()} > ?"
        is GreaterOrEqual -> "${column.sql()} >= ?"
        is LesserOrEqual -> "${column.sql()} <= ?"
        is Lesser -> "${column.sql()} < ?"
    }

    /**
     * Generate ORDER BY clause.
     */
    private fun OrderByNode.sql(): String = when (this) {
        NoOrderBy -> ""
        is OrderBy -> "ORDER BY " + columns.joinToString(", ") { it.sql() }
    }

    /**
     * Collect parameter bindings for prepared statement.
     */
    private fun SelectQuerySpec.bindings(): List<SelectQuery.Binding> =
        where.bindings() + limit.bindings()

    private fun WhereNode.bindings(): List<SelectQuery.Binding> = when (this) {
        NoWhere -> listOf()
        is Where -> clause.bindings()
    }

    private fun WhereClauseNode.bindings(): List<SelectQuery.Binding> = when (this) {
        is And -> conj.flatMap { it.bindings() }
        is Or -> disj.flatMap { it.bindings() }
        is WhereClauseLeafNode -> {
            val type = column.type as LosslessJdbcFieldType<*, *>
            listOf(SelectQuery.Binding(bindingValue, type))
        }
    }

    private fun LimitNode.bindings(): List<SelectQuery.Binding> = when (this) {
        NoLimit, Limit(0) -> listOf()
        is Limit -> listOf(SelectQuery.Binding(Jsons.numberNode(n), LongFieldType))
    }
}
```

### Step 3: Test Query Generation

```kotlin
// Unit test for query generation
@Test
fun testSelectQuery() {
    val ops = {DB}SourceOperations()

    val field1 = Field("id", IntFieldType)
    val field2 = Field("name", StringFieldType)

    val spec = SelectQuerySpec(
        select = SelectColumns(listOf(field1, field2)),
        from = From("users", "public"),
        where = NoWhere,
        orderBy = NoOrderBy,
        limit = NoLimit,
    )

    val query = ops.generate(spec)
    assertEquals("SELECT `id`, `name` FROM `public`.`users`", query.sql)
}
```

---

## Read Phase 2: Partition Factory

**Goal:** Create partitions for full refresh streams

**Checkpoint:** PartitionFactory creates correct partition types

### Step 1: Understand Partitions

A **Partition** represents a unit of work for reading data:
- Full refresh: Single partition for entire table
- Incremental: Partition with cursor bounds
- CDC: Snapshot partition + streaming partition

The **PartitionFactory** decides which partition type to create based on:
- Sync mode (full refresh vs incremental)
- Current state (cold start vs resuming)
- Configuration (CDC enabled or not)

### Step 2: Create Stream State Value

**Purpose:** Serialize/deserialize state for resumability

**File:** `src/main/kotlin/io/airbyte/integrations/source/{db}/{DB}SourceJdbcStreamStateValue.kt`

```kotlin
package io.airbyte.integrations.source.{db}

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons

/**
 * State value for cursor-based streams.
 * Tracks checkpoint position for resumability.
 */
data class {DB}SourceJdbcStreamStateValue(
    @JsonProperty("state_type")
    val stateType: String,

    @JsonProperty("cursor_field")
    val cursorField: List<String>? = null,

    @JsonProperty("cursor")
    val cursors: String? = null,

    @JsonProperty("pk_name")
    val pkName: String? = null,

    @JsonProperty("pk_val")
    val pkValue: String? = null,
) {
    companion object {
        /** State indicating snapshot is complete (for non-resumable). */
        val snapshotCompleted: JsonNode = Jsons.jsonNode(
            mapOf("state_type" to "snapshot_completed")
        )
    }
}
```

### Step 3: Create Partition Classes

**File:** `src/main/kotlin/io/airbyte/integrations/source/{db}/{DB}SourceJdbcPartition.kt`

```kotlin
package io.airbyte.integrations.source.{db}

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.read.*
import io.airbyte.cdk.util.Jsons

/**
 * Base interface for all partition types.
 */
sealed interface {DB}SourceJdbcPartition : JdbcPartition<DefaultJdbcStreamState>

/**
 * Non-resumable full refresh partition.
 * Used when table has no primary key.
 */
class {DB}SourceJdbcNonResumableSnapshotPartition(
    val selectQueryGenerator: {DB}SourceOperations,
    override val streamState: DefaultJdbcStreamState,
) : {DB}SourceJdbcPartition, JdbcNonResumableSnapshotPartition<DefaultJdbcStreamState> {

    override val stream: Stream get() = streamState.stream

    override val cursorUpperBound: JsonNode? = null

    override fun querySpec(): SelectQuerySpec = SelectQuerySpec(
        SelectColumns(stream.fields),
        From(stream.name, stream.namespace),
    )

    override fun completeState(): OpaqueStateValue =
        {DB}SourceJdbcStreamStateValue.snapshotCompleted
}

/**
 * Resumable full refresh partition.
 * Uses primary key for checkpointing.
 */
class {DB}SourceJdbcSnapshotPartition(
    val selectQueryGenerator: {DB}SourceOperations,
    override val streamState: DefaultJdbcStreamState,
    override val checkpointColumns: List<Field>,
    override val lowerBound: List<JsonNode>?,
    override val upperBound: List<JsonNode>?,
) : {DB}SourceJdbcPartition,
    JdbcResumableSnapshotPartition<DefaultJdbcStreamState>,
    JdbcSplittableSnapshotPartition<DefaultJdbcStreamState> {

    override val stream: Stream get() = streamState.stream

    override val cursorUpperBound: JsonNode? = null

    override fun querySpec(): SelectQuerySpec {
        val columns = SelectColumns(stream.fields)
        val from = From(stream.name, stream.namespace)

        // Build WHERE clause for PK range
        val where = buildWhereClause()
        val orderBy = OrderBy(checkpointColumns)

        return SelectQuerySpec(columns, from, where, orderBy)
    }

    private fun buildWhereClause(): WhereNode {
        if (lowerBound == null && upperBound == null) return NoWhere

        val conditions = mutableListOf<WhereClauseNode>()

        // pk > lowerBound
        if (lowerBound != null) {
            conditions.add(Greater(checkpointColumns[0], lowerBound[0]))
        }

        // pk <= upperBound
        if (upperBound != null) {
            conditions.add(LesserOrEqual(checkpointColumns[0], upperBound[0]))
        }

        return when (conditions.size) {
            0 -> NoWhere
            1 -> Where(conditions[0])
            else -> Where(And(conditions))
        }
    }

    override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue {
        val pkValue = lastRecord.get(checkpointColumns[0].id)?.asText()
        return Jsons.jsonNode({DB}SourceJdbcStreamStateValue(
            stateType = "primary_key",
            pkName = checkpointColumns[0].id,
            pkValue = pkValue,
        ))
    }

    override fun completeState(): OpaqueStateValue = Jsons.nullNode()
}
```

### Step 4: Create Partition Factory

**File:** `src/main/kotlin/io/airbyte/integrations/source/{db}/{DB}SourceJdbcPartitionFactory.kt`

```kotlin
package io.airbyte.integrations.source.{db}

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.*
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

private val log = KotlinLogging.logger {}

@Primary
@Singleton
class {DB}SourceJdbcPartitionFactory(
    override val sharedState: DefaultJdbcSharedState,
    val selectQueryGenerator: {DB}SourceOperations,
    val config: {DB}SourceConfiguration,
) : JdbcPartitionFactory<
    DefaultJdbcSharedState,
    DefaultJdbcStreamState,
    {DB}SourceJdbcPartition,
> {

    private val streamStates = ConcurrentHashMap<StreamIdentifier, DefaultJdbcStreamState>()

    override fun streamState(streamFeedBootstrap: StreamFeedBootstrap): DefaultJdbcStreamState =
        streamStates.getOrPut(streamFeedBootstrap.feed.id) {
            DefaultJdbcStreamState(sharedState, streamFeedBootstrap)
        }

    /**
     * Create partition for a stream.
     * Called once per stream at start of sync.
     */
    override fun create(streamFeedBootstrap: StreamFeedBootstrap): {DB}SourceJdbcPartition? {
        val stream = streamFeedBootstrap.feed
        val streamState = streamState(streamFeedBootstrap)

        // Check if stream is already complete
        if (streamFeedBootstrap.currentState?.isNull == true) {
            return null  // Already synced
        }

        // Cold start (no state) or empty state
        if (streamFeedBootstrap.currentState == null ||
            streamFeedBootstrap.currentState?.isEmpty == true) {
            return coldStart(streamState)
        }

        // Warm start (resume from state)
        return warmStart(streamState, streamFeedBootstrap.currentState!!)
    }

    /**
     * Initial read - no previous state.
     */
    private fun coldStart(streamState: DefaultJdbcStreamState): {DB}SourceJdbcPartition {
        val stream = streamState.stream
        val pkColumns = stream.configuredPrimaryKey ?: emptyList()

        // Full refresh mode
        if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
            return if (pkColumns.isEmpty()) {
                // No PK - non-resumable
                {DB}SourceJdbcNonResumableSnapshotPartition(selectQueryGenerator, streamState)
            } else {
                // Has PK - resumable with PK checkpoint
                val upperBound = findPkUpperBound(stream, pkColumns)
                {DB}SourceJdbcSnapshotPartition(
                    selectQueryGenerator,
                    streamState,
                    pkColumns,
                    lowerBound = null,
                    upperBound = listOf(upperBound),
                )
            }
        }

        // Incremental mode - will be implemented in next guide
        throw UnsupportedOperationException("Incremental mode not yet implemented")
    }

    /**
     * Resume from saved state.
     */
    private fun warmStart(
        streamState: DefaultJdbcStreamState,
        state: OpaqueStateValue,
    ): {DB}SourceJdbcPartition? {
        val stream = streamState.stream
        val pkColumns = stream.configuredPrimaryKey ?: emptyList()

        // Parse state
        val sv = Jsons.treeToValue(state, {DB}SourceJdbcStreamStateValue::class.java)

        // Check if complete
        if (sv.stateType == "snapshot_completed") {
            return null
        }

        // Resume snapshot from last PK
        if (pkColumns.isEmpty()) {
            return {DB}SourceJdbcNonResumableSnapshotPartition(selectQueryGenerator, streamState)
        }

        val upperBound = findPkUpperBound(stream, pkColumns)
        val lowerBound = sv.pkValue?.let { pkVal ->
            stateValueToJsonNode(pkColumns[0], pkVal)
        }

        return {DB}SourceJdbcSnapshotPartition(
            selectQueryGenerator,
            streamState,
            pkColumns,
            lowerBound = lowerBound?.let { listOf(it) },
            upperBound = listOf(upperBound),
        )
    }

    /**
     * Find maximum primary key value in table.
     */
    private fun findPkUpperBound(stream: Stream, pkColumns: List<Field>): JsonNode {
        val jdbcConnectionFactory = JdbcConnectionFactory(config)
        val maxPkQuery = SelectQuerySpec(
            SelectColumnMaxValue(pkColumns[0]),
            From(stream.name, stream.namespace),
        )

        jdbcConnectionFactory.get().use { connection ->
            val stmt = connection.prepareStatement(selectQueryGenerator.generate(maxPkQuery).sql)
            val rs = stmt.executeQuery()

            return if (rs.next()) {
                val jdbcFieldType = pkColumns[0].type as JdbcFieldType<*>
                jdbcFieldType.get(rs, 1)
            } else {
                Jsons.nullNode()
            }
        }
    }

    /**
     * Convert state string value back to JsonNode for query binding.
     */
    private fun stateValueToJsonNode(field: Field, stateValue: String?): JsonNode {
        if (stateValue == null) return Jsons.nullNode()

        return when (field.type) {
            is IntFieldType, is LongFieldType, is ShortFieldType ->
                Jsons.valueToTree(stateValue.toLongOrNull())
            is BigDecimalFieldType, is DoubleFieldType, is FloatFieldType ->
                Jsons.valueToTree(stateValue.toDoubleOrNull())
            else -> Jsons.valueToTree(stateValue)
        }
    }

    /**
     * Split partition for parallel reads.
     * Optional - return unsplit partition if not supporting parallelism.
     */
    override fun split(
        unsplitPartition: {DB}SourceJdbcPartition,
        opaqueStateValues: List<OpaqueStateValue>,
    ): List<{DB}SourceJdbcPartition> {
        // For now, don't split - read sequentially
        return listOf(unsplitPartition)
    }
}
```

---

## Read Phase 3: Test Full Refresh

**Goal:** Verify full refresh read works

**Checkpoint:** `read` operation emits records

### Step 1: Create Test Catalog

**File:** `secrets/catalog.json`

```json
{
  "streams": [
    {
      "stream": {
        "name": "users",
        "namespace": "public",
        "json_schema": {
          "type": "object",
          "properties": {
            "id": { "type": "integer" },
            "name": { "type": "string" }
          }
        },
        "supported_sync_modes": ["full_refresh"],
        "source_defined_primary_key": [["id"]]
      },
      "sync_mode": "full_refresh",
      "destination_sync_mode": "overwrite"
    }
  ]
}
```

### Step 2: Run Read Operation

```bash
./gradlew :airbyte-integrations:connectors:source-{db}:run \
  --args='read --config secrets/config.json --catalog secrets/catalog.json'
```

**Expected output:**
```json
{"type":"RECORD","record":{"stream":"users","namespace":"public","data":{"id":1,"name":"Alice"},"emitted_at":1234567890}}
{"type":"RECORD","record":{"stream":"users","namespace":"public","data":{"id":2,"name":"Bob"},"emitted_at":1234567891}}
{"type":"STATE","state":{"type":"STREAM","stream":{"stream_descriptor":{"name":"users","namespace":"public"},"stream_state":null}}}
```

### Step 3: Verify Type Mapping

Insert test data with various types:

```sql
INSERT INTO type_test VALUES (
    1,                          -- id
    TRUE,                       -- bool_col
    42,                         -- int_col
    9223372036854775807,        -- bigint_col
    3.14,                       -- float_col
    123.45,                     -- decimal_col
    'hello',                    -- varchar_col
    'world',                    -- text_col
    '2024-01-15',              -- date_col
    '10:30:00',                -- time_col
    '2024-01-15 10:30:00',     -- timestamp_col
    '2024-01-15 10:30:00+00',  -- timestamptz_col
    '{"key": "value"}',        -- json_col
    E'\\xDEADBEEF'             -- binary_col
);
```

Read and verify:

```bash
./gradlew :airbyte-integrations:connectors:source-{db}:run \
  --args='read --config secrets/config.json --catalog secrets/catalog.json' \
  | grep '"stream":"type_test"'
```

---

## Summary

**What you've built:**
- Complete SQL query generation
- Partition factory for full refresh streams
- Resumable reads using primary key checkpointing
- State serialization for resumability

**Files created:**
- `{DB}SourceOperations.kt` - Completed query generation
- `{DB}SourceJdbcStreamStateValue.kt` - State serialization
- `{DB}SourceJdbcPartition.kt` - Partition implementations
- `{DB}SourceJdbcPartitionFactory.kt` - Partition creation

**Key interfaces implemented:**
- `SelectQueryGenerator` - Full SQL generation
- `JdbcPartitionFactory` - Partition creation
- `JdbcNonResumableSnapshotPartition` - Non-resumable reads
- `JdbcResumableSnapshotPartition` - Resumable reads

**Next:** Continue to [4-incremental.md](./4-incremental.md) to implement cursor-based incremental sync.
