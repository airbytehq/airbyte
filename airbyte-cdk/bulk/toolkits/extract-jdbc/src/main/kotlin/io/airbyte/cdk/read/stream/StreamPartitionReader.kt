/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read.stream

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.read.LimitState
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.source.Field
import io.airbyte.cdk.source.PartitionReadCheckpoint
import io.airbyte.cdk.source.PartitionReader
import io.airbyte.cdk.source.select.And
import io.airbyte.cdk.source.select.Equal
import io.airbyte.cdk.source.select.From
import io.airbyte.cdk.source.select.Greater
import io.airbyte.cdk.source.select.Lesser
import io.airbyte.cdk.source.select.LesserOrEqual
import io.airbyte.cdk.source.select.Limit
import io.airbyte.cdk.source.select.NoLimit
import io.airbyte.cdk.source.select.NoOrderBy
import io.airbyte.cdk.source.select.Or
import io.airbyte.cdk.source.select.OrderBy
import io.airbyte.cdk.source.select.SelectColumns
import io.airbyte.cdk.source.select.SelectQuerier
import io.airbyte.cdk.source.select.SelectQuery
import io.airbyte.cdk.source.select.SelectQuerySpec
import io.airbyte.cdk.source.select.Where
import io.airbyte.cdk.source.select.WhereClauseLeafNode
import io.airbyte.cdk.source.select.WhereClauseNode
import io.airbyte.cdk.source.select.optimize
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlin.coroutines.coroutineContext
import kotlinx.coroutines.ensureActive

/** Default implementation of [PartitionReader] for streams in JDBC sources. */
class StreamPartitionReader(
    val ctx: StreamReadContext,
    val input: Input,
    val parameters: Parameters,
) : PartitionReader {
    sealed interface Input

    data class SnapshotInput(
        val primaryKey: List<Field>,
        val primaryKeyLowerBound: List<JsonNode>?,
        val primaryKeyUpperBound: List<JsonNode>?,
    ) : Input

    data class SnapshotWithCursorInput(
        val primaryKey: List<Field>,
        val primaryKeyLowerBound: List<JsonNode>?,
        val primaryKeyUpperBound: List<JsonNode>?,
        val cursor: Field,
        val cursorUpperBound: JsonNode,
    ) : Input

    data class CursorIncrementalInput(
        val cursor: Field,
        val cursorLowerBound: JsonNode,
        val cursorUpperBound: JsonNode,
    ) : Input

    data class Parameters(
        val preferResumable: Boolean,
    )

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus =
        if (ctx.querySemaphore.tryAcquire()) {
            PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
        } else {
            PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        }

    override fun releaseResources() {
        ctx.querySemaphore.release()
    }

    val resumable: Boolean =
        parameters.preferResumable &&
            when (input) {
                is SnapshotInput -> input.primaryKey.isNotEmpty()
                is SnapshotWithCursorInput -> input.primaryKey.isNotEmpty()
                is CursorIncrementalInput -> true
            }

    val incumbentTransientState = AtomicReference<TransientState>()
    val numRecords = AtomicLong()
    val lastRecord = AtomicReference<ObjectNode?>(null)
    val runComplete = AtomicBoolean(false)

    override suspend fun run() {
        // Store the transient state at the start of the run for use in checkpoint().
        val transientState =
            TransientState(ctx.transientLimitState.get(), ctx.transientFetchSize.get())
        incumbentTransientState.set(transientState)
        // Build the query.
        val querySpec: SelectQuerySpec =
            input.querySpec(
                ctx.stream,
                isOrdered = resumable,
                limit = transientState.limit.takeIf { resumable },
            )
        val query: SelectQuery = ctx.selectQueryGenerator.generate(querySpec.optimize())
        val streamFieldNames: List<String> = ctx.stream.fields.map { it.id }
        val querierParameters = SelectQuerier.Parameters(fetchSize = transientState.fetchSize)
        // Execute the query.
        ctx.selectQuerier.executeQuery(query, querierParameters).use { result: SelectQuerier.Result
            ->
            for (record in result) {
                val dataRecord: JsonNode =
                    Jsons.objectNode().apply {
                        for (fieldName in streamFieldNames) {
                            set<JsonNode>(fieldName, record[fieldName] ?: Jsons.nullNode())
                        }
                    }
                ctx.outputConsumer.accept(
                    AirbyteRecordMessage()
                        .withStream(ctx.stream.name)
                        .withNamespace(ctx.stream.namespace)
                        .withData(dataRecord),
                )
                lastRecord.set(record)
                numRecords.incrementAndGet()
                // If progress can be checkpointed at any time,
                // check activity periodically to handle timeout.
                if (!resumable) continue
                if (numRecords.get() % transientState.fetchSizeOrLowerBound != 0L) continue
                coroutineContext.ensureActive()
            }
        }
        runComplete.set(true)
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        val checkpointState: CheckpointStreamState
        val transientState: TransientState = incumbentTransientState.get()
        if (!runComplete.get()) {
            // Sanity check.
            if (!resumable) throw RuntimeException("cannot checkpoint non-resumable read")
            // The run method execution was interrupted.
            checkpointState = input.checkpoint(lastRecord.get())
            // Decrease the limit clause for the next PartitionReader, because it's too big.
            // If it had been smaller then run might have completed in time.
            ctx.transientLimitState.update {
                if (transientState.limitState.current <= it.current) it.down else it
            }
        } else if (resumable) {
            // The run method executed to completion with a LIMIT clause.
            // The partition boundary may or may not have been reached.
            // If the number of records read is less than the LIMIT clause,
            // then it certainly has.
            checkpointState =
                if (numRecords.get() < transientState.limit) {
                    input.checkpoint()
                } else {
                    input.checkpoint(lastRecord.get())
                }
            // Increase the limit clause for the next PartitionReader, because it's too small.
            // If it had been bigger then run might have executed for longer.
            ctx.transientLimitState.update {
                if (it.current <= transientState.limitState.current) it.up else it
            }
        } else {
            // The run method executed to completion without a LIMIT clause.
            // This implies that the partition boundary has been reached.
            checkpointState = input.checkpoint()
        }
        return PartitionReadCheckpoint(checkpointState.opaqueStateValue(), numRecords.get())
    }

    inner class TransientState(
        val limitState: LimitState,
        val fetchSize: Int?,
    ) {
        val fetchSizeOrLowerBound: Int
            get() = fetchSize ?: MemoryFetchSizeEstimator.FETCH_SIZE_LOWER_BOUND

        /** Value to use for the LIMIT clause, if applicable. */
        val limit: Long
            get() = fetchSizeOrLowerBound * limitState.current
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
                checkpointUpperBound = primaryKeyUpperBound,
                isOrdered,
                limit,
            )
        is StreamPartitionReader.SnapshotWithCursorInput ->
            querySpecForStreamPartitionReader(
                stream,
                checkpointColumns = primaryKey,
                checkpointLowerBound = primaryKeyLowerBound,
                checkpointUpperBound = primaryKeyUpperBound,
                isOrdered,
                limit,
                extraConjWhereClauses = arrayOf(LesserOrEqual(cursor, cursorUpperBound)),
            )
        is StreamPartitionReader.CursorIncrementalInput ->
            querySpecForStreamPartitionReader(
                stream,
                checkpointColumns = listOf(cursor),
                checkpointLowerBound = listOf(cursorLowerBound),
                checkpointUpperBound = listOf(cursorUpperBound),
                isOrdered,
                limit,
            )
    }

private fun querySpecForStreamPartitionReader(
    stream: Stream,
    checkpointColumns: List<Field>,
    checkpointLowerBound: List<JsonNode>?,
    checkpointUpperBound: List<JsonNode>?,
    isOrdered: Boolean,
    limit: Long?,
    vararg extraConjWhereClauses: WhereClauseNode,
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
            val lastLeaf: WhereClauseLeafNode = Greater(gtCol, gtValue)
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
    val whereClause = And(listOf(Or(lowerBoundDisj), Or(upperBoundDisj)) + extraConjWhereClauses)
    return SelectQuerySpec(
        SelectColumns(selectColumns),
        From(stream.name, stream.namespace),
        Where(whereClause),
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
