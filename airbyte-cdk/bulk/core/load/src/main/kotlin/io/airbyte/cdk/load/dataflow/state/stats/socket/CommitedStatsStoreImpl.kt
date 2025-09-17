/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats.socket

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.state.PartitionHistogram
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.state.stats.CommittedStatsStore
import io.airbyte.cdk.load.dataflow.state.stats.EmissionStats
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

/** Stores stat histograms per stream. For hydrating state messages with stats. */
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "SOCKET")
@Singleton
class CommittedStatsStoreImpl : CommittedStatsStore {
    private val aggregatedStats = ConcurrentHashMap<DestinationStream.Descriptor, PartitionStats>()

    override fun acceptStats(
        s: DestinationStream.Descriptor,
        flushed: PartitionHistogram,
        bytes: PartitionHistogram,
    ) {
        aggregatedStats.merge(s, PartitionStats(flushed, bytes), PartitionStats::merge)
    }

    fun removeStats(s: DestinationStream.Descriptor, ps: List<PartitionKey>) =
        ps.fold(EmissionStats()) { acc, key -> removeStats(s, key)?.let { acc.merge(it) } ?: acc }

    @VisibleForTesting
    fun removeStats(s: DestinationStream.Descriptor, p: PartitionKey): EmissionStats? =
        aggregatedStats[s]?.let {
            EmissionStats(
                count = it.flushed.remove(p) ?: 0,
                bytes = it.bytes.remove(p) ?: 0,
            )
        }
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
