/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.state.Histogram
import io.airbyte.cdk.load.dataflow.state.PartitionHistogram
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Singleton
class StreamStatsStore {
    private val log = KotlinLogging.logger {}

    private val readCounts = Histogram<DestinationStream.Descriptor>()

    private val aggregatedStats = ConcurrentHashMap<DestinationStream.Descriptor, PartitionStats>()

    // these don't need to be atomic
    private var aggregateStatsEnabled = true
    private var firstStateSeen = false

    // Disables per stream stats aggregation if we are in per-stream mode.
    // Detected on first state.
    fun configure(msg: CheckpointMessage) {
        if (firstStateSeen) return

        if (msg is StreamCheckpoint) {
            aggregateStatsEnabled = false
            // best-effort empty the stats cache
            aggregatedStats.clear()
        }

        firstStateSeen = true
    }

    fun incrementReadCount(s: DestinationStream.Descriptor) = readCounts.increment(s, 1)

    fun acceptStats(
        s: DestinationStream.Descriptor,
        flushed: PartitionHistogram,
        bytes: PartitionHistogram,
    ) {
        if (aggregateStatsEnabled) {
            aggregatedStats.merge(s, PartitionStats(flushed, bytes), PartitionStats::merge)
        }
    }

    @VisibleForTesting
    fun removeStats(s: DestinationStream.Descriptor, p: PartitionKey): EmissionStats? =
        aggregatedStats[s]?.let {
            EmissionStats(
                count = it.flushed.remove(p) ?: 0,
                bytes = it.bytes.remove(p) ?: 0,
            )
        }

    fun removeStats(s: DestinationStream.Descriptor, ps: List<PartitionKey>) =
        ps.fold(EmissionStats()) { acc, key -> removeStats(s, key)?.let { acc.merge(it) } ?: acc }
}

data class PartitionStats(
    // Counts of flushed messages by partition id
    val flushed: PartitionHistogram = PartitionHistogram(),
    // Counts of flushed bytes by partition id
    val bytes: PartitionHistogram = PartitionHistogram(),
) {
    fun merge(other: PartitionStats): PartitionStats =
        this.apply {
            flushed.merge(other.flushed)
            bytes.merge(other.bytes)
        }
}
