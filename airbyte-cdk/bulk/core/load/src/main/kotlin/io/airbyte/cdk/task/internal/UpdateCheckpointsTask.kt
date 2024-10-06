/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task.internal

import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.message.CheckpointMessage
import io.airbyte.cdk.message.CheckpointMessageWrapped
import io.airbyte.cdk.message.GlobalCheckpointWrapped
import io.airbyte.cdk.message.MessageQueue
import io.airbyte.cdk.message.StreamCheckpointWrapped
import io.airbyte.cdk.state.CheckpointManager
import io.airbyte.cdk.state.Reserved
import io.airbyte.cdk.task.SyncTask
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface UpdateCheckpointsTask : SyncTask

@Singleton
@Secondary
class DefaultUpdateCheckpointsTask(
    private val checkpointManager:
        CheckpointManager<DestinationStream.Descriptor, Reserved<CheckpointMessage>>,
    private val checkpointMessageQueue: MessageQueue<Reserved<CheckpointMessageWrapped>>
) : UpdateCheckpointsTask {
    val log = KotlinLogging.logger {}
    override suspend fun execute() {
        log.info { "Starting to consume checkpoint messages (state) for updating" }
        checkpointMessageQueue.consume().collect {
            when (it.value) {
                is StreamCheckpointWrapped -> {
                    val (_, stream, index, message) = it.value
                    checkpointManager.addStreamCheckpoint(stream, index, it.replace(message))
                }
                is GlobalCheckpointWrapped -> {
                    val (_, streamIndexes, message) = it.value
                    checkpointManager.addGlobalCheckpoint(streamIndexes, it.replace(message))
                }
            }
        }
        log.info { "All checkpoints (state) updated" }
    }
}
