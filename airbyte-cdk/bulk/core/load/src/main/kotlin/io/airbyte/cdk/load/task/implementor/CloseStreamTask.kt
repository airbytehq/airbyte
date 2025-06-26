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
import jakarta.inject.Singleton

class CloseStreamTask(
    private val syncManager: SyncManager,
    val streamDescriptor: DestinationStream.Descriptor,
    private val taskLauncher: DestinationTaskLauncher
) : Task {
    override val terminalCondition: TerminalCondition = SelfTerminating

    override suspend fun execute() {
        val streamLoader = syncManager.getOrAwaitStreamLoader(streamDescriptor)
        streamLoader.close(
            hadNonzeroRecords = syncManager.getStreamManager(streamDescriptor).hadNonzeroRecords(),
        )
        syncManager.getStreamManager(streamDescriptor).markProcessingSucceeded()
        taskLauncher.handleStreamClosed()
    }
}

@Singleton
class CloseStreamTaskFactory(
    private val syncManager: SyncManager,
) {
    fun make(
        taskLauncher: DestinationTaskLauncher,
        streamDescriptor: DestinationStream.Descriptor,
    ): CloseStreamTask {
        return CloseStreamTask(syncManager, streamDescriptor, taskLauncher)
    }
}
