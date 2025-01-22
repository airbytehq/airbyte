/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface OpenStreamTask : Task

/**
 * Wraps @[StreamLoader.start] and starts the spill-to-disk tasks.
 *
 * TODO: There's no reason to wait on initialization to start spilling to disk.
 */
class DefaultOpenStreamTask(
    private val destinationWriter: DestinationWriter,
    private val syncManager: SyncManager,
    val streamDescriptor: DestinationStream.Descriptor,
    private val taskLauncher: DestinationTaskLauncher,
    private val stream: DestinationStream,
) : OpenStreamTask {
    override val terminalCondition: TerminalCondition = SelfTerminating

    override suspend fun execute() {
        val streamLoader = destinationWriter.createStreamLoader(stream)
        val result = runCatching {
            streamLoader.start()
            streamLoader
        }
        syncManager.registerStartedStreamLoader(stream.descriptor, result)
        result.getOrThrow() // throw after registering the failure
        taskLauncher.handleStreamStarted(streamDescriptor)
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
        return DefaultOpenStreamTask(
            destinationWriter,
            syncManager,
            stream.descriptor,
            taskLauncher,
            stream
        )
    }
}
