/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.state.StreamIncompleteResult
import io.airbyte.cdk.state.SyncManager
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface FailStreamTask : Task

/**
 * FailStreamTask is a task that is executed when a stream fails. It is responsible for cleaning up
 * resources and reporting the failure.
 */
class DefaultFailStreamTask(
    private val exceptionHandler: DestinationTaskLauncherExceptionHandler,
    private val exception: Exception,
    private val syncManager: SyncManager,
    private val stream: DestinationStream
) : FailStreamTask {
    val log = KotlinLogging.logger {}

    override suspend fun execute() {
        val streamManager = syncManager.getStreamManager(stream.descriptor)
        streamManager.markFailed(exception)
        val streamResult = streamManager.awaitStreamResult()
        val incompleteResult =
            if (streamResult is StreamIncompleteResult) {
                streamResult
            } else {
                null
            }
        // TODO: Bit of smell here, suggests we should be fetching the StreamLoader
        // lazily+unconditionally
        //  through the DestinationWriter (via an injected wrapper?)
        syncManager.getStreamLoaderOrNull(stream.descriptor)?.close(incompleteResult)
            ?: log.warn {
                "StreamLoader not found for stream ${stream.descriptor}, cannot call close."
            }
        exceptionHandler.handleSyncFailure(exception)
    }
}

interface FailStreamTaskFactory {
    fun make(
        exceptionHandler: DestinationTaskLauncherExceptionHandler,
        exception: Exception,
        stream: DestinationStream
    ): FailStreamTask
}

@Singleton
@Secondary
class DefaultFailStreamTaskFactory(private val syncManager: SyncManager) : FailStreamTaskFactory {
    override fun make(
        exceptionHandler: DestinationTaskLauncherExceptionHandler,
        exception: Exception,
        stream: DestinationStream
    ): FailStreamTask {
        return DefaultFailStreamTask(exceptionHandler, exception, syncManager, stream)
    }
}
