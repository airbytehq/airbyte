/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.state.SyncManager
import io.airbyte.cdk.write.StreamLoader
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface CloseStreamTask : StreamTask

/**
 * Wraps @[StreamLoader.close] and marks the stream as closed in the stream manager. Also starts the
 * teardown task.
 */
class DefaultCloseStreamTask(
    private val syncManager: SyncManager,
    private val stream: DestinationStream,
    private val taskLauncher: DestinationTaskLauncher
) : CloseStreamTask {

    override suspend fun execute() {
        val streamLoader = syncManager.getOrAwaitStreamLoader(stream.descriptor)
        streamLoader.close()
        syncManager.getStreamManager(stream.descriptor).markClosed()
        taskLauncher.handleStreamClosed(streamLoader.stream)
    }
}

interface CloseStreamTaskFactory {
    fun make(taskLauncher: DestinationTaskLauncher, stream: DestinationStream): CloseStreamTask
}

@Singleton
@Secondary
class DefaultCloseStreamTaskFactory(private val syncManager: SyncManager) : CloseStreamTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream
    ): CloseStreamTask {
        return DefaultCloseStreamTask(syncManager, stream, taskLauncher)
    }
}
