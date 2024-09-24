/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.write.StreamLoader
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface CloseStreamTask : Task

/**
 * Wraps @[StreamLoader.close] and marks the stream as closed in the stream manager. Also starts the
 * teardown task.
 */
class DefaultCloseStreamTask(
    private val streamLoader: StreamLoader,
    private val taskLauncher: DestinationTaskLauncher
) : CloseStreamTask {

    override suspend fun execute() {
        streamLoader.close()
        taskLauncher.handleStreamClosed(streamLoader.stream)
    }
}

interface CloseStreamTaskFactory {
    fun make(taskLauncher: DestinationTaskLauncher, streamLoader: StreamLoader): CloseStreamTask
}

@Singleton
@Secondary
class DefaultCloseStreamTaskFactory : CloseStreamTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        streamLoader: StreamLoader
    ): CloseStreamTask {
        return DefaultCloseStreamTask(streamLoader, taskLauncher)
    }
}
