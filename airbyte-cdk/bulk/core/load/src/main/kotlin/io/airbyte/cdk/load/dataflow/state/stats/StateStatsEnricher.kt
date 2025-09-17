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
    private val statsStore: StreamStatsStore,
    private val namespaceMapper: NamespaceMapper,
) {
    fun enrich(msg: CheckpointMessage, stats: EmissionStats, ps: List<PartitionKey>) =
        enrichStreamStats(enrichTopLevelStats(msg, stats), ps)

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
    fun enrichStreamStats(msg: CheckpointMessage, ps: List<PartitionKey>): CheckpointMessage {
        val checkpoints =
            when (msg) {
                // streams checkpoints don't have sub stream states to enrich
                is StreamCheckpoint -> return msg
                is GlobalSnapshotCheckpoint -> msg.checkpoints
                is GlobalCheckpoint -> msg.checkpoints
            }

        checkpoints.forEach {
            val desc =
                namespaceMapper.map(
                    namespace = it.unmappedNamespace,
                    name = it.unmappedName,
                )
            val stats = statsStore.removeStats(desc, ps)
            it.updateStats(stats.count, stats.bytes)
        }

        return msg
    }
}
