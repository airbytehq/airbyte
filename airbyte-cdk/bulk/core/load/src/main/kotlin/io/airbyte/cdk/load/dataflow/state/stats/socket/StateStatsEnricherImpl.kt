/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats.socket

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.state.stats.EmissionStats
import io.airbyte.cdk.load.dataflow.state.stats.StateStatsEnricher
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.GlobalSnapshotCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/** Decorates states with destination stats — both top level and per stream. */
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "SOCKET")
@Singleton
class StateStatsEnricherImpl(
    private val statsStore: CommittedStatsStoreImpl,
    private val namespaceMapper: NamespaceMapper,
) : StateStatsEnricher {
    override fun enrich(msg: CheckpointMessage, ps: List<PartitionKey>): CheckpointMessage {
        return when (msg) {
            is StreamCheckpoint -> enrichStreamState(msg, ps)
            is GlobalSnapshotCheckpoint -> enrichGlobalState(msg, msg.checkpoints, ps)
            is GlobalCheckpoint -> enrichGlobalState(msg, msg.checkpoints, ps)
        }
    }

    @VisibleForTesting
    fun enrichTopLevelStats(msg: CheckpointMessage, stats: EmissionStats): CheckpointMessage {
        msg.updateStats(
            destinationStats = CheckpointMessage.Stats(stats.count),
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
        val stats = statsStore.removeStats(desc, ps)

        enrichTopLevelStats(msg, stats)

        return msg
    }

    @VisibleForTesting
    fun enrichGlobalState(
        msg: CheckpointMessage,
        checkpoints: List<CheckpointMessage.Checkpoint>,
        ps: List<PartitionKey>,
    ): CheckpointMessage {
        val stats =
            checkpoints
                .map {
                    val desc =
                        namespaceMapper.map(
                            namespace = it.unmappedNamespace,
                            name = it.unmappedName,
                        )
                    val stats = statsStore.removeStats(desc, ps)
                    // Side effect: We update the checkpoints in place before summing
                    it.updateStats(stats.count, stats.bytes)
                    stats
                }
                .fold(EmissionStats()) { acc, stats -> acc.merge(stats) }

        enrichTopLevelStats(msg, stats)

        return msg
    }
}
