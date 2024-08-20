/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.output.CatalogValidationFailureHandler
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.output.ResetStream
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicReference
import kotlin.random.Random

/** Base class for JDBC implementations of [PartitionsCreator]. */
sealed class JdbcPartitionsCreator(
    val selectQueryGenerator: SelectQueryGenerator,
    val streamState: JdbcStreamState<*>,
    val input: Input,
) : PartitionsCreator {
    private val log = KotlinLogging.logger {}

    val stream: Stream = streamState.stream
    val sharedState: JdbcSharedState = streamState.sharedState
    val outputConsumer: OutputConsumer = sharedState.outputConsumer
    val selectQuerier: SelectQuerier = sharedState.selectQuerier

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

    private val acquiredResources = AtomicReference<AcquiredResources>()

    /** Calling [close] releases the resources acquired for the [JdbcPartitionsCreator]. */
    fun interface AcquiredResources : AutoCloseable

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus {
        val acquiredResources: AcquiredResources =
            sharedState.tryAcquireResourcesForCreator()
                ?: return PartitionsCreator.TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredResources.set(acquiredResources)
        return PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run(): List<PartitionReader> =
        input.partitionReaderInputs().map { createReader(it) }

    abstract fun createReader(input: JdbcPartitionReader.Input): JdbcPartitionReader

    fun Input.partitionReaderInputs(): List<JdbcPartitionReader.Input> {
        return when (this) {
            is NoStart -> listOf()
            is SnapshotColdStart ->
                JdbcPartitionReader.SnapshotInput(
                        primaryKey = primaryKey,
                        primaryKeyLowerBound = null,
                        primaryKeyUpperBound = null,
                    )
                    .split()
            is SnapshotWithCursorColdStart ->
                JdbcPartitionReader.SnapshotWithCursorInput(
                        primaryKey = primaryKey,
                        primaryKeyLowerBound = null,
                        primaryKeyUpperBound = null,
                        cursor = cursor,
                        cursorUpperBound = ensureCursorUpperBound(cursor) ?: return listOf(),
                    )
                    .split()
            is CursorIncrementalColdStart ->
                JdbcPartitionReader.CursorIncrementalInput(
                        cursor = cursor,
                        cursorLowerBound = cursorLowerBound,
                        isLowerBoundIncluded = true,
                        cursorUpperBound = ensureCursorUpperBound(cursor) ?: return listOf(),
                    )
                    .split()
            is SnapshotWarmStart ->
                JdbcPartitionReader.SnapshotInput(
                        primaryKey = primaryKey,
                        primaryKeyLowerBound = primaryKeyLowerBound,
                        primaryKeyUpperBound = null,
                    )
                    .split()
            is SnapshotWithCursorWarmStart ->
                JdbcPartitionReader.SnapshotWithCursorInput(
                        primaryKey = primaryKey,
                        primaryKeyLowerBound = primaryKeyLowerBound,
                        primaryKeyUpperBound = null,
                        cursor = cursor,
                        cursorUpperBound = cursorUpperBound,
                    )
                    .split()
            is CursorIncrementalWarmStart ->
                JdbcPartitionReader.CursorIncrementalInput(
                        cursor = cursor,
                        cursorLowerBound = cursorLowerBound,
                        isLowerBoundIncluded = true,
                        cursorUpperBound = cursorUpperBound,
                    )
                    .split()
        }
    }

    fun JdbcPartitionReader.SnapshotInput.split(): List<JdbcPartitionReader.SnapshotInput> =
        split(this, primaryKeyLowerBound, primaryKeyUpperBound).map { (lb, ub) ->
            copy(primaryKeyLowerBound = lb, primaryKeyUpperBound = ub)
        }

    fun JdbcPartitionReader.SnapshotWithCursorInput.split():
        List<JdbcPartitionReader.SnapshotWithCursorInput> =
        split(this, primaryKeyLowerBound, primaryKeyUpperBound).map { (lb, ub) ->
            copy(primaryKeyLowerBound = lb, primaryKeyUpperBound = ub)
        }

    fun JdbcPartitionReader.CursorIncrementalInput.split():
        List<JdbcPartitionReader.CursorIncrementalInput> =
        split(this, listOf(cursorLowerBound), listOf(cursorUpperBound)).mapIndexed {
            idx: Int,
            (lb, ub) ->
            copy(
                cursorLowerBound = lb!!.first(),
                isLowerBoundIncluded = idx == 0,
                cursorUpperBound = ub!!.first(),
            )
        }

    abstract fun split(
        input: JdbcPartitionReader.Input,
        globalLowerBound: List<JsonNode>?,
        globalUpperBound: List<JsonNode>?,
    ): List<Pair<List<JsonNode>?, List<JsonNode>?>>

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.close()
    }

    fun ensureCursorUpperBound(cursor: Field): JsonNode? {
        if (streamState.cursorUpperBound != null) {
            return streamState.cursorUpperBound
        }
        val querySpec =
            SelectQuerySpec(
                SelectColumnMaxValue(cursor),
                From(stream.name, stream.namespace),
            )
        val cursorUpperBoundQuery: SelectQuery = selectQueryGenerator.generate(querySpec.optimize())
        log.info { "Querying maximum cursor column value." }
        val record: ObjectNode? =
            selectQuerier.executeQuery(cursorUpperBoundQuery).use {
                if (it.hasNext()) it.next() else null
            }
        val cursorUpperBound: JsonNode? = record?.fields()?.asSequence()?.firstOrNull()?.value
        if (cursorUpperBound == null) {
            streamState.cursorUpperBound = Jsons.nullNode()
            log.warn { "No cursor column value found in '${stream.label}'." }
            return null
        }
        streamState.cursorUpperBound = cursorUpperBound
        if (cursorUpperBound.isNull) {
            log.warn { "Maximum cursor column value in '${stream.label}' is NULL." }
            return null
        }
        log.info { "Maximum cursor column value in '${stream.label}' is '$cursorUpperBound'." }
        return cursorUpperBound
    }

    /** Collects a sample of rows in the unsplit partition. */
    fun <T> collectSample(
        querySpec: SelectQuerySpec,
        recordMapper: (ObjectNode) -> T,
    ): Sample<T> {
        val values = mutableListOf<T>()
        var previousWeight = 0L
        for (sampleRateInvPow2 in listOf(16, 8, 0)) {
            val sampleRateInv: Long = 1L shl sampleRateInvPow2
            log.info { "Sampling stream '${stream.label}' at rate 1 / $sampleRateInv." }
            // First, try sampling the table at a rate of one every 2^16 = 65_536 rows.
            // If that's not enough to produce the desired number of sampled rows (1024 by default)
            // then try sampling at a higher rate of one every 2^8 = 256 rows.
            // If that's still not enough, don't sample at all.
            values.clear()
            val fromSample =
                FromSample(
                    stream.name,
                    stream.namespace,
                    sampleRateInvPow2,
                    sharedState.maxSampleSize,
                )
            val sampledQuerySpec: SelectQuerySpec = querySpec.copy(from = fromSample)
            val samplingQuery: SelectQuery =
                selectQueryGenerator.generate(sampledQuerySpec.optimize())
            selectQuerier.executeQuery(samplingQuery).use {
                for (record in it) {
                    values.add(recordMapper(record))
                }
            }
            if (values.size < sharedState.maxSampleSize) {
                previousWeight = sampleRateInv * values.size / sharedState.maxSampleSize
                continue
            }
            val kind: Sample.Kind =
                when (sampleRateInvPow2) {
                    16 -> Sample.Kind.LARGE
                    8 -> Sample.Kind.MEDIUM
                    else -> Sample.Kind.SMALL
                }
            log.info { "Sampled ${values.size} rows in ${kind.name} stream '${stream.label}'." }
            return Sample(values, kind, previousWeight.coerceAtLeast(sampleRateInv))
        }
        val kind: Sample.Kind = if (values.isEmpty()) Sample.Kind.EMPTY else Sample.Kind.TINY
        log.info { "Sampled ${values.size} rows in ${kind.name} stream '${stream.label}'." }
        return Sample(values, kind, if (values.isEmpty()) 0L else 1L)
    }
}

/** Sequential JDBC implementation of [PartitionsCreator]. */
class JdbcSequentialPartitionsCreator(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: JdbcStreamState<*>,
    input: Input,
) : JdbcPartitionsCreator(selectQueryGenerator, streamState, input) {
    private val log = KotlinLogging.logger {}

    override fun createReader(input: JdbcPartitionReader.Input): JdbcPartitionReader {
        // Handle edge case where the partition cannot be split.
        if (!input.resumable) {
            log.warn {
                "Table cannot be read by sequential partition reader because it cannot be split."
            }
            return JdbcNonResumablePartitionReader(selectQueryGenerator, streamState, input)
        }
        // Happy path.
        log.info { "Table will be read by sequential partition reader(s)." }
        return JdbcResumablePartitionReader(selectQueryGenerator, streamState, input)
    }

    override fun split(
        input: JdbcPartitionReader.Input,
        globalLowerBound: List<JsonNode>?,
        globalUpperBound: List<JsonNode>?
    ): List<Pair<List<JsonNode>?, List<JsonNode>?>> {
        return listOf(globalLowerBound to globalUpperBound)
    }
}

/** Concurrent JDBC implementation of [PartitionsCreator]. */
class JdbcConcurrentPartitionsCreator(
    selectQueryGenerator: SelectQueryGenerator,
    streamState: JdbcStreamState<*>,
    input: Input,
) : JdbcPartitionsCreator(selectQueryGenerator, streamState, input) {
    private val log = KotlinLogging.logger {}

    override fun createReader(input: JdbcPartitionReader.Input): JdbcPartitionReader =
        JdbcNonResumablePartitionReader(selectQueryGenerator, streamState, input)

    override fun split(
        input: JdbcPartitionReader.Input,
        globalLowerBound: List<JsonNode>?,
        globalUpperBound: List<JsonNode>?
    ): List<Pair<List<JsonNode>?, List<JsonNode>?>> {
        // Handle edge case where the table can't be sampled.
        if (!sharedState.withSampling) {
            log.warn {
                "Table cannot be read by concurrent partition readers because it cannot be sampled."
            }
            // TODO: adaptive fetchSize computation?
            return listOf(globalLowerBound to globalUpperBound)
        }
        // Sample the table for partition split boundaries and for record byte sizes.
        val unsplitQuerySpec: SelectQuerySpec =
            input.querySpec(stream, isOrdered = true, limit = null)
        val checkpointColumns: List<Field> = (unsplitQuerySpec.orderBy as OrderBy).columns
        val sample: Sample<Pair<List<JsonNode>, Long>> =
            collectSample(unsplitQuerySpec) { record: ObjectNode ->
                val checkpointValues: List<JsonNode> =
                    checkpointColumns.map { record[it.id] ?: Jsons.nullNode() }
                val rowByteSize: Long = sharedState.rowByteSizeEstimator().apply(record)
                checkpointValues to rowByteSize
            }
        if (sample.kind == Sample.Kind.EMPTY) {
            log.info { "Sampling query found that the table was empty." }
            return listOf()
        }
        val rowByteSizeSample: Sample<Long> = sample.map { (_, rowByteSize: Long) -> rowByteSize }
        streamState.fetchSize = sharedState.jdbcFetchSizeEstimator().apply(rowByteSizeSample)
        val expectedTableByteSize: Long = rowByteSizeSample.sampledValues.sum() * sample.valueWeight
        log.info { "Table memory size estimated at ${expectedTableByteSize shr 20} MiB." }
        // Handle edge case where the table can't be split.
        if (!input.resumable) {
            log.warn {
                "Table cannot be read by concurrent partition readers because it cannot be split."
            }
            return listOf(globalLowerBound to globalUpperBound)
        }
        // Happy path.
        log.info { "Target partition size is ${sharedState.targetPartitionByteSize shr 20} MiB." }
        val secondarySamplingRate: Double =
            if (expectedTableByteSize <= sharedState.targetPartitionByteSize) {
                0.0
            } else {
                val expectedPartitionByteSize: Long =
                    expectedTableByteSize / sharedState.maxSampleSize
                if (expectedPartitionByteSize < sharedState.targetPartitionByteSize) {
                    expectedPartitionByteSize.toDouble() / sharedState.targetPartitionByteSize
                } else {
                    1.0
                }
            }
        val random = Random(expectedTableByteSize) // RNG output is repeatable.
        val innerSplitBoundaries: List<List<JsonNode>> =
            sample.sampledValues
                .filter { random.nextDouble() < secondarySamplingRate }
                .map { (splitBoundary: List<JsonNode>, _) -> splitBoundary }
                .distinct()
        log.info {
            "Table will be read by ${innerSplitBoundaries.size + 1} concurrent partition reader(s)."
        }
        val lbs: List<List<JsonNode>?> = listOf(globalLowerBound) + innerSplitBoundaries
        val ubs: List<List<JsonNode>?> = innerSplitBoundaries + listOf(globalUpperBound)
        return lbs.zip(ubs)
    }
}

/** Converts a nullable [OpaqueStateValue] into an input for [JdbcPartitionsCreator]. */
fun OpaqueStateValue?.streamPartitionsCreatorInput(
    handler: CatalogValidationFailureHandler,
    streamState: JdbcStreamState<*>,
): JdbcPartitionsCreator.Input {
    val checkpoint: CheckpointStreamState? = checkpoint(handler, streamState)
    if (checkpoint == null && this != null) {
        handler.accept(ResetStream(streamState.stream.name, streamState.stream.namespace))
        streamState.reset()
    }
    return checkpoint.streamPartitionsCreatorInput(streamState)
}

/** Converts a nullable [CheckpointStreamState] into an input for [JdbcPartitionsCreator]. */
fun CheckpointStreamState?.streamPartitionsCreatorInput(
    streamState: JdbcStreamState<*>,
): JdbcPartitionsCreator.Input {
    val stream: Stream = streamState.stream
    val sharedState: JdbcSharedState = streamState.sharedState
    val configuration: JdbcSourceConfiguration = sharedState.configuration
    if (this == null) {
        val pkChosenFromCatalog: List<Field> = stream.configuredPrimaryKey ?: listOf()
        if (stream.configuredSyncMode == SyncMode.FULL_REFRESH || configuration.global) {
            return JdbcPartitionsCreator.SnapshotColdStart(pkChosenFromCatalog)
        }
        val cursorChosenFromCatalog: Field =
            stream.configuredCursor as? Field ?: throw ConfigErrorException("no cursor")
        return JdbcPartitionsCreator.SnapshotWithCursorColdStart(
            pkChosenFromCatalog,
            cursorChosenFromCatalog,
        )
    }
    return when (this) {
        SnapshotCompleted -> JdbcPartitionsCreator.NoStart
        is SnapshotCheckpoint ->
            JdbcPartitionsCreator.SnapshotWarmStart(
                primaryKey,
                primaryKeyCheckpoint,
            )
        is SnapshotWithCursorCheckpoint ->
            JdbcPartitionsCreator.SnapshotWithCursorWarmStart(
                primaryKey,
                primaryKeyCheckpoint,
                cursor,
                cursorUpperBound,
            )
        is CursorIncrementalCheckpoint ->
            when (val cursorUpperBound: JsonNode? = streamState.cursorUpperBound) {
                null ->
                    JdbcPartitionsCreator.CursorIncrementalColdStart(
                        cursor,
                        cursorCheckpoint,
                    )
                else ->
                    if (cursorCheckpoint == cursorUpperBound) {
                        JdbcPartitionsCreator.NoStart
                    } else {
                        JdbcPartitionsCreator.CursorIncrementalWarmStart(
                            cursor,
                            cursorCheckpoint,
                            cursorUpperBound,
                        )
                    }
            }
    }
}
