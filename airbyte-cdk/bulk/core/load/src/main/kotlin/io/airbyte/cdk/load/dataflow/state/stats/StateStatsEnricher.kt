/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.dataflow.state.PartitionKey
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
) {
    fun enrich(msg: CheckpointMessage, ps: List<PartitionKey>): CheckpointMessage {
        return when (msg) {
            is StreamCheckpoint -> enrichStreamState(msg, ps)
            is GlobalSnapshotCheckpoint -> enrichGlobalState(msg, msg.checkpoints, ps)
            is GlobalCheckpoint -> enrichGlobalState(msg, msg.checkpoints, ps)
        }
    }

    @VisibleForTesting
    fun enrichTopLevelDestinationStats(msg: CheckpointMessage, count: Long): CheckpointMessage {
        msg.updateStats(
            destinationStats = CheckpointMessage.Stats(count),
        )

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
        ps: List<PartitionKey>,
    ): CheckpointMessage {
        val desc =
            namespaceMapper.map(
                namespace = msg.checkpoint.unmappedNamespace,
                name = msg.checkpoint.unmappedName,
            )
        val (committed, cumulative) = statsStore.commitStats(desc, ps)

        enrichTopLevelDestinationStats(msg, committed.count)
        enrichTopLevelStats(msg, cumulative)

        return msg
    }

    @VisibleForTesting
    fun enrichGlobalState(
        msg: CheckpointMessage,
        checkpoints: List<CheckpointMessage.Checkpoint>,
        ps: List<PartitionKey>,
    ): CheckpointMessage {
        val (committed, cumulative) =
            checkpoints
                .map {
                    val desc =
                        namespaceMapper.map(
                            namespace = it.unmappedNamespace,
                            name = it.unmappedName,
                        )
                    val result = statsStore.commitStats(desc, ps)
                    // Side effect: We update the checkpoints in place before summing
                    it.updateStats(result.cumulativeStats.count, result.cumulativeStats.bytes)
                    result
                }
                .fold(CommitStatsResult()) { acc, c -> acc.merge(c) }

        enrichTopLevelDestinationStats(msg, committed.count)
        enrichTopLevelStats(msg, cumulative)

        return msg
    }
}
