/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.state.SyncManager
import io.airbyte.cdk.write.DestinationWriter
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface FailSyncTask : Task

/**
 * FailSyncTask is a task that is executed when a sync fails. It is responsible for cleaning up
 * resources and reporting the failure.
 */
class DefaultFailSyncTask(
    private val exceptionHandler: DestinationTaskLauncherExceptionHandler,
    private val destinationWriter: DestinationWriter,
    private val exception: Exception,
    private val syncManager: SyncManager
) : FailSyncTask {
    override suspend fun execute() {
        val result = syncManager.markFailed(exception)
        destinationWriter.teardown(result)
        exceptionHandler.stop()
    }
}

interface FailSyncTaskFactory {
    fun make(
        exceptionHandler: DestinationTaskLauncherExceptionHandler,
        exception: Exception
    ): FailSyncTask
}

@Singleton
@Secondary
class DefaultFailSyncTaskFactory(
    private val syncManager: SyncManager,
    private val destinationWriter: DestinationWriter
) : FailSyncTaskFactory {
    override fun make(
        exceptionHandler: DestinationTaskLauncherExceptionHandler,
        exception: Exception
    ): FailSyncTask {
        return DefaultFailSyncTask(exceptionHandler, destinationWriter, exception, syncManager)
    }
}
