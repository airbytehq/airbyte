/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.ImplementorScope
import io.airbyte.cdk.load.task.StreamLevel
import io.airbyte.cdk.load.write.StreamLoader
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface CloseStreamTask : StreamLevel, ImplementorScope

/**
 * Wraps @[StreamLoader.close] and marks the stream as closed in the stream manager. Also starts the
 * teardown task.
 */
class DefaultCloseStreamTask(
    private val syncManager: SyncManager,
    override val stream: DestinationStream,
    private val taskLauncher: DestinationTaskLauncher
) : CloseStreamTask {

    override suspend fun execute() {
        val streamLoader = syncManager.getOrAwaitStreamLoader(stream.descriptor)
        streamLoader.close()
        syncManager.getStreamManager(stream.descriptor).markSucceeded()
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
