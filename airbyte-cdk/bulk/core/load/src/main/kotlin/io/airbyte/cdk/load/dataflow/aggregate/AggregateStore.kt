/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.aggregate

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.config.MemoryAndParallelismConfig
import io.airbyte.cdk.load.dataflow.state.PartitionHistogram
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.ConcurrentHashMap

typealias StoreKey = DestinationStream.Descriptor

class AggregateStore(
    private val aggFactory: AggregateFactory,
    memoryAndParallelismConfig: MemoryAndParallelismConfig,
) {
    private val log = KotlinLogging.logger {}

    private val maxConcurrentAggregates = memoryAndParallelismConfig.maxOpenAggregates
    private val stalenessDeadlinePerAggMs =
        memoryAndParallelismConfig.stalenessDeadlinePerAgg.inWholeMilliseconds
    private val maxRecordsPerAgg = memoryAndParallelismConfig.maxRecordsPerAgg
    private val maxEstBytesPerAgg = memoryAndParallelismConfig.maxEstBytesPerAgg

    private val aggregates = ConcurrentHashMap<StoreKey, AggregateEntry>()

    fun acceptFor(key: StoreKey, record: RecordDTO) {
        val (_, agg, counts, bytes, timeTrigger, countTrigger, bytesTrigger) = getOrCreate(key)

        agg.accept(record)
        counts.increment(record.partitionKey, 1)
        bytes.increment(record.partitionKey, record.sizeBytes)
        countTrigger.increment(1)
        bytesTrigger.increment(record.sizeBytes)
        timeTrigger.update(record.emittedAtMs)
    }

    fun removeNextComplete(timestampMs: Long): AggregateEntry? {
        for ((key, entry) in aggregates) {
            // remove complete
            if (entry.isComplete()) {
                log.info { "PUBLISH — Reason: Complete" }
                return remove(key)
            }
            if (entry.isStale(timestampMs)) {
                log.info { "PUBLISH — Reason: Stale" }
                return remove(key)
            }
        }
        // evict largest in case of concurrency
        if (aggregates.size > maxConcurrentAggregates) {
            log.info { "PUBLISH — Reason: Cardinality" }
            val largest = aggregates.entries.maxBy { it.value.estimatedBytesTrigger.watermark() }
            return remove(largest.key)
        }
        return null
    }

    fun getAll(): List<AggregateEntry> {
        return aggregates.values.toList()
    }

    @VisibleForTesting
    internal fun getOrCreate(key: StoreKey): AggregateEntry {
        val entry =
            aggregates.computeIfAbsent(key) {
                AggregateEntry(
                    key = key,
                    value = aggFactory.create(it),
                    partitionCountsHistogram = PartitionHistogram(),
                    partitionBytesHistogram = PartitionHistogram(),
                    stalenessTrigger = TimeTrigger(stalenessDeadlinePerAggMs),
                    recordCountTrigger = SizeTrigger(maxRecordsPerAgg),
                    estimatedBytesTrigger = SizeTrigger(maxEstBytesPerAgg),
                )
            }

        return entry
    }

    @VisibleForTesting
    internal fun remove(key: StoreKey): AggregateEntry {
        return aggregates.remove(key)!!
    }
}

data class AggregateEntry(
    val key: StoreKey,
    val value: Aggregate,
    val partitionCountsHistogram: PartitionHistogram,
    val partitionBytesHistogram: PartitionHistogram,
    val stalenessTrigger: TimeTrigger,
    val recordCountTrigger: SizeTrigger,
    val estimatedBytesTrigger: SizeTrigger,
) {
    fun isComplete(): Boolean {
        return recordCountTrigger.isComplete() || estimatedBytesTrigger.isComplete()
    }

    fun isStale(ts: Long): Boolean {
        return stalenessTrigger.isComplete(ts)
    }
}

/* For testing purposes so we can mock. */
class AggregateStoreFactory(
    private val aggFactory: AggregateFactory,
    private val memoryAndParallelismConfig: MemoryAndParallelismConfig,
) {
    fun make() = AggregateStore(aggFactory, memoryAndParallelismConfig)
}
