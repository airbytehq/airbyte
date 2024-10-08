/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.SpilledRawMessagesLocalFile
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.ImplementorScope
import io.airbyte.cdk.load.task.StreamLevel
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface ProcessLocalFileTask : StreamLevel, ImplementorScope

class DefaultProcessLocalFileTask(
    private val syncManager: SyncManager,
    override val stream: DestinationStream,
    private val localFileWrapped: BatchEnvelope<SpilledRawMessagesLocalFile>,
    private val taskLauncher: DestinationTaskLauncher
) : ProcessLocalFileTask {
    val log = KotlinLogging.logger {}

    override suspend fun execute() {
        val streamLoader = syncManager.getOrAwaitStreamLoader(stream.descriptor)

        log.info { "Maybe processing local file." }
        val maybeNewBatch = streamLoader.processStagedLocalFile(localFileWrapped.batch)
        if (maybeNewBatch == localFileWrapped.batch) {
            log.info { "Client deferred processing of local file." }
            taskLauncher.handleUnhandledLocalFile(stream, localFileWrapped)
        } else {
            log.info { "Client handled local file, deleting." }
            localFileWrapped.batch.localFile.delete()
            taskLauncher.handleNewBatch(stream, localFileWrapped.withBatch(maybeNewBatch))
        }
    }
}

interface ProcessLocalFileTaskFactory {
    fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream,
        localFileWrapped: BatchEnvelope<SpilledRawMessagesLocalFile>
    ): ProcessLocalFileTask
}

@Singleton
@Secondary
class DefaultProcessLocalFileTaskFactory(private val syncManager: SyncManager) :
    ProcessLocalFileTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream,
        localFileWrapped: BatchEnvelope<SpilledRawMessagesLocalFile>
    ): ProcessLocalFileTask {
        return DefaultProcessLocalFileTask(syncManager, stream, localFileWrapped, taskLauncher)
    }
}
