/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.state.StreamsManager
import io.airbyte.cdk.write.StreamLoader
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface ProcessBatchTask : Task

/** Wraps @[StreamLoader.processBatch] and handles the resulting batch. */
class DefaultProcessBatchTask(
    private val batchEnvelope: BatchEnvelope<*>,
    private val streamLoader: StreamLoader,
    private val taskLauncher: DestinationTaskLauncher
) : ProcessBatchTask {
    override suspend fun execute() {
        val nextBatch = streamLoader.processBatch(batchEnvelope.batch)
        val nextWrapped = batchEnvelope.withBatch(nextBatch)
        taskLauncher.handleNewBatch(streamLoader, nextWrapped)
    }
}

interface ProcessBatchTaskFactory {
    fun make(
        taskLauncher: DestinationTaskLauncher,
        streamLoader: StreamLoader,
        batchEnvelope: BatchEnvelope<*>
    ): ProcessBatchTask
}

@Singleton
@Secondary
class DefaultProcessBatchTaskFactory(
    private val streamsManager: StreamsManager,
) : ProcessBatchTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        streamLoader: StreamLoader,
        batchEnvelope: BatchEnvelope<*>
    ): ProcessBatchTask {
        return DefaultProcessBatchTask(batchEnvelope, streamLoader, taskLauncher)
    }
}
