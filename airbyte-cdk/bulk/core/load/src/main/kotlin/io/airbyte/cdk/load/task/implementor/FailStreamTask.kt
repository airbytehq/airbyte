/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamIncompleteResult
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskExceptionHandler
import io.airbyte.cdk.load.task.ImplementorScope
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface FailStreamTask : ImplementorScope

/**
 * FailStreamTask is a task that is executed when a stream fails. It is responsible for cleaning up
 * resources and reporting the failure.
 */
class DefaultFailStreamTask(
    private val exceptionHandler: DestinationTaskExceptionHandler<*, *>,
    private val exception: Exception,
    private val syncManager: SyncManager,
    private val stream: DestinationStream.Descriptor,
    private val kill: Boolean,
) : FailStreamTask {
    val log = KotlinLogging.logger {}

    override suspend fun execute() {
        val streamManager = syncManager.getStreamManager(stream)
        if (kill) {
            if (!streamManager.markKilled(exception)) {
                log.info { "Stream $stream already complete, skipping kill." }
                return
            }
        } else {
            if (!streamManager.markFailed(exception)) {
                throw IllegalStateException(
                    "Cannot fail stream $stream, which is already complete."
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
        // TODO: Bit of smell here, suggests we should be fetching the StreamLoader
        // lazily+unconditionally
        //  through the DestinationWriter (via an injected wrapper?)
        syncManager.getStreamLoaderOrNull(stream)?.close(incompleteResult)
            ?: log.warn { "StreamLoader not found for stream $stream, cannot call close." }
    }
}

interface FailStreamTaskFactory {
    fun make(
        exceptionHandler: DestinationTaskExceptionHandler<*, *>,
        exception: Exception,
        stream: DestinationStream.Descriptor,
        kill: Boolean,
    ): FailStreamTask
}

@Singleton
@Secondary
class DefaultFailStreamTaskFactory(private val syncManager: SyncManager) : FailStreamTaskFactory {
    override fun make(
        exceptionHandler: DestinationTaskExceptionHandler<*, *>,
        exception: Exception,
        stream: DestinationStream.Descriptor,
        kill: Boolean,
    ): FailStreamTask {
        return DefaultFailStreamTask(exceptionHandler, exception, syncManager, stream, kill)
    }
}
