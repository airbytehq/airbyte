/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlin.coroutines.coroutineContext
import kotlinx.coroutines.ensureActive

/** Base class for JDBC implementations of [PartitionReader]. */
sealed class StreamPartitionReader(
    val streamState: JdbcStreamState<*>,
    val input: Input,
) : PartitionReader {
    val stream: Stream = streamState.stream
    val sharedState: JdbcSharedState = streamState.sharedState
    val outputConsumer: OutputConsumer = sharedState.outputConsumer
    val selectQuerier: SelectQuerier = sharedState.selectQuerier

    sealed interface Input {
        val resumable: Boolean
    }

    data class SnapshotInput(
        val primaryKey: List<Field>,
        val primaryKeyLowerBound: List<JsonNode>?,
        val primaryKeyUpperBound: List<JsonNode>?,
    ) : Input {
        override val resumable: Boolean
            get() = primaryKey.isNotEmpty()
    }

    data class SnapshotWithCursorInput(
        val primaryKey: List<Field>,
        val primaryKeyLowerBound: List<JsonNode>?,
        val primaryKeyUpperBound: List<JsonNode>?,
        val cursor: Field,
        val cursorUpperBound: JsonNode,
    ) : Input {
        override val resumable: Boolean
            get() = primaryKey.isNotEmpty()
    }

    data class CursorIncrementalInput(
        val cursor: Field,
        val cursorLowerBound: JsonNode,
        val isLowerBoundIncluded: Boolean,
        val cursorUpperBound: JsonNode,
    ) : Input {
        override val resumable: Boolean
            get() = true
    }

    private val acquiredResources = AtomicReference<AcquiredResources>()

    fun interface AcquiredResources : AutoCloseable

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val acquiredResources: AcquiredResources =
            sharedState.tryAcquireResourcesForReader()
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredResources.set(acquiredResources)
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    fun out(record: ObjectNode) {
        val recordMessageData: ObjectNode = Jsons.objectNode()
        for (fieldName in streamFieldNames) {
            recordMessageData.set<JsonNode>(fieldName, record[fieldName] ?: Jsons.nullNode())
        }
        outputConsumer.accept(
            AirbyteRecordMessage()
                .withStream(stream.name)
                .withNamespace(stream.namespace)
                .withData(recordMessageData),
        )
    }

    val streamFieldNames: List<String> = stream.fields.map { it.id }

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.close()
    }
}

/** JDBC implementation of [PartitionReader] which reads the [input] in its entirety. */
class StreamNonResumablePartitionReader(
    val selectQueryGenerator: SelectQueryGenerator,
    streamState: JdbcStreamState<*>,
    input: Input,
) : StreamPartitionReader(streamState, input) {

    val runComplete = AtomicBoolean(false)
    val numRecords = AtomicLong()

    override suspend fun run() {
        val querySpec: SelectQuerySpec =
            input.querySpec(
                stream,
                isOrdered = false,
                limit = null,
            )
        val query: SelectQuery = selectQueryGenerator.generate(querySpec.optimize())
        selectQuerier
            .executeQuery(
                q = query,
                parameters = SelectQuerier.Parameters(streamState.fetchSize),
            )
            .use { result: SelectQuerier.Result ->
                for (record in result) {
                    out(record)
                    numRecords.incrementAndGet()
                }
            }
        runComplete.set(true)
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        // Sanity check.
        if (!runComplete.get()) throw RuntimeException("cannot checkpoint non-resumable read")
        // The run method executed to completion without a LIMIT clause.
        // This implies that the partition boundary has been reached.
        return PartitionReadCheckpoint(input.checkpoint().opaqueStateValue(), numRecords.get())
    }
}

/**
 * JDBC implementation of [PartitionReader] which reads as much as possible of the [input], in
 * order, before timing out.
 */
class StreamResumablePartitionReader(
    val selectQueryGenerator: SelectQueryGenerator,
    streamState: JdbcStreamState<*>,
    input: Input,
) : StreamPartitionReader(streamState, input) {

    val incumbentLimit = AtomicLong()
    val numRecords = AtomicLong()
    val lastRecord = AtomicReference<ObjectNode?>(null)
    val runComplete = AtomicBoolean(false)

    override suspend fun run() {
        val fetchSize: Int = streamState.fetchSizeOrDefault
        val limit: Long = streamState.limit
        incumbentLimit.set(limit)
        val querySpec: SelectQuerySpec =
            input.querySpec(
                stream,
                isOrdered = true,
                limit = limit,
            )
        val query: SelectQuery = selectQueryGenerator.generate(querySpec.optimize())
        selectQuerier
            .executeQuery(
                q = query,
                parameters = SelectQuerier.Parameters(fetchSize),
            )
            .use { result: SelectQuerier.Result ->
                for (record in result) {
                    out(record)
                    lastRecord.set(record)
                    // Check activity periodically to handle timeout.
                    if (numRecords.incrementAndGet() % fetchSize == 0L) {
                        coroutineContext.ensureActive()
                    }
                }
            }
        runComplete.set(true)
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        if (runComplete.get() && numRecords.get() < streamState.limit) {
            // The run method executed to completion with a LIMIT clause which was not reached.
            return PartitionReadCheckpoint(input.checkpoint().opaqueStateValue(), numRecords.get())
        }
        // The run method ended because of either the LIMIT or the timeout.
        // Adjust the LIMIT value so that it grows or shrinks to try to fit the timeout.
        if (incumbentLimit.get() > 0L) {
            if (runComplete.get() && streamState.limit <= incumbentLimit.get()) {
                // Increase the limit clause for the next PartitionReader, because it's too small.
                // If it had been bigger then run might have executed for longer.
                streamState.updateLimitState { it.up }
            }
            if (!runComplete.get() && incumbentLimit.get() <= streamState.limit) {
                // Decrease the limit clause for the next PartitionReader, because it's too big.
                // If it had been smaller then run might have completed in time.
                streamState.updateLimitState { it.down }
            }
        }
        val checkpointState: OpaqueStateValue =
            input.checkpoint(lastRecord.get()!!).opaqueStateValue()
        return PartitionReadCheckpoint(checkpointState, numRecords.get())
    }
}

/** Converts a [StreamPartitionReader.Input] into a [SelectQuerySpec]. */
fun StreamPartitionReader.Input.querySpec(
    stream: Stream,
    isOrdered: Boolean,
    limit: Long?,
): SelectQuerySpec =
    when (this) {
        is StreamPartitionReader.SnapshotInput ->
            querySpecForStreamPartitionReader(
                stream,
                checkpointColumns = primaryKey,
                checkpointLowerBound = primaryKeyLowerBound,
                isLowerBoundIncluded = false,
                checkpointUpperBound = primaryKeyUpperBound,
                isOrdered,
                limit,
            )
        is StreamPartitionReader.SnapshotWithCursorInput ->
            querySpecForStreamPartitionReader(
                stream,
                checkpointColumns = primaryKey,
                checkpointLowerBound = primaryKeyLowerBound,
                isLowerBoundIncluded = false,
                checkpointUpperBound = primaryKeyUpperBound,
                isOrdered,
                limit,
            )
        is StreamPartitionReader.CursorIncrementalInput ->
            querySpecForStreamPartitionReader(
                stream,
                checkpointColumns = listOf(cursor),
                checkpointLowerBound = listOf(cursorLowerBound),
                isLowerBoundIncluded = isLowerBoundIncluded,
                checkpointUpperBound = listOf(cursorUpperBound),
                isOrdered,
                limit,
            )
    }

private fun querySpecForStreamPartitionReader(
    stream: Stream,
    checkpointColumns: List<Field>,
    checkpointLowerBound: List<JsonNode>?,
    isLowerBoundIncluded: Boolean,
    checkpointUpperBound: List<JsonNode>?,
    isOrdered: Boolean,
    limit: Long?,
): SelectQuerySpec {
    val selectColumns: List<Field> =
        if (isOrdered) {
            stream.fields + checkpointColumns
        } else {
            stream.fields
        }
    val zippedLowerBound: List<Pair<Field, JsonNode>> =
        checkpointLowerBound?.let { checkpointColumns.zip(it) } ?: listOf()
    val lowerBoundDisj: List<WhereClauseNode> =
        zippedLowerBound.mapIndexed { idx: Int, (gtCol: Field, gtValue: JsonNode) ->
            val lastLeaf: WhereClauseLeafNode =
                if (isLowerBoundIncluded && idx == checkpointColumns.size - 1) {
                    GreaterOrEqual(gtCol, gtValue)
                } else {
                    Greater(gtCol, gtValue)
                }
            And(
                zippedLowerBound.take(idx).map { (eqCol: Field, eqValue: JsonNode) ->
                    Equal(eqCol, eqValue)
                } + listOf(lastLeaf),
            )
        }
    val zippedUpperBound: List<Pair<Field, JsonNode>> =
        checkpointUpperBound?.let { checkpointColumns.zip(it) } ?: listOf()
    val upperBoundDisj: List<WhereClauseNode> =
        zippedUpperBound.mapIndexed { idx: Int, (leqCol: Field, leqValue: JsonNode) ->
            val lastLeaf: WhereClauseLeafNode =
                if (idx < zippedUpperBound.size - 1) {
                    Lesser(leqCol, leqValue)
                } else {
                    LesserOrEqual(leqCol, leqValue)
                }
            And(
                zippedUpperBound.take(idx).map { (eqCol: Field, eqValue: JsonNode) ->
                    Equal(eqCol, eqValue)
                } + listOf(lastLeaf),
            )
        }
    return SelectQuerySpec(
        SelectColumns(selectColumns),
        From(stream.name, stream.namespace),
        Where(And(Or(lowerBoundDisj), Or(upperBoundDisj))),
        if (isOrdered) OrderBy(checkpointColumns) else NoOrderBy,
        if (limit == null) NoLimit else Limit(limit),
    )
}

/**
 * Generates a [CheckpointStreamState] using the [StreamPartitionReader.Input] initial state and, if
 * provided, the last record read by the [StreamPartitionReader]. When not provided, the partition
 * is presumed to have been read in its entirety.
 */
fun StreamPartitionReader.Input.checkpoint(row: ObjectNode? = null): CheckpointStreamState {
    fun getRowValue(field: Field): JsonNode = row?.get(field.id) ?: Jsons.nullNode()
    return when (this) {
        is StreamPartitionReader.SnapshotInput ->
            if (row != null) {
                SnapshotCheckpoint(primaryKey, primaryKey.map(::getRowValue))
            } else if (primaryKeyUpperBound != null) {
                SnapshotCheckpoint(primaryKey, primaryKeyUpperBound)
            } else {
                SnapshotCompleted
            }
        is StreamPartitionReader.SnapshotWithCursorInput ->
            if (row != null) {
                SnapshotWithCursorCheckpoint(
                    primaryKey,
                    primaryKey.map(::getRowValue),
                    cursor,
                    cursorUpperBound,
                )
            } else if (primaryKeyUpperBound != null) {
                SnapshotWithCursorCheckpoint(
                    primaryKey,
                    primaryKeyUpperBound,
                    cursor,
                    cursorUpperBound,
                )
            } else {
                CursorIncrementalCheckpoint(cursor, cursorUpperBound)
            }
        is StreamPartitionReader.CursorIncrementalInput ->
            if (row == null) {
                CursorIncrementalCheckpoint(cursor, cursorUpperBound)
            } else {
                CursorIncrementalCheckpoint(cursor, getRowValue(cursor))
            }
    }
}
