/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.protocol.models.v0.SyncMode

/** Default implementation of [PartitionsCreator] for streams in JDBC sources. */
class StreamPartitionsCreator(
    val ctx: StreamReadContext,
    val input: Input,
    val parameters: Parameters,
    val readerParameters: StreamPartitionReader.Parameters,
) : PartitionsCreator {
    sealed interface Input

    data object NoStart : Input

    data class SnapshotColdStart(
        val primaryKey: List<Field>,
    ) : Input

    data class SnapshotWithCursorColdStart(
        val primaryKey: List<Field>,
        val cursor: Field,
    ) : Input

    data class CursorIncrementalColdStart(
        val cursor: Field,
        val cursorLowerBound: JsonNode,
    ) : Input

    data class SnapshotWarmStart(
        val primaryKey: List<Field>,
        val primaryKeyLowerBound: List<JsonNode>,
    ) : Input

    data class SnapshotWithCursorWarmStart(
        val primaryKey: List<Field>,
        val primaryKeyLowerBound: List<JsonNode>,
        val cursor: Field,
        val cursorUpperBound: JsonNode,
    ) : Input

    data class CursorIncrementalWarmStart(
        val cursor: Field,
        val cursorLowerBound: JsonNode,
        val cursorUpperBound: JsonNode,
    ) : Input

    data class Parameters(
        val preferParallelized: Boolean,
        val tableSampleSize: Int = 1024,
        val throughputBytesPerSecond: Long = 10L * 1024L * 1024L,
    )

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus =
        // Running this PartitionsCreator may not always involve JDBC queries.
        // In those cases, the semaphore will be released very soon after, so this is OK.
        if (ctx.querySemaphore.tryAcquire()) {
            PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN
        } else {
            PartitionsCreator.TryAcquireResourcesStatus.RETRY_LATER
        }

    override fun releaseResources() {
        ctx.querySemaphore.release()
    }

    override suspend fun run(): List<PartitionReader> =
        input.partitionReaderInputs().map { StreamPartitionReader(ctx, it, readerParameters) }

    fun Input.partitionReaderInputs(): List<StreamPartitionReader.Input> {
        return when (this) {
            is NoStart -> listOf()
            is SnapshotColdStart ->
                StreamPartitionReader.SnapshotInput(
                        primaryKey = primaryKey,
                        primaryKeyLowerBound = null,
                        primaryKeyUpperBound = null,
                    )
                    .split()
            is SnapshotWithCursorColdStart ->
                StreamPartitionReader.SnapshotWithCursorInput(
                        primaryKey = primaryKey,
                        primaryKeyLowerBound = null,
                        primaryKeyUpperBound = null,
                        cursor = cursor,
                        cursorUpperBound = utils.computeCursorUpperBound(cursor) ?: return listOf(),
                    )
                    .split()
            is CursorIncrementalColdStart ->
                StreamPartitionReader.CursorIncrementalInput(
                        cursor = cursor,
                        cursorLowerBound = cursorLowerBound,
                        cursorUpperBound = utils.computeCursorUpperBound(cursor) ?: return listOf(),
                    )
                    .split()
            is SnapshotWarmStart ->
                StreamPartitionReader.SnapshotInput(
                        primaryKey = primaryKey,
                        primaryKeyLowerBound = primaryKeyLowerBound,
                        primaryKeyUpperBound = null,
                    )
                    .split()
            is SnapshotWithCursorWarmStart ->
                StreamPartitionReader.SnapshotWithCursorInput(
                        primaryKey = primaryKey,
                        primaryKeyLowerBound = primaryKeyLowerBound,
                        primaryKeyUpperBound = null,
                        cursor = cursor,
                        cursorUpperBound = cursorUpperBound,
                    )
                    .split()
            is CursorIncrementalWarmStart ->
                StreamPartitionReader.CursorIncrementalInput(
                        cursor = cursor,
                        cursorLowerBound = cursorLowerBound,
                        cursorUpperBound = cursorUpperBound,
                    )
                    .split()
        }
    }

    fun StreamPartitionReader.SnapshotInput.split(): List<StreamPartitionReader.SnapshotInput> =
        utils.split(this, primaryKeyLowerBound, primaryKeyUpperBound).map { (lb, ub) ->
            copy(primaryKeyLowerBound = lb, primaryKeyUpperBound = ub)
        }

    fun StreamPartitionReader.SnapshotWithCursorInput.split():
        List<StreamPartitionReader.SnapshotWithCursorInput> =
        utils.split(this, primaryKeyLowerBound, primaryKeyUpperBound).map { (lb, ub) ->
            copy(primaryKeyLowerBound = lb, primaryKeyUpperBound = ub)
        }

    fun StreamPartitionReader.CursorIncrementalInput.split():
        List<StreamPartitionReader.CursorIncrementalInput> =
        utils.split(this, listOf(cursorLowerBound), listOf(cursorUpperBound)).map { (lb, ub) ->
            copy(cursorLowerBound = lb!!.first(), cursorUpperBound = ub!!.first())
        }

    private val utils = StreamPartitionsCreatorUtils(ctx, parameters)
}

/** Converts a nullable [OpaqueStateValue] into an input for [StreamPartitionsCreator]. */
fun OpaqueStateValue?.streamPartitionsCreatorInput(
    ctx: StreamReadContext,
): StreamPartitionsCreator.Input {
    val checkpoint: CheckpointStreamState? = checkpoint(ctx)
    if (checkpoint == null && this != null) {
        ctx.resetStream()
    }
    return checkpoint.streamPartitionsCreatorInput(ctx)
}

/** Converts a nullable [CheckpointStreamState] into an input for [StreamPartitionsCreator]. */
fun CheckpointStreamState?.streamPartitionsCreatorInput(
    ctx: StreamReadContext,
): StreamPartitionsCreator.Input {
    if (this == null) {
        val pkChosenFromCatalog: List<Field> = ctx.stream.configuredPrimaryKey ?: listOf()
        if (ctx.stream.configuredSyncMode == SyncMode.FULL_REFRESH || ctx.configuration.global) {
            return StreamPartitionsCreator.SnapshotColdStart(pkChosenFromCatalog)
        }
        val cursorChosenFromCatalog: Field =
            ctx.stream.configuredCursor as? Field ?: throw ConfigErrorException("no cursor")
        return StreamPartitionsCreator.SnapshotWithCursorColdStart(
            pkChosenFromCatalog,
            cursorChosenFromCatalog,
        )
    }
    return when (this) {
        SnapshotCompleted -> StreamPartitionsCreator.NoStart
        is SnapshotCheckpoint ->
            StreamPartitionsCreator.SnapshotWarmStart(
                primaryKey,
                primaryKeyCheckpoint,
            )
        is SnapshotWithCursorCheckpoint ->
            StreamPartitionsCreator.SnapshotWithCursorWarmStart(
                primaryKey,
                primaryKeyCheckpoint,
                cursor,
                cursorUpperBound,
            )
        is CursorIncrementalCheckpoint ->
            when (val cursorUpperBound: JsonNode? = ctx.transientCursorUpperBoundState.get()) {
                null ->
                    StreamPartitionsCreator.CursorIncrementalColdStart(
                        cursor,
                        cursorCheckpoint,
                    )
                else ->
                    if (cursorCheckpoint == cursorUpperBound) {
                        StreamPartitionsCreator.NoStart
                    } else {
                        StreamPartitionsCreator.CursorIncrementalWarmStart(
                            cursor,
                            cursorCheckpoint,
                            cursorUpperBound,
                        )
                    }
            }
    }
}
