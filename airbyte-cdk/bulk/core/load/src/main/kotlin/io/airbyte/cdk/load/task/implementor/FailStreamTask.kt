/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.state.StreamProcessingSucceeded
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface FailStreamTask : Task

/**
 * FailStreamTask is a task that is executed when the processing of a stream fails in the
 * destination. It is responsible for cleaning up resources and reporting the failure.
 */
class DefaultFailStreamTask(
    private val taskLauncher: DestinationTaskLauncher,
    private val exception: Exception,
    private val syncManager: SyncManager,
    private val stream: DestinationStream.Descriptor,
) : FailStreamTask {
    val log = KotlinLogging.logger {}

    override val terminalCondition: TerminalCondition = SelfTerminating

    override suspend fun execute() {
        val streamManager = syncManager.getStreamManager(stream)
        syncManager.registerStartedStreamLoader(stream, Result.failure(exception))
        streamManager.markProcessingFailed(exception)
        when (val streamResult = streamManager.awaitStreamResult()) {
            is StreamProcessingSucceeded -> {
                log.info { "Cannot fail stream $stream, which is already complete, doing nothing." }
            }
            is StreamProcessingFailed -> {
                syncManager.getStreamLoaderOrNull(stream)?.close(streamResult)
                    ?: log.warn { "StreamLoader not found for stream $stream, cannot call close." }
            }
        }
        taskLauncher.handleFailStreamComplete(stream, exception)
    }
}

interface FailStreamTaskFactory {
    fun make(
        taskLauncher: DestinationTaskLauncher,
        exception: Exception,
        stream: DestinationStream.Descriptor,
    ): FailStreamTask
}

@Singleton
@Secondary
class DefaultFailStreamTaskFactory(private val syncManager: SyncManager) : FailStreamTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        exception: Exception,
        stream: DestinationStream.Descriptor,
    ): FailStreamTask {
        return DefaultFailStreamTask(taskLauncher, exception, syncManager, stream)
    }
}
