/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.KillableScope
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Named
import jakarta.inject.Singleton

interface ProcessBatchTask : KillableScope

/** Wraps @[StreamLoader.processBatch] and handles the resulting batch. */
class DefaultProcessBatchTask(
    private val syncManager: SyncManager,
    private val batchQueue: MultiProducerChannel<BatchEnvelope<*>>,
    private val taskLauncher: DestinationTaskLauncher
) : ProcessBatchTask {
    val log = KotlinLogging.logger {}
    override suspend fun execute() {
        batchQueue.consume().collect { batchEnvelope ->
            val streamLoader = syncManager.getOrAwaitStreamLoader(batchEnvelope.streamDescriptor)
            val nextBatch = streamLoader.processBatch(batchEnvelope.batch)
            val nextWrapped = batchEnvelope.withBatch(nextBatch)
            taskLauncher.handleNewBatch(nextWrapped.streamDescriptor, nextWrapped)
        }
    }
}

interface ProcessBatchTaskFactory {
    fun make(
        taskLauncher: DestinationTaskLauncher,
    ): ProcessBatchTask
}

@Singleton
@Secondary
class DefaultProcessBatchTaskFactory(
    private val syncManager: SyncManager,
    @Named("batchQueue") private val batchQueue: MultiProducerChannel<BatchEnvelope<*>>
) : ProcessBatchTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
    ): ProcessBatchTask {
        return DefaultProcessBatchTask(syncManager, batchQueue, taskLauncher)
    }
}
