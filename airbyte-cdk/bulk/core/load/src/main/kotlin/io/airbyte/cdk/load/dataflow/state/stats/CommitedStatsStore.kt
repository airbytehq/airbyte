/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.state.PartitionHistogram
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.state.StateKey
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

/** Stores stat histograms per stream. For hydrating state messages with stats. */
@Singleton
class CommittedStatsStore {
    // stats for live (non-committed) partitions by stream x partition
    private val liveStats = ConcurrentHashMap<DestinationStream.Descriptor, PartitionStats>()
    // summed stats for committed partitions by stream
    private val cumulativeStats = ConcurrentHashMap<DestinationStream.Descriptor, EmissionStats>()

    fun acceptStats(
        s: DestinationStream.Descriptor,
        counts: PartitionHistogram,
        bytes: PartitionHistogram,
    ) {
        liveStats.merge(s, PartitionStats(counts, bytes), PartitionStats::merge)
    }

    fun commitStats(s: DestinationStream.Descriptor, key: StateKey): CommitStatsResult {
        val toCommit = removeLiveStats(s, key)
        val cumulativeStats = commitStats(s, toCommit)
        return CommitStatsResult(toCommit, cumulativeStats)
    }

    // accumulates stats into the cumulative counts
    @VisibleForTesting
    internal fun commitStats(s: DestinationStream.Descriptor, stats: EmissionStats): EmissionStats =
        cumulativeStats.merge(s, stats, EmissionStats::merge) ?: EmissionStats()

    // removes and gets the summed stats for a stream given a list of partitions
    @VisibleForTesting
    internal fun removeLiveStats(s: DestinationStream.Descriptor, key: StateKey) =
        key.partitionKeys.fold(EmissionStats()) { acc, p ->
            removeLiveStats(s, p)?.let { acc.merge(it) } ?: acc
        }

    // removes and gets the summed stats for a stream given a single partition
    @VisibleForTesting
    internal fun removeLiveStats(s: DestinationStream.Descriptor, p: PartitionKey): EmissionStats? =
        liveStats[s]?.let {
            EmissionStats(
                count = it.counts.remove(p)?.toLong() ?: 0,
                bytes = it.bytes.remove(p)?.toLong() ?: 0,
            )
        }
}

data class CommitStatsResult(
    val committedStats: EmissionStats = EmissionStats(),
    val cumulativeStats: EmissionStats = EmissionStats(),
) {
    fun merge(other: CommitStatsResult): CommitStatsResult =
        this.apply {
            committedStats.merge(other.committedStats)
            cumulativeStats.merge(other.cumulativeStats)
        }
}

data class PartitionStats(
    // Counts of committed messages by partition id
    val counts: PartitionHistogram = PartitionHistogram(),
    // Counts of committed bytes by partition id
    val bytes: PartitionHistogram = PartitionHistogram(),
) {
    fun merge(other: PartitionStats): PartitionStats =
        this.apply {
            counts.merge(other.counts)
            bytes.merge(other.bytes)
        }
}
