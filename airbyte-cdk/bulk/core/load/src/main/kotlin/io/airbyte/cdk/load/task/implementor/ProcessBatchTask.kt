/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.ImplementorTask
import io.airbyte.cdk.load.task.StreamTask
import io.airbyte.cdk.load.write.DestinationWriterInternal
import io.airbyte.cdk.load.write.StreamLoader
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface ProcessBatchTask : StreamTask, ImplementorTask

/** Wraps @[StreamLoader.processBatch] and handles the resulting batch. */
class DefaultProcessBatchTask<B>(
    private val destinationWriterInternal: DestinationWriterInternal<B>,
    private val batchEnvelope: BatchEnvelope<B>,
    override val stream: DestinationStream,
    private val taskLauncher: DestinationTaskLauncher<B>
) : ProcessBatchTask {
    override suspend fun execute() {
        val streamLoader = destinationWriterInternal.awaitStreamLoader(stream)
        val nextBatch = streamLoader.processBatch(batchEnvelope.batch)
        val nextWrapped = batchEnvelope.withBatch(nextBatch)
        taskLauncher.handleNewBatch(stream, nextWrapped)
    }
}

interface ProcessBatchTaskFactory<B> {
    fun make(
        taskLauncher: DestinationTaskLauncher<B>,
        stream: DestinationStream,
        batchEnvelope: BatchEnvelope<B>
    ): ProcessBatchTask
}

@Singleton
@Secondary
class DefaultProcessBatchTaskFactory<B>(
    val destinationWriterInternal: DestinationWriterInternal<B>
):
    ProcessBatchTaskFactory<B> {
    override fun make(
        taskLauncher: DestinationTaskLauncher<B>,
        stream: DestinationStream,
        batchEnvelope: BatchEnvelope<B>
    ): ProcessBatchTask {
        return DefaultProcessBatchTask(destinationWriterInternal, batchEnvelope, stream, taskLauncher)
    }
}
