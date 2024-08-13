/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.OutputStream
import kotlin.random.Random

/** Utilities for [StreamPartitionsCreator] that don't rely directly on its input state. */
class StreamPartitionsCreatorUtils(
    val ctx: StreamReadContext,
    val parameters: StreamPartitionsCreator.Parameters,
) {
    fun split(
        input: StreamPartitionReader.Input,
        globalLowerBound: List<JsonNode>?,
        globalUpperBound: List<JsonNode>?,
    ): List<Pair<List<JsonNode>?, List<JsonNode>?>> {
        // Collect a sample from the unsplit partition of this table.
        // Each sampled row is mapped to the values of the order fields
        // and to the approximate byte size in memory of the row.
        val unsplitQuerySpec: SelectQuerySpec =
            input.querySpec(ctx.stream, isOrdered = true, limit = null)
        val checkpointColumns: List<Field> = (unsplitQuerySpec.orderBy as OrderBy).columns
        val rowByteSizeEstimator: (ObjectNode) -> Long = rowByteSizeEstimator()
        val sample: Sample<Pair<List<JsonNode>, Long>> by lazy {
            log.info { "Sampling stream '${ctx.stream.label}'" }
            collectSample(unsplitQuerySpec) { record: ObjectNode ->
                val checkpointValues: List<JsonNode> =
                    checkpointColumns.map { record[it.id] ?: Jsons.nullNode() }
                checkpointValues to rowByteSizeEstimator(record)
            }
        }
        // Ensure that the JDBC fetchSize parameter value for this table is set.
        // Compute it using the sample.
        if (ctx.transientFetchSize.get() == null) {
            val rowByteSizeSample: Sample<Long> =
                sample.map { (_, rowByteSize: Long) -> rowByteSize }
            val maxMemoryBytes: Long = Runtime.getRuntime().maxMemory()
            val fetchSizeEstimator =
                MemoryFetchSizeEstimator(maxMemoryBytes, ctx.configuration.maxConcurrency)
            ctx.transientFetchSize.update { fetchSizeEstimator.apply(rowByteSizeSample) }
        }
        // Compute partition split boundaries.
        // First, check if splitting can or should be done, and exit if that isn't the case.
        if (checkpointColumns.isEmpty() || !parameters.preferParallelized) {
            log.info {
                "not attempting to create more than one partition for '${ctx.stream.label}'"
            }
            return listOf(globalLowerBound to globalUpperBound)
        }
        // At this point, try to split the partition defined by
        // ]globalLowerBound, globalUpperBound]. Each of these splits should be processed within the
        // targeted amount of time defined in the configuration. This estimate is very imprecise:
        // the sampling is almost certainly going to be biased, the throughput is wildly dependent
        // on many uncontrollable factors, etc.
        val splitBoundaries: List<List<JsonNode>> = computeSplitBoundaries(sample)
        if (splitBoundaries.isEmpty()) {
            log.info { "creating one partition for remaining data in '${ctx.stream.label}" }
        } else {
            log.info {
                "split remaining data in '${ctx.stream.label} " +
                    "into ${splitBoundaries.size + 1} partitions"
            }
        }
        val lbs: List<List<JsonNode>?> = listOf(globalLowerBound) + splitBoundaries
        val ubs: List<List<JsonNode>?> = splitBoundaries + listOf(globalUpperBound)
        return lbs.zip(ubs)
    }

    fun rowByteSizeEstimator(): (ObjectNode) -> Long {
        val countingOutputStream =
            object : OutputStream() {
                var counter: Long = 0L

                override fun write(b: Int) {
                    counter++
                }
            }
        val jsonGenerator: JsonGenerator = Jsons.createGenerator(countingOutputStream)
        val fieldOverheadEstimate = 16L
        return { record: ObjectNode ->
            countingOutputStream.counter = 0L
            Jsons.writeValue(jsonGenerator, record)
            val rowOverheadBytes: Long =
                fieldOverheadEstimate * record.fields().asSequence().count()
            countingOutputStream.counter + rowOverheadBytes
        }
    }

    /** Computes the max value for the cursor column, used as an upper bound during this sync. */
    fun computeCursorUpperBound(cursor: Field): JsonNode? {
        val querySpec =
            SelectQuerySpec(
                SelectColumnMaxValue(cursor),
                From(ctx.stream.name, ctx.stream.namespace),
            )
        val q: SelectQuery = ctx.selectQueryGenerator.generate(querySpec.optimize())
        val record: ObjectNode =
            ctx.selectQuerier.executeQuery(q).use { if (it.hasNext()) it.next() else return null }
        val value: JsonNode = record[cursor.id] ?: Jsons.nullNode()
        if (value.isNull) {
            throw IllegalStateException("NULL value found for cursor ${cursor.id}")
        }
        return ctx.transientCursorUpperBoundState.update { value }
    }

    /** Computes the partition split boundaries from the given sample. */
    private fun computeSplitBoundaries(
        sample: Sample<Pair<List<JsonNode>, Long>>,
    ): List<List<JsonNode>> {
        val expectedTableByteSize: Long =
            sample.sampledValues.sumOf { (_, rowByteSize: Long) ->
                rowByteSize * sample.valueWeight
            }
        log.info {
            "remaining data in '${ctx.stream.label}' " +
                "is estimated at ${expectedTableByteSize shr 20} MiB"
        }
        val streamThroughputBytesPerSecond: Long =
            parameters.throughputBytesPerSecond / ctx.configuration.maxConcurrency
        val targetCheckpointByteSize: Long =
            streamThroughputBytesPerSecond * ctx.configuration.checkpointTargetInterval.seconds
        log.info {
            "target partition size for '${ctx.stream.label}' " +
                "is ${targetCheckpointByteSize shr 20} MiB"
        }
        val secondarySamplingRate: Double =
            if (expectedTableByteSize <= targetCheckpointByteSize) {
                0.0
            } else {
                val expectedPartitionByteSize: Long =
                    expectedTableByteSize / parameters.tableSampleSize
                if (expectedPartitionByteSize < targetCheckpointByteSize) {
                    expectedPartitionByteSize.toDouble() / targetCheckpointByteSize
                } else {
                    1.0
                }
            }
        val random = Random(expectedTableByteSize) // RNG output is repeatable.
        return sample.sampledValues
            .filter { random.nextDouble() < secondarySamplingRate }
            .map { (splitBoundary: List<JsonNode>, _) -> splitBoundary }
    }

    /** Collects a sample of rows in the unsplit partition. */
    fun <T> collectSample(
        querySpec: SelectQuerySpec,
        rowFn: (ObjectNode) -> T,
    ): Sample<T> {
        val values = mutableListOf<T>()
        var previousWeight = 0L
        for (sampleRateInvPow2 in listOf(16, 8, 0)) {
            // First, try sampling the table at a rate of one every 2^16 = 65_536 rows.
            // If that's not enough to produce the desired number of sampled rows (1024 by default)
            // then try sampling at a higher rate of one every 2^8 = 256 rows.
            // If that's still not enough, don't sample at all.
            values.clear()
            val fromSample =
                FromSample(
                    ctx.stream.name,
                    ctx.stream.namespace,
                    sampleRateInvPow2,
                    parameters.tableSampleSize,
                )
            val sampledQuerySpec: SelectQuerySpec = querySpec.copy(from = fromSample)
            val q: SelectQuery = ctx.selectQueryGenerator.generate(sampledQuerySpec.optimize())
            ctx.selectQuerier.executeQuery(q).use { for (record in it) values.add(rowFn(record)) }
            if (values.size < parameters.tableSampleSize) {
                previousWeight = (fromSample.sampleRateInv * values.size) / fromSample.sampleSize
                continue
            }
            val kind: Sample.Kind =
                when (sampleRateInvPow2) {
                    16 -> Sample.Kind.LARGE
                    8 -> Sample.Kind.MEDIUM
                    else -> Sample.Kind.SMALL
                }
            log.info { "sampled ${values.size} rows in ${kind.name} stream ${ctx.stream.label}." }
            return Sample(values, kind, previousWeight.coerceAtLeast(fromSample.sampleRateInv))
        }
        val kind: Sample.Kind = if (values.isEmpty()) Sample.Kind.EMPTY else Sample.Kind.TINY
        log.info { "sampled ${values.size} rows in ${kind.name} stream ${ctx.stream.label}." }
        return Sample(values, kind, if (values.isEmpty()) 0L else 1L)
    }

    private val log = KotlinLogging.logger {}
}
