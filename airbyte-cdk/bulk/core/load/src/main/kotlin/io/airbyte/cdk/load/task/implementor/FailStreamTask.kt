/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamIncompleteResult
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskExceptionHandler
import io.airbyte.cdk.load.task.ImplementorTask
import io.airbyte.cdk.load.write.DestinationWriterInternal
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface FailStreamTask : ImplementorTask

/**
 * FailStreamTask is a task that is executed when a stream fails. It is responsible for cleaning up
 * resources and reporting the failure.
 */
class DefaultFailStreamTask(
    private val writer: DestinationWriterInternal<*>,
    private val exceptionHandler: DestinationTaskExceptionHandler<*>,
    private val exception: Exception,
    private val syncManager: SyncManager,
    private val stream: DestinationStream,
    private val kill: Boolean,
) : FailStreamTask {
    val log = KotlinLogging.logger {}

    override suspend fun execute() {
        val streamManager = syncManager.getStreamManager(stream.descriptor)
        if (kill) {
            if (!streamManager.markKilled(exception)) {
                log.info { "Stream ${stream.descriptor} already complete, skipping kill." }
                return
            }
        } else {
            if (!streamManager.markFailed(exception)) {
                throw IllegalStateException(
                    "Cannot fail stream ${stream.descriptor}, which is already complete."
                )
            }
            // Stream failure implies sync failure
            exceptionHandler.handleSyncFailure(exception)
        }

        val streamResult = streamManager.awaitStreamResult()
        val incompleteResult =
            if (streamResult is StreamIncompleteResult) {
                streamResult
            } else {
                null
            }
        // We call getOrCreate here in case the failure occurred before open was complete
        writer.getOrCreateStreamLoader(stream).close(incompleteResult)
    }
}

interface FailStreamTaskFactory {
    fun make(
        exceptionHandler: DestinationTaskExceptionHandler<*>,
        exception: Exception,
        stream: DestinationStream,
        kill: Boolean,
    ): FailStreamTask
}

@Singleton
@Secondary
class DefaultFailStreamTaskFactory(
    private val writer: DestinationWriterInternal<*>,
    private val syncManager: SyncManager
) : FailStreamTaskFactory {
    override fun make(
        exceptionHandler: DestinationTaskExceptionHandler<*>,
        exception: Exception,
        stream: DestinationStream,
        kill: Boolean,
    ): FailStreamTask {
        return DefaultFailStreamTask(writer, exceptionHandler, exception, syncManager, stream, kill)
    }
}
