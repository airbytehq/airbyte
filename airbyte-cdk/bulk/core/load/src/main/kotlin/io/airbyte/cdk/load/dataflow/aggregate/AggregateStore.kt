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
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

typealias StoreKey = DestinationStream.Descriptor

@Singleton
class AggregateStore(
    private val aggFactory: AggregateFactory,
    private val memoryAndParallelismConfig: MemoryAndParallelismConfig,
) {
    private val log = KotlinLogging.logger {}

    private val maxConcurrentAggregates = memoryAndParallelismConfig.maxOpenAggregates
    private val stalenessDeadlinePerAggMs =
        memoryAndParallelismConfig.stalenessDeadlinePerAgg.inWholeMilliseconds
    private val maxRecordsPerAgg = memoryAndParallelismConfig.maxRecordsPerAgg
    private val maxEstBytesPerAgg = memoryAndParallelismConfig.maxEstBytesPerAgg

    private val aggregates = ConcurrentHashMap<StoreKey, AggregateEntry>()

    fun acceptFor(key: StoreKey, record: RecordDTO) {
        val (agg, histogram, timeTrigger, countTrigger, bytesTrigger) = getOrCreate(key)

        agg.accept(record)
        histogram.increment(record.partitionKey)
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
                    value = aggFactory.create(it),
                    partitionHistogram = PartitionHistogram(),
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
    val value: Aggregate,
    val partitionHistogram: PartitionHistogram,
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
