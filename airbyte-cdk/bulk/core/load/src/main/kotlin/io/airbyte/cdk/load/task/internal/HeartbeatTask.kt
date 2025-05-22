/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.config.PipelineInputEvent
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.task.OnEndOfSync
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import kotlinx.coroutines.channels.ClosedSendChannelException
import kotlinx.coroutines.delay

class HeartbeatTask(
    private val config: DestinationConfiguration,
    private val outputQueue: PartitionedQueue<PipelineInputEvent>,
    private val checkpointManager: CheckpointManager<*>,
) : Task {
    override val terminalCondition: TerminalCondition = OnEndOfSync

    override suspend fun execute() {
        while (true) {
            delay(config.heartbeatIntervalSeconds * 1000L)
            try {
                outputQueue.broadcast(PipelineHeartbeat())
                checkpointManager.flushReadyCheckpointMessages()
            } catch (e: ClosedSendChannelException) {
                // Do nothing. We don't care. Move on
            }
        }
    }
}
