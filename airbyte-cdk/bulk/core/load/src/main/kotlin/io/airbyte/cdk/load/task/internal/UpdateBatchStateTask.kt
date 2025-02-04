/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import com.google.common.collect.Range
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.QueueReader
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.pipeline.BatchEndOfStream
import io.airbyte.cdk.load.pipeline.BatchStateUpdate
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
            // For now just rewrap the message to shim into the current interface
            val envelope =
                when (message) {
                    is BatchStateUpdate ->
                        BatchEnvelope(
                            SimpleBatch(message.state),
                            message.indexRange,
                            message.stream
                        )
                    is BatchEndOfStream ->
                        BatchEnvelope(
                            SimpleBatch(Batch.State.COMPLETE),
                            Range.singleton(0),
                            message.stream
                        )
                }
            manager.updateBatchState(envelope)
            if (envelope.batch.isPersisted()) {
                checkpointManager.flushReadyCheckpointMessages()
            }
            if (manager.isBatchProcessingComplete()) {
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
