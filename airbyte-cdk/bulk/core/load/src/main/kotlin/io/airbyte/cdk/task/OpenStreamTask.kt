/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.write.DestinationWriteOperation
import io.airbyte.cdk.write.StreamLoader
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface OpenStreamTask : Task

/**
 * Wraps @[StreamLoader.start] and starts the spill-to-disk tasks.
 *
 * TODO: There's no reason to wait on initialization to start spilling to disk.
 */
class DefaultOpenStreamTask(
    private val streamLoader: StreamLoader,
    private val taskLauncher: DestinationTaskLauncher
) : OpenStreamTask {
    override suspend fun execute() {
        streamLoader.start()
        taskLauncher.handleStreamOpen(streamLoader)
    }
}

interface OpenStreamTaskFactory {
    fun make(taskLauncher: DestinationTaskLauncher, stream: DestinationStream): OpenStreamTask
}

@Singleton
@Secondary
class DefaultOpenStreamTaskFactory(
    private val destination: DestinationWriteOperation,
) : OpenStreamTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream
    ): OpenStreamTask {
        return DefaultOpenStreamTask(destination.getStreamLoader(stream), taskLauncher)
    }
}
