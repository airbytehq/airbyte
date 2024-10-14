/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.ImplementorTask
import io.airbyte.cdk.load.task.StreamTask
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.DestinationWriterInternal
import io.airbyte.cdk.load.write.StreamLoader
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface OpenStreamTask : StreamTask, ImplementorTask

/**
 * Wraps @[StreamLoader.start] and starts the spill-to-disk tasks.
 *
 * TODO: There's no reason to wait on initialization to start spilling to disk.
 */
class DefaultOpenStreamTask(
    private val destinationWriter: DestinationWriterInternal<*>,
    override val stream: DestinationStream,
    private val taskLauncher: DestinationTaskLauncher<*>
) : OpenStreamTask {
    override suspend fun execute() {
        val streamLoader = destinationWriter.getOrCreateStreamLoader(stream)
        streamLoader.start()
        taskLauncher.handleStreamStarted(stream)
    }
}

interface OpenStreamTaskFactory {
    fun make(taskLauncher: DestinationTaskLauncher<*>, stream: DestinationStream): OpenStreamTask
}

@Singleton
@Secondary
class DefaultOpenStreamTaskFactory(
    private val destinationWriter: DestinationWriterInternal<*>,
) : OpenStreamTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher<*>,
        stream: DestinationStream
    ): OpenStreamTask {
        return DefaultOpenStreamTask(destinationWriter, stream, taskLauncher)
    }
}
