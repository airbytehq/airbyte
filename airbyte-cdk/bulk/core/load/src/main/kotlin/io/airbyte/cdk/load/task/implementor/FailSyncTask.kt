/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.ImplementorScope
import io.airbyte.cdk.load.write.DestinationWriter
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface FailSyncTask : ImplementorScope

/**
 * FailSyncTask is a task that is executed only when the destination itself fails during a sync. If
 * the sync is failed by upstream (e.g. an incomplete stream message is received), we do not call
 * this task. It is responsible for cleaning up resources and reporting the failure.
 */
class DefaultFailSyncTask(
    private val taskLauncher: DestinationTaskLauncher,
    private val destinationWriter: DestinationWriter,
    private val exception: Exception,
    private val syncManager: SyncManager,
    private val checkpointManager: CheckpointManager<*, *>,
) : FailSyncTask {
    private val log = KotlinLogging.logger {}

    override suspend fun execute() {
        // Ensure any remaining ready state gets captured: don't waste work!
        checkpointManager.flushReadyCheckpointMessages()
        val result = syncManager.markDestinationFailed(exception) // awaits stream completion
        log.info { "Calling teardown with failure result $result" }
        destinationWriter.teardown(result)
        taskLauncher.handleTeardownComplete(success = false)
    }
}

interface FailSyncTaskFactory {
    fun make(taskLauncher: DestinationTaskLauncher, exception: Exception): FailSyncTask
}

@Singleton
@Secondary
class DefaultFailSyncTaskFactory(
    private val syncManager: SyncManager,
    private val checkpointManager: CheckpointManager<*, *>,
    private val destinationWriter: DestinationWriter
) : FailSyncTaskFactory {
    override fun make(taskLauncher: DestinationTaskLauncher, exception: Exception): FailSyncTask {
        return DefaultFailSyncTask(
            taskLauncher,
            destinationWriter,
            exception,
            syncManager,
            checkpointManager,
        )
    }
}
