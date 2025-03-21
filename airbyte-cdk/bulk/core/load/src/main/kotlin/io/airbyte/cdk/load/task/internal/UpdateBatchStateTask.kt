/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.QueueReader
import io.airbyte.cdk.load.pipeline.BatchEndOfStream
import io.airbyte.cdk.load.pipeline.BatchStateUpdate
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.state.CheckpointValue
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.OnEndOfSync
import io.airbyte.cdk.load.task.Task
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton

/** A long-running task that updates the state of record batches after they are processed. */
class UpdateBatchStateTask(
    private val inputQueue: QueueReader<BatchUpdate>,
    private val syncManager: SyncManager,
    private val checkpointManager: CheckpointManager<DestinationStream.Descriptor, *>,
    private val launcher: DestinationTaskLauncher
) : Task {
    private val log = KotlinLogging.logger {}

    override val terminalCondition = OnEndOfSync

    override suspend fun execute() {
        inputQueue.consume().collect { message ->
            val manager = syncManager.getStreamManager(message.stream)
            when (message) {
                is BatchStateUpdate -> {
                    log.info {
                        "Batch update for ${message.stream}: ${message.taskName}[${message.part}](${message.state}) += ${message.checkpointCounts}"
                    }
                    manager.incrementCheckpointCounts(
                        message.taskName,
                        message.part,
                        message.state,
                        message.checkpointCounts,
                        message.inputCount
                    )
                }
                is BatchEndOfStream -> {
                    log.info {
                        "End-of-stream checks for ${message.stream}: ${message.taskName}[${message.part}]"
                    }
                    manager.markTaskEndOfStream(message.taskName, message.part,  message.totalInputCount)
                }
            }
            checkpointManager.flushReadyCheckpointMessages()
            if (manager.isBatchProcessingCompleteForCheckpoints()) {
                log.info { "Batch processing complete for ${message.stream}" }
                launcher.handleStreamComplete(message.stream)
            } else {
                log.info { "Batch processing still incomplete for ${message.stream}" }
            }
        }
    }
}

@Singleton
class UpdateBatchStateTaskFactory(
    @Named("batchStateUpdateQueue") val inputQueue: QueueReader<BatchUpdate>,
    private val syncManager: SyncManager,
    private val checkpointManager: CheckpointManager<DestinationStream.Descriptor, *>
) {
    fun make(launcher: DestinationTaskLauncher): Task {
        return UpdateBatchStateTask(inputQueue, syncManager, checkpointManager, launcher)
    }
}
