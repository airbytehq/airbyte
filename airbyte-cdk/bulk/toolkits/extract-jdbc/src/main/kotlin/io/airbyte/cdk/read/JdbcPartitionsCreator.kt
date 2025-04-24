/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicReference
import kotlin.random.Random

/** Base class for JDBC implementations of [PartitionsCreator]. */
sealed class JdbcPartitionsCreator<
    A : JdbcSharedState,
    S : JdbcStreamState<A>,
    P : JdbcPartition<S>,
>(
    val partition: P,
    val partitionFactory: JdbcPartitionFactory<A, S, P>,
) : PartitionsCreator {
    private val log = KotlinLogging.logger {}

    val streamState: S = partition.streamState
    val stream: Stream = streamState.stream
    val sharedState: A = streamState.sharedState
    val configuration: JdbcSourceConfiguration = sharedState.configuration
    val selectQuerier: SelectQuerier = sharedState.selectQuerier

    private val acquiredResources = AtomicReference<AcquiredResources>()

    // A reader that only checkpoints the complete state of a partition
    // used for empty tables
    inner class CheckpointOnlyPartitionReader() : PartitionReader {
        override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus =
            PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN

        override suspend fun run() {}

        override fun checkpoint(): PartitionReadCheckpoint =
            PartitionReadCheckpoint(partition.completeState, 0)

        override fun releaseResources() {}
    }

    /** Calling [close] releases the resources acquired for the [JdbcPartitionsCreator]. */
    fun interface AcquiredResources : AutoCloseable

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus {
        val acquiredResources: AcquiredResources =
            partition.tryAcquireResourcesForCreator()
                ?: return PartitionsCreator.TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredResources.set(acquiredResources)
        return PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.close()
    }

    fun ensureCursorUpperBound() {
        val cursorUpperBoundQuery: SelectQuery =
            (partition as JdbcCursorPartition<*>).cursorUpperBoundQuery
        if (streamState.cursorUpperBound != null) {
            return
        }
        log.info { "Querying maximum cursor column value." }
        val record: ObjectNode? =
            selectQuerier.executeQuery(cursorUpperBoundQuery).use {
                if (it.hasNext()) it.next().data else null
            }
        if (record == null) {
            streamState.cursorUpperBound = Jsons.nullNode()
            return
        }
        val cursorUpperBound: JsonNode? =
            Jsons.valueToTree(record.fields().asSequence().firstOrNull()?.value)
        if (cursorUpperBound == null) {
            log.warn { "No cursor column value found in '${stream.label}'." }
            return
        }
        if (cursorUpperBound.isNull) {
            log.warn { "Maximum cursor column value in '${stream.label}' is NULL." }
            return
        }
        log.info { "Maximum cursor column value in '${stream.label}' is '$cursorUpperBound'." }
        streamState.cursorUpperBound = cursorUpperBound
    }

    /** Collects a sample of rows in the unsplit partition. */
    fun <T> collectSample(
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
            val samplingQuery: SelectQuery = partition.samplingQuery(sampleRateInvPow2)
            selectQuerier.executeQuery(samplingQuery).use {
                for (row in it) {
                    values.add(recordMapper(row.data))
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
class JdbcSequentialPartitionsCreator<
    A : JdbcSharedState,
    S : JdbcStreamState<A>,
    P : JdbcPartition<S>,
>(
    partition: P,
    partitionFactory: JdbcPartitionFactory<A, S, P>,
) : JdbcPartitionsCreator<A, S, P>(partition, partitionFactory) {
    private val log = KotlinLogging.logger {}

    override suspend fun run(): List<PartitionReader> {
        // Ensure that the cursor upper bound is known, if required.
        if (partition is JdbcCursorPartition<*>) {
            ensureCursorUpperBound()
            if (
                streamState.cursorUpperBound == null || streamState.cursorUpperBound?.isNull == true
            ) {
                log.info { "Maximum cursor column value query found that the table was empty." }
                return listOf(CheckpointOnlyPartitionReader())
            }
        }
        if (streamState.fetchSize == null) {
            if (sharedState.withSampling) {
                val rowByteSizeSample: Sample<Long> =
                    collectSample(sharedState.rowByteSizeEstimator()::apply)
                val expectedTableByteSize: Long =
                    rowByteSizeSample.sampledValues.sum() * rowByteSizeSample.valueWeight
                log.info { "Table memory size estimated at ${expectedTableByteSize shr 20} MiB." }
                if (rowByteSizeSample.kind == Sample.Kind.EMPTY) {
                    log.info { "Sampling query found that the table was empty." }
                    // An empty table will checkpoint once in order to emit its complete state
                    // Otherwise on each sync we would try to read this partition
                    return listOf(CheckpointOnlyPartitionReader())
                }
                streamState.fetchSize =
                    sharedState.jdbcFetchSizeEstimator().apply(rowByteSizeSample)
            } else {
                // TODO: adaptive fetchSize computation?
            }
        }
        // Handle edge case where the partition cannot be split.
        if (partition !is JdbcSplittablePartition<*>) {
            log.warn {
                "Table cannot be read by sequential partition reader because it cannot be split."
            }
            return listOf(JdbcNonResumablePartitionReader(partition))
        }
        // Happy path.
        log.info { "Table will be read by sequential partition reader(s)." }
        return listOf(JdbcResumablePartitionReader(partition))
    }
}

/** Concurrent JDBC implementation of [PartitionsCreator]. */
class JdbcConcurrentPartitionsCreator<
    A : JdbcSharedState,
    S : JdbcStreamState<A>,
    P : JdbcPartition<S>,
>(
    partition: P,
    partitionFactory: JdbcPartitionFactory<A, S, P>,
) : JdbcPartitionsCreator<A, S, P>(partition, partitionFactory) {
    private val log = KotlinLogging.logger {}

    override suspend fun run(): List<PartitionReader> {
        // Ensure that the cursor upper bound is known, if required.
        if (partition is JdbcCursorPartition<*>) {
            ensureCursorUpperBound()
            if (
                streamState.cursorUpperBound == null || streamState.cursorUpperBound?.isNull == true
            ) {
                log.info { "Maximum cursor column value query found that the table was empty." }
                return listOf(CheckpointOnlyPartitionReader())
            }
        }
        // Handle edge case where the table can't be sampled.
        if (!sharedState.withSampling) {
            log.warn {
                "Table cannot be read by concurrent partition readers because it cannot be sampled."
            }
            // TODO: adaptive fetchSize computation?
            return listOf(JdbcNonResumablePartitionReader(partition))
        }
        // Sample the table for partition split boundaries and for record byte sizes.
        val sample: Sample<Pair<OpaqueStateValue?, Long>> = collectSample { record: ObjectNode ->
            val boundary: OpaqueStateValue? =
                (partition as? JdbcSplittablePartition<*>)?.incompleteState(record)
            val rowByteSize: Long = sharedState.rowByteSizeEstimator().apply(record)
            boundary to rowByteSize
        }
        if (sample.kind == Sample.Kind.EMPTY) {
            log.info { "Sampling query found that the table was empty." }
            return listOf(CheckpointOnlyPartitionReader())
        }
        val rowByteSizeSample: Sample<Long> = sample.map { (_, rowByteSize: Long) -> rowByteSize }
        streamState.fetchSize = sharedState.jdbcFetchSizeEstimator().apply(rowByteSizeSample)
        val expectedTableByteSize: Long = rowByteSizeSample.sampledValues.sum() * sample.valueWeight
        log.info { "Table memory size estimated at ${expectedTableByteSize shr 20} MiB." }
        // Handle edge case where the table can't be split.
        if (partition !is JdbcSplittablePartition<*>) {
            log.warn {
                "Table cannot be read by concurrent partition readers because it cannot be split."
            }
            return listOf(JdbcNonResumablePartitionReader(partition))
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
        val splitBoundaries: List<OpaqueStateValue> =
            sample.sampledValues
                .filter { random.nextDouble() < secondarySamplingRate }
                .mapNotNull { (splitBoundary: OpaqueStateValue?, _) -> splitBoundary }
                .distinct()
        val partitions: List<JdbcPartition<*>> = partitionFactory.split(partition, splitBoundaries)
        log.info { "Table will be read by ${partitions.size} concurrent partition reader(s)." }
        return partitions.map { JdbcNonResumablePartitionReader(it) }
    }
}
