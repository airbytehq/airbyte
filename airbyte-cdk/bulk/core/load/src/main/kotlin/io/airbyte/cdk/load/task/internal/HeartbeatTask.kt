/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.task.OnEndOfSync
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.channels.ClosedSendChannelException
import kotlinx.coroutines.delay

@Singleton
class HeartbeatTask<K : WithStream, V>(
    private val config: DestinationConfiguration,
    @Named("recordQueue") private val recordQueue: PartitionedQueue<PipelineEvent<K, V>>
) : Task {
    override val terminalCondition: TerminalCondition = OnEndOfSync

    override suspend fun execute() {
        while (true) {
            delay(config.heartbeatIntervalSeconds * 1000L)
            try {
                recordQueue.broadcast(PipelineHeartbeat())
            } catch (e: ClosedSendChannelException) {
                // Do nothing. We don't care. Move on
            }
        }
    }
}
