/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.aggregate

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig
import io.airbyte.cdk.load.dataflow.state.PartitionHistogram
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.ConcurrentHashMap

typealias StoreKey = DestinationStream.Descriptor

class AggregateStore(
    private val aggFactory: AggregateFactory,
    private val config: AggregatePublishingConfig,
) {
    private val log = KotlinLogging.logger {}

    private val aggregates = ConcurrentHashMap<StoreKey, AggregateEntry>()

    private val stalenessDeadlinePerAggMs = config.stalenessDeadlinePerAgg.inWholeMilliseconds
    private val maxOpenAggregatesSoft = config.maxEstBytesAllAggregates / config.maxEstBytesPerAgg

    fun acceptFor(key: StoreKey, record: RecordDTO) {
        val (_, agg, counts, bytes, timeTrigger, countTrigger, bytesTrigger) = getOrCreate(key)

        agg.accept(record)
        counts.increment(record.partitionKey, 1.0)
        bytes.increment(record.partitionKey, record.sizeBytes.toDouble())
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
        // only sum bytes if we have a high cardinality of active aggregates (in practice this is
        // the number of interleaved streams)
        if (aggregates.size > maxOpenAggregatesSoft) {
            val activeBytes = aggregates.map { it.value.estimatedBytesTrigger.watermark() }.sum()

            if (activeBytes > config.maxEstBytesAllAggregates) {
                // evict largest in case of heavy cardinality
                log.info { "PUBLISH — Reason: Cardinality" }
                val largest =
                    aggregates.entries.maxBy { it.value.estimatedBytesTrigger.watermark() }
                return remove(largest.key)
            }
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
                    recordCountTrigger = SizeTrigger(config.maxRecordsPerAgg),
                    estimatedBytesTrigger = SizeTrigger(config.maxEstBytesPerAgg),
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
    private val aggregatePublishingConfig: AggregatePublishingConfig,
) {
    fun make() = AggregateStore(aggFactory, aggregatePublishingConfig)
}
