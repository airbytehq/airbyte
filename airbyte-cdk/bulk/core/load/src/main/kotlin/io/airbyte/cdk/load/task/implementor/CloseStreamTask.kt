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
import io.airbyte.cdk.load.write.StreamLoader
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

/**
 * Wraps @[StreamLoader.close] and marks the stream as closed in the stream manager. Also starts the
 * teardown task. Called after the end of stream message (complete OR incomplete) has been received
 * and all record messages have been processed.
 */
class CloseStreamTask(
    private val syncManager: SyncManager,
    val streamDescriptor: DestinationStream.Descriptor,
) : Task() {
    override val terminalCondition: TerminalCondition = SelfTerminating

    override suspend fun execute() {
        val streamLoader = syncManager.getOrAwaitStreamLoader(streamDescriptor)
        streamLoader.close(
            hadNonzeroRecords = syncManager.getStreamManager(streamDescriptor).hadNonzeroRecords(),
        )
        syncManager.getStreamManager(streamDescriptor).markProcessingSucceeded()
        taskLauncher!!.handleStreamClosed()
    }
}
