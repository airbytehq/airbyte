/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.state.SyncManager
import io.airbyte.cdk.write.StreamLoader
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface ProcessBatchTask : StreamTask

/** Wraps @[StreamLoader.processBatch] and handles the resulting batch. */
class DefaultProcessBatchTask(
    private val syncManager: SyncManager,
    private val batchEnvelope: BatchEnvelope<*>,
    private val stream: DestinationStream,
    private val taskLauncher: DestinationTaskLauncher
) : ProcessBatchTask {
    override suspend fun execute() {
        val streamLoader = syncManager.getOrAwaitStreamLoader(stream.descriptor)
        val nextBatch = streamLoader.processBatch(batchEnvelope.batch)
        val nextWrapped = batchEnvelope.withBatch(nextBatch)
        taskLauncher.handleNewBatch(stream, nextWrapped)
    }
}

interface ProcessBatchTaskFactory {
    fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream,
        batchEnvelope: BatchEnvelope<*>
    ): ProcessBatchTask
}

@Singleton
@Secondary
class DefaultProcessBatchTaskFactory(private val syncManager: SyncManager) :
    ProcessBatchTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream,
        batchEnvelope: BatchEnvelope<*>
    ): ProcessBatchTask {
        return DefaultProcessBatchTask(syncManager, batchEnvelope, stream, taskLauncher)
    }
}
