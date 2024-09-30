/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.state.SyncManager
import io.airbyte.cdk.write.DestinationWriter
import io.airbyte.cdk.write.StreamLoader
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface OpenStreamTask : StreamTask

/**
 * Wraps @[StreamLoader.start] and starts the spill-to-disk tasks.
 *
 * TODO: There's no reason to wait on initialization to start spilling to disk.
 */
class DefaultOpenStreamTask(
    private val destinationWriter: DestinationWriter,
    private val syncManager: SyncManager,
    private val stream: DestinationStream,
    private val taskLauncher: DestinationTaskLauncher
) : OpenStreamTask {
    override suspend fun execute() {
        val streamLoader = destinationWriter.createStreamLoader(stream)
        streamLoader.start()
        syncManager.registerStartedStreamLoader(streamLoader)
        taskLauncher.handleStreamStarted(stream)
    }
}

interface OpenStreamTaskFactory {
    fun make(taskLauncher: DestinationTaskLauncher, stream: DestinationStream): OpenStreamTask
}

@Singleton
@Secondary
class DefaultOpenStreamTaskFactory(
    private val destinationWriter: DestinationWriter,
    private val syncManager: SyncManager
) : OpenStreamTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream
    ): OpenStreamTask {
        return DefaultOpenStreamTask(destinationWriter, syncManager, stream, taskLauncher)
    }
}
