/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.message.Batch
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.state.StreamManager
import io.airbyte.cdk.state.StreamsManager
import io.airbyte.cdk.write.StreamLoader
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

/**
 * Wraps @[StreamLoader.processBatch] and handles the resulting batch, possibly calling back into
 * the task or initiating close stream if processing is complete.
 *
 * TODO: Move handling batch results into the task launcher.
 */
class ProcessBatchTask(
    private val batchEnvelope: BatchEnvelope<*>,
    private val streamLoader: StreamLoader,
    private val streamManager: StreamManager,
    private val taskLauncher: DestinationTaskLauncher
) : Task {
    override suspend fun execute() {
        val nextBatch = streamLoader.processBatch(batchEnvelope.batch)
        val nextWrapped = batchEnvelope.withBatch(nextBatch)
        streamManager.updateBatchState(nextWrapped)

        if (nextBatch.state != Batch.State.COMPLETE) {
            taskLauncher.startProcessBatchTask(streamLoader, nextWrapped)
        } else if (streamManager.isBatchProcessingComplete()) {
            taskLauncher.startCloseStreamTasks(streamLoader)
        }
    }
}

@Singleton
@Secondary
class ProcessBatchTaskFactory(
    private val streamsManager: StreamsManager,
) {
    fun make(
        taskLauncher: DestinationTaskLauncher,
        streamLoader: StreamLoader,
        batchEnvelope: BatchEnvelope<*>
    ): ProcessBatchTask {
        return ProcessBatchTask(
            batchEnvelope,
            streamLoader,
            streamsManager.getManager(streamLoader.stream),
            taskLauncher
        )
    }
}
