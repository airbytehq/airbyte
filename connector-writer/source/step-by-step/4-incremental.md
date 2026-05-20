# Incremental Sync: Cursor-Based Reading

**Prerequisites:** Complete [3-full-refresh.md](./3-full-refresh.md)

**Summary:** Implement cursor-based incremental sync. After this guide, your connector can track state using cursor columns and read only new/updated records.

---

## Incremental Phase 1: Understanding Incremental Sync

**Goal:** Understand the incremental sync flow

### How Incremental Sync Works

1. **First sync (cold start):**
   - Read entire table (snapshot)
   - Track cursor value (e.g., `updated_at`) from each record
   - Save final cursor value as state

2. **Subsequent syncs (warm start):**
   - Load saved cursor value from state
   - Query: `SELECT * FROM table WHERE cursor > saved_value ORDER BY cursor`
   - Track new cursor values
   - Save updated state

### Two-Phase Initial Sync

For tables with primary keys, the initial sync has two phases:

1. **PK Phase:** Read table ordered by PK, checkpoint using PK
   - Query: `SELECT * WHERE pk > last_pk ORDER BY pk`
   - State: `{state_type: "primary_key", pk_val: "123"}`

2. **Cursor Phase:** Switch to cursor-based reading
   - Query: `SELECT * WHERE cursor > last_cursor ORDER BY cursor`
   - State: `{state_type: "cursor_based", cursor: "2024-01-15T10:30:00"}`

This allows resumable initial sync AND efficient incremental updates.

---

## Incremental Phase 2: Partition Implementations

**Goal:** Add incremental partition types

**Checkpoint:** Incremental partitions work

### Step 1: Add Incremental Partitions

**File:** Update `{DB}SourceJdbcPartition.kt`

```kotlin
package io.airbyte.integrations.source.{db}

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.read.*
import io.airbyte.cdk.util.Jsons

// ... existing partition classes from previous guide ...

/**
 * Snapshot partition with cursor tracking.
 * Used for initial incremental sync - reads entire table while tracking cursor.
 */
class {DB}SourceJdbcSnapshotWithCursorPartition(
    val selectQueryGenerator: {DB}SourceOperations,
    override val streamState: DefaultJdbcStreamState,
    override val checkpointColumns: List<Field>,  // Primary key columns
    override val lowerBound: List<JsonNode>?,     // Last PK value
    val cursor: Field,                             // Cursor column (e.g., updated_at)
    val cursorUpperBound: JsonNode?,              // Max cursor value at start
) : {DB}SourceJdbcPartition,
    JdbcResumableSnapshotWithCursorPartition<DefaultJdbcStreamState> {

    override val stream: Stream get() = streamState.stream

    override fun querySpec(): SelectQuerySpec {
        val columns = SelectColumns(stream.fields)
        val from = From(stream.name, stream.namespace)

        // WHERE pk > last_pk (if resuming)
        val where = if (lowerBound != null) {
            Where(Greater(checkpointColumns[0], lowerBound[0]))
        } else {
            NoWhere
        }

        // ORDER BY pk for resumability
        val orderBy = OrderBy(checkpointColumns)

        return SelectQuerySpec(columns, from, where, orderBy)
    }

    /**
     * State during snapshot phase - track PK position.
     */
    override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue {
        val pkValue = lastRecord.get(checkpointColumns[0].id)?.asText()
        val cursorValue = lastRecord.get(cursor.id)?.asText()

        return Jsons.jsonNode({DB}SourceJdbcStreamStateValue(
            stateType = "primary_key",
            pkName = checkpointColumns[0].id,
            pkValue = pkValue,
            cursorField = listOf(cursor.id),
            cursors = cursorValue,
        ))
    }

    /**
     * State when snapshot completes - switch to cursor-based.
     */
    override fun completeState(): OpaqueStateValue {
        // Get the cursor upper bound that was captured at start of sync
        val cursorValue = cursorUpperBound?.asText()
            ?: streamState.cursorUpperBound?.asText()

        return Jsons.jsonNode({DB}SourceJdbcStreamStateValue(
            stateType = "cursor_based",
            cursorField = listOf(cursor.id),
            cursors = cursorValue,
        ))
    }
}

/**
 * Non-resumable snapshot with cursor tracking.
 * Used when table has no primary key.
 */
class {DB}SourceJdbcNonResumableSnapshotWithCursorPartition(
    val selectQueryGenerator: {DB}SourceOperations,
    override val streamState: DefaultJdbcStreamState,
    val cursor: Field,
) : {DB}SourceJdbcPartition,
    JdbcNonResumableSnapshotPartition<DefaultJdbcStreamState> {

    override val stream: Stream get() = streamState.stream

    override val cursorUpperBound: JsonNode? = null

    override fun querySpec(): SelectQuerySpec = SelectQuerySpec(
        SelectColumns(stream.fields),
        From(stream.name, stream.namespace),
    )

    override fun completeState(): OpaqueStateValue {
        val cursorValue = streamState.cursorUpperBound?.asText()

        return Jsons.jsonNode({DB}SourceJdbcStreamStateValue(
            stateType = "cursor_based",
            cursorField = listOf(cursor.id),
            cursors = cursorValue,
        ))
    }
}

/**
 * Cursor-based incremental partition.
 * Used for incremental reads after initial sync.
 */
class {DB}SourceJdbcCursorIncrementalPartition(
    val selectQueryGenerator: {DB}SourceOperations,
    override val streamState: DefaultJdbcStreamState,
    val cursor: Field,
    val cursorLowerBound: JsonNode,       // Last cursor value from state
    val isLowerBoundIncluded: Boolean,    // Include lower bound in query?
    override val cursorUpperBound: JsonNode?,  // Max cursor at start of sync
) : {DB}SourceJdbcPartition,
    JdbcCursorIncrementalPartition<DefaultJdbcStreamState> {

    override val stream: Stream get() = streamState.stream

    override fun querySpec(): SelectQuerySpec {
        val columns = SelectColumns(stream.fields)
        val from = From(stream.name, stream.namespace)

        // WHERE cursor > last_cursor (or >= if inclusive)
        val cursorCondition = if (isLowerBoundIncluded) {
            GreaterOrEqual(cursor, cursorLowerBound)
        } else {
            Greater(cursor, cursorLowerBound)
        }

        // Add upper bound if specified
        val where = if (cursorUpperBound != null) {
            Where(And(listOf(cursorCondition, LesserOrEqual(cursor, cursorUpperBound))))
        } else {
            Where(cursorCondition)
        }

        val orderBy = OrderBy(listOf(cursor))

        return SelectQuerySpec(columns, from, where, orderBy)
    }

    /**
     * State with current cursor position.
     */
    override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue {
        val cursorValue = lastRecord.get(cursor.id)?.asText()

        return Jsons.jsonNode({DB}SourceJdbcStreamStateValue(
            stateType = "cursor_based",
            cursorField = listOf(cursor.id),
            cursors = cursorValue,
        ))
    }

    /**
     * Final state when incremental read completes.
     */
    override fun completeState(): OpaqueStateValue {
        val cursorValue = cursorUpperBound?.asText()
            ?: streamState.cursorUpperBound?.asText()

        return Jsons.jsonNode({DB}SourceJdbcStreamStateValue(
            stateType = "cursor_based",
            cursorField = listOf(cursor.id),
            cursors = cursorValue,
        ))
    }
}
```

### Step 2: Update Partition Factory

**File:** Update `{DB}SourceJdbcPartitionFactory.kt`

```kotlin
// Add to coldStart() method:

private fun coldStart(streamState: DefaultJdbcStreamState): {DB}SourceJdbcPartition {
    val stream = streamState.stream
    val pkColumns = stream.configuredPrimaryKey ?: emptyList()

    // Full refresh mode
    if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
        return if (pkColumns.isEmpty()) {
            {DB}SourceJdbcNonResumableSnapshotPartition(selectQueryGenerator, streamState)
        } else {
            val upperBound = findPkUpperBound(stream, pkColumns)
            {DB}SourceJdbcSnapshotPartition(
                selectQueryGenerator, streamState, pkColumns,
                lowerBound = null, upperBound = listOf(upperBound),
            )
        }
    }

    // Incremental mode
    val cursorColumn = stream.configuredCursor as? Field
        ?: throw ConfigErrorException("Incremental sync requires a cursor column")

    return if (pkColumns.isEmpty()) {
        // No PK - non-resumable snapshot
        {DB}SourceJdbcNonResumableSnapshotWithCursorPartition(
            selectQueryGenerator, streamState, cursorColumn
        )
    } else {
        // Has PK - resumable snapshot with cursor
        {DB}SourceJdbcSnapshotWithCursorPartition(
            selectQueryGenerator, streamState, pkColumns,
            lowerBound = null,
            cursor = cursorColumn,
            cursorUpperBound = streamState.cursorUpperBound,
        )
    }
}

// Add to warmStart() method:

private fun warmStart(
    streamState: DefaultJdbcStreamState,
    state: OpaqueStateValue,
): {DB}SourceJdbcPartition? {
    val stream = streamState.stream
    val pkColumns = stream.configuredPrimaryKey ?: emptyList()

    val sv = Jsons.treeToValue(state, {DB}SourceJdbcStreamStateValue::class.java)

    // Full refresh - handled in previous guide
    if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH) {
        // ... existing full refresh logic ...
    }

    // Incremental mode
    val cursorColumn = stream.configuredCursor as? Field
        ?: throw ConfigErrorException("Incremental sync requires a cursor column")

    return when (sv.stateType) {
        "primary_key" -> {
            // Still in initial snapshot phase
            val pkLowerBound = sv.pkValue?.let {
                stateValueToJsonNode(pkColumns[0], it)
            }

            {DB}SourceJdbcSnapshotWithCursorPartition(
                selectQueryGenerator, streamState, pkColumns,
                lowerBound = pkLowerBound?.let { listOf(it) },
                cursor = cursorColumn,
                cursorUpperBound = sv.cursors?.let { stateValueToJsonNode(cursorColumn, it) },
            )
        }

        "cursor_based" -> {
            // Incremental phase
            val cursorLowerBound = sv.cursors?.let {
                stateValueToJsonNode(cursorColumn, it)
            } ?: return coldStart(streamState)  // No cursor value - restart

            // Check if we've caught up
            if (cursorLowerBound == streamState.cursorUpperBound) {
                return null  // Already up to date
            }

            {DB}SourceJdbcCursorIncrementalPartition(
                selectQueryGenerator, streamState, cursorColumn,
                cursorLowerBound = cursorLowerBound,
                isLowerBoundIncluded = false,
                cursorUpperBound = streamState.cursorUpperBound,
            )
        }

        else -> coldStart(streamState)
    }
}
```

---

## Incremental Phase 3: Cursor Upper Bound

**Goal:** Capture cursor upper bound at start of sync

### Why Cursor Upper Bound Matters

Without capturing the cursor upper bound:
- Records inserted during sync might be missed
- Records might be read multiple times

Solution: Query `MAX(cursor)` at start and use as upper bound.

### Step 1: Update Partition Factory

The CDK's `DefaultJdbcStreamState` handles cursor upper bound automatically via `cursorUpperBound` property. Make sure to use it:

```kotlin
// In coldStart():
{DB}SourceJdbcSnapshotWithCursorPartition(
    selectQueryGenerator, streamState, pkColumns,
    lowerBound = null,
    cursor = cursorColumn,
    cursorUpperBound = streamState.cursorUpperBound,  // CDK provides this
)

// In CursorIncrementalPartition:
{DB}SourceJdbcCursorIncrementalPartition(
    selectQueryGenerator, streamState, cursorColumn,
    cursorLowerBound = cursorLowerBound,
    isLowerBoundIncluded = false,
    cursorUpperBound = streamState.cursorUpperBound,  // CDK provides this
)
```

---

## Incremental Phase 4: Testing Incremental Sync

**Goal:** Verify incremental sync works correctly

### Step 1: Create Test Catalog with Incremental Mode

**File:** `secrets/catalog-incremental.json`

```json
{
  "streams": [
    {
      "stream": {
        "name": "events",
        "namespace": "public",
        "json_schema": {
          "type": "object",
          "properties": {
            "id": { "type": "integer" },
            "event_type": { "type": "string" },
            "created_at": { "type": "string", "format": "date-time" }
          }
        },
        "supported_sync_modes": ["full_refresh", "incremental"],
        "source_defined_cursor": false,
        "default_cursor_field": ["created_at"],
        "source_defined_primary_key": [["id"]]
      },
      "sync_mode": "incremental",
      "cursor_field": ["created_at"],
      "destination_sync_mode": "append"
    }
  ]
}
```

### Step 2: Initial Sync (Cold Start)

```bash
# Insert test data
INSERT INTO events (id, event_type, created_at) VALUES
    (1, 'login', '2024-01-01 10:00:00'),
    (2, 'purchase', '2024-01-02 10:00:00'),
    (3, 'logout', '2024-01-03 10:00:00');

# Run initial sync
./gradlew :airbyte-integrations:connectors:source-{db}:run \
  --args='read --config secrets/config.json --catalog secrets/catalog-incremental.json' \
  > initial_sync.txt
```

**Expected:** All 3 records + state with cursor value

```json
{"type":"RECORD","record":{"stream":"events","data":{"id":1,"event_type":"login","created_at":"2024-01-01T10:00:00"}}}
{"type":"RECORD","record":{"stream":"events","data":{"id":2,"event_type":"purchase","created_at":"2024-01-02T10:00:00"}}}
{"type":"RECORD","record":{"stream":"events","data":{"id":3,"event_type":"logout","created_at":"2024-01-03T10:00:00"}}}
{"type":"STATE","state":{"type":"STREAM","stream":{"stream_state":{"state_type":"cursor_based","cursor_field":["created_at"],"cursor":"2024-01-03T10:00:00"}}}}
```

### Step 3: Extract State

```bash
# Extract final state
grep '"type":"STATE"' initial_sync.txt | tail -1 | jq '.state' > secrets/state.json
```

### Step 4: Insert New Data

```sql
INSERT INTO events (id, event_type, created_at) VALUES
    (4, 'click', '2024-01-04 10:00:00'),
    (5, 'view', '2024-01-05 10:00:00');
```

### Step 5: Incremental Sync (Warm Start)

```bash
./gradlew :airbyte-integrations:connectors:source-{db}:run \
  --args='read --config secrets/config.json --catalog secrets/catalog-incremental.json --state secrets/state.json'
```

**Expected:** Only new records (4, 5)

```json
{"type":"RECORD","record":{"stream":"events","data":{"id":4,"event_type":"click","created_at":"2024-01-04T10:00:00"}}}
{"type":"RECORD","record":{"stream":"events","data":{"id":5,"event_type":"view","created_at":"2024-01-05T10:00:00"}}}
{"type":"STATE","state":{"type":"STREAM","stream":{"stream_state":{"state_type":"cursor_based","cursor_field":["created_at"],"cursor":"2024-01-05T10:00:00"}}}}
```

### Step 6: Verify No Data (Up to Date)

```bash
# Run again with updated state - should get no records
grep '"type":"STATE"' incremental_sync.txt | tail -1 | jq '.state' > secrets/state.json

./gradlew :airbyte-integrations:connectors:source-{db}:run \
  --args='read --config secrets/config.json --catalog secrets/catalog-incremental.json --state secrets/state.json'
```

**Expected:** Only state message, no records

---

## Common Issues

### Issue: Duplicate Records

**Cause:** Cursor value not unique (multiple records with same timestamp)

**Solutions:**
1. Use higher precision timestamp (`TIMESTAMP(6)`)
2. Use composite cursor (timestamp + id)
3. Accept some duplicates (destination dedupes)

### Issue: Missing Records

**Cause:** Records inserted during sync with timestamp before cursor upper bound

**Solution:** CDK captures cursor upper bound at start - ensure you use `streamState.cursorUpperBound`

### Issue: Wrong State Type After Initial Sync

**Cause:** `completeState()` returns wrong state type

**Solution:** Ensure snapshot partition's `completeState()` returns `cursor_based` state type

### Issue: State Not Serializable

**Cause:** State value contains non-serializable types

**Solution:** Ensure all state values are JSON-serializable strings

---

## Summary

**What you've built:**
- Cursor-based incremental sync
- Two-phase initial sync (PK snapshot → cursor incremental)
- State tracking and resumability
- Cursor upper bound handling

**Files modified:**
- `{DB}SourceJdbcStreamStateValue.kt` - Added cursor fields
- `{DB}SourceJdbcPartition.kt` - Added incremental partitions
- `{DB}SourceJdbcPartitionFactory.kt` - Added incremental logic

**Partition types:**
| Partition | Use Case |
|-----------|----------|
| `NonResumableSnapshotPartition` | Full refresh, no PK |
| `SnapshotPartition` | Full refresh with PK |
| `SnapshotWithCursorPartition` | Initial incremental with PK |
| `NonResumableSnapshotWithCursorPartition` | Initial incremental, no PK |
| `CursorIncrementalPartition` | Incremental after initial sync |

**Next Steps:**
- [5-cdc.md](./5-cdc.md) - Add CDC support (optional)
- [6-troubleshooting.md](./6-troubleshooting.md) - Debug common issues
