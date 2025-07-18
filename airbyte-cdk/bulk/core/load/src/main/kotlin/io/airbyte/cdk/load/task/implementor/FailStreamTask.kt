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
import jakarta.inject.Singleton

class FailStreamTask(
    private val taskLauncher: DestinationTaskLauncher,
    private val exception: Exception,
    private val syncManager: SyncManager,
    private val stream: DestinationStream.Descriptor,
    private val shouldRunStreamLoaderClose: Boolean,
) : Task {
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
                if (shouldRunStreamLoaderClose) {
                    try {
                        syncManager
                            .getStreamLoaderOrNull(stream)
                            ?.close(
                                hadNonzeroRecords = streamManager.hadNonzeroRecords(),
                                streamResult,
                            )
                            ?: log.warn {
                                "StreamLoader not found for stream $stream, cannot call close."
                            }
                    } catch (e: Exception) {
                        log.warn(e) {
                            "Exception while closing StreamLoader for $stream after another failure in the sync. Ignoring this exception and continuing with shutdown."
                        }
                    }
                } else {
                    log.info { "Skipping StreamLoader.close for stream $stream" }
                }
            }
        }
        taskLauncher.handleFailStreamComplete(exception)
    }
}

@Singleton
class FailStreamTaskFactory(private val syncManager: SyncManager) {
    fun make(
        taskLauncher: DestinationTaskLauncher,
        exception: Exception,
        stream: DestinationStream.Descriptor,
        shouldRunStreamLoaderClose: Boolean,
    ): FailStreamTask {
        return FailStreamTask(
            taskLauncher,
            exception,
            syncManager,
            stream,
            shouldRunStreamLoaderClose = shouldRunStreamLoaderClose,
        )
    }
}
