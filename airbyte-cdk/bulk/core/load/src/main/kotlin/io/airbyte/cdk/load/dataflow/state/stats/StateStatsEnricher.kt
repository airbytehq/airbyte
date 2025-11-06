/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.dataflow.state.StateKey
import io.airbyte.cdk.load.dataflow.stats.MetricTracker
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.GlobalSnapshotCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpoint
import jakarta.inject.Singleton

/** Decorates states with destination stats — both top level and per stream. */
@Singleton
class StateStatsEnricher(
    private val statsStore: CommittedStatsStore,
    private val namespaceMapper: NamespaceMapper,
    private val metricTracker: MetricTracker,
    private val metricStats: MetricStatsStore,
) {
    // Enriches provided state message with stats associated with the given state key.
    fun enrich(msg: CheckpointMessage, key: StateKey): CheckpointMessage {
        return when (msg) {
            is StreamCheckpoint -> enrichStreamState(msg, key)
            is GlobalSnapshotCheckpoint,
            is GlobalCheckpoint -> enrichGlobalState(msg, key)
        }
    }

    @VisibleForTesting
    @Suppress("UNUSED_PARAMETER")
    fun enrichTopLevelDestinationStats(
        msg: CheckpointMessage,
        desc: DestinationStream.Descriptor,
        count: Long
    ): CheckpointMessage {
        // TODO: set this using the count above once we get to total rejected
        // records.
        msg.updateStats(
            destinationStats = msg.sourceStats,
            additionalStats = metricTracker.drain(desc)
        )

        return msg
    }

    @VisibleForTesting
    @Suppress("UNUSED_PARAMETER")
    fun enrichTopLevelDestinationStatsGlobalState(
        msg: CheckpointMessage,
        count: Long
    ): CheckpointMessage {
        // TODO: set this using the count above once we get to total rejected
        // records.
        msg.updateStats(destinationStats = msg.sourceStats)

        return msg
    }

    @VisibleForTesting
    fun enrichTopLevelStats(msg: CheckpointMessage, stats: EmissionStats): CheckpointMessage {
        msg.updateStats(
            totalRecords = stats.count,
            totalBytes = stats.bytes,
        )

        return msg
    }

    @VisibleForTesting
    fun enrichStreamState(
        msg: StreamCheckpoint,
        key: StateKey,
    ): CheckpointMessage {
        val desc =
            namespaceMapper.map(
                namespace = msg.checkpoint.unmappedNamespace,
                name = msg.checkpoint.unmappedName,
            )
        val (committed, cumulative) = statsStore.commitStats(desc, key)

        val additionalStats = metricStats.drainStats(key.partitionKeys)[desc]

        enrichTopLevelDestinationStats(msg, committed.count, additionalStats)
        enrichTopLevelStats(msg, cumulative)

        return msg
    }

    @VisibleForTesting
    fun enrichGlobalState(
        msg: CheckpointMessage,
        key: StateKey,
    ): CheckpointMessage {
        val additionalStatsByStream = metricStats.drainStats(key.partitionKeys)

        val (committed, cumulative) =
            msg.checkpoints
                .map {
                    val desc =
                        namespaceMapper.map(
                            namespace = it.unmappedNamespace,
                            name = it.unmappedName,
                        )
                    val result = statsStore.commitStats(desc, key)
                    val additionalStats = additionalStatsByStream[desc]
                    // Side effect: We update the checkpoints in place before summing
                    it.updateStats(
                        result.cumulativeStats.count,
                        result.cumulativeStats.bytes,
                        additionalStats,
                    )
                    result
                }
                .fold(CommitStatsResult()) { acc, c -> acc.merge(c) }

        enrichTopLevelDestinationStatsGlobalState(msg, committed.count)
        enrichTopLevelStats(msg, cumulative)

        return msg
    }
}
