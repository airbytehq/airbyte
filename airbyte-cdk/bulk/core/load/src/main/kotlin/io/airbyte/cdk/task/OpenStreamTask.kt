/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.write.DestinationWrite
import io.airbyte.cdk.write.StreamLoader
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

/**
 * Wraps @[StreamLoader.start] and starts the spill-to-disk tasks.
 *
 * TODO: There's no reason to wait on initialization to start spilling to disk.
 */
class OpenStreamTask(
    private val streamLoader: StreamLoader,
    private val taskLauncher: DestinationTaskLauncher
) : Task {
    override suspend fun execute() {
        streamLoader.start()
        taskLauncher.startSpillToDiskTasks(streamLoader)
    }
}

@Singleton
@Secondary
class OpenStreamTaskFactory(
    private val destination: DestinationWrite,
) {
    fun make(taskLauncher: DestinationTaskLauncher, stream: DestinationStream): OpenStreamTask {
        return OpenStreamTask(destination.getStreamLoader(stream), taskLauncher)
    }
}
