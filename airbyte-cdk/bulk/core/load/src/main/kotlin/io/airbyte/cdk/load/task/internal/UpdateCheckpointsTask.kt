/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.GlobalCheckpointWrapped
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.StreamCheckpointWrapped
import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

@Singleton
@Secondary
class UpdateCheckpointsTask(
    private val syncManager: SyncManager,
    private val checkpointManager: CheckpointManager<Reserved<CheckpointMessage>>,
    private val checkpointMessageQueue: MessageQueue<Reserved<CheckpointMessageWrapped>>
) : Task {
    val log = KotlinLogging.logger {}

    override val terminalCondition: TerminalCondition = SelfTerminating

    override suspend fun execute() {
        log.info { "Starting to consume checkpoint messages (state) for updating" }
        checkpointMessageQueue.consume().collect {
            when (it.value) {
                is StreamCheckpointWrapped -> {
                    val (stream, checkpointKey, message) = it.value
                    log.info {
                        "Updating stream checkpoint $stream:$checkpointKey:${it.value.checkpoint.sourceStats}"
                    }
                    checkpointManager.addStreamCheckpoint(
                        stream,
                        checkpointKey,
                        it.replace(message)
                    )
                }
                is GlobalCheckpointWrapped -> {
                    val (checkpointKey, message) = it.value
                    log.info {
                        "Updating global checkpoint with $checkpointKey:${it.value.checkpoint.sourceStats}"
                    }
                    checkpointManager.addGlobalCheckpoint(checkpointKey, it.replace(message))
                }
            }
            // If its corresponding data was processed before this checkpoint was added,
            // then it's possible it's already data-sufficient.
            checkpointManager.flushReadyCheckpointMessages()
        }
        syncManager.markCheckpointsProcessed()
        log.info { "All checkpoints (state) updated" }
    }
}
