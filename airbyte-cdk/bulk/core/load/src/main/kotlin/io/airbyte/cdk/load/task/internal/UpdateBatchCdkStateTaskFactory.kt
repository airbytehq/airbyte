/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.message.BatchCdkState
import io.airbyte.cdk.load.message.QueueReader
import io.airbyte.cdk.load.pipeline.BatchCdkStateUpdate
import io.airbyte.cdk.load.pipeline.BatchEndOfStream
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.OnEndOfSync
import io.airbyte.cdk.load.task.Task
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton

/** A long-running task that updates the state of record batches after they are processed. */
class UpdateBatchCdkStateTask(
    private val inputQueue: QueueReader<BatchUpdate>,
    private val syncManager: SyncManager,
    private val checkpointManager: CheckpointManager,
    private val launcher: DestinationTaskLauncher
) : Task {
    private val log = KotlinLogging.logger {}

    override val terminalCondition = OnEndOfSync

    override suspend fun execute() {
        inputQueue.consume().collect { message ->
            val manager = syncManager.getStreamManager(message.stream)
            val cdkState =
                when (message) {
                    is BatchCdkStateUpdate -> {
                        log.debug {
                            "Batch update for ${message.stream}: ${message.taskName}[${message.part}](${message.cdkState}) += ${message.checkpointCounts} (inputs += ${message.inputCount})"
                        }
                        manager.incrementCheckpointCounts(
                            message.cdkState,
                            message.checkpointCounts,
                        )
                        message.cdkState
                    }
                    is BatchEndOfStream -> {
                        log.info {
                            "End-of-stream checks for ${message.stream}: ${message.taskName}[${message.part}]"
                        }
                        BatchCdkState.COMPLETE
                    }
                }
            if (cdkState.isPersisted()) {
                checkpointManager.flushReadyCheckpointMessages()
            }
            if (manager.isBatchProcessingCompleteForCheckpoints()) {
                log.debug { "Batch processing complete for ${message.stream}" }
                launcher.handleStreamComplete(message.stream)
            } else {
                log.debug { "Batch processing still incomplete for ${message.stream}" }
            }
        }
    }
}

@Singleton
class UpdateBatchCdkStateTaskFactory(
    @Named("batchStateUpdateQueue") private val inputQueue: QueueReader<BatchUpdate>,
    private val syncManager: SyncManager,
    private val checkpointManager: CheckpointManager,
) {
    fun make(taskLauncher: DestinationTaskLauncher): UpdateBatchCdkStateTask {
        return UpdateBatchCdkStateTask(inputQueue, syncManager, checkpointManager, taskLauncher)
    }
}
