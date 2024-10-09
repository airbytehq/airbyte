/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskExceptionHandler
import io.airbyte.cdk.load.task.ImplementorTask
import io.airbyte.cdk.load.util.setOnce
import io.airbyte.cdk.load.write.DestinationWriter
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean

interface FailSyncTask : ImplementorTask

/**
 * FailSyncTask is a task that is executed when a sync fails. It is responsible for cleaning up
 * resources and reporting the failure.
 */
class DefaultFailSyncTask(
    private val exceptionHandler: DestinationTaskExceptionHandler<*>,
    private val destinationWriter: DestinationWriter,
    private val exception: Exception,
    private val syncManager: SyncManager,
) : FailSyncTask {
    private val log = KotlinLogging.logger {}
    private val teardownRan = AtomicBoolean(false)

    override suspend fun execute() {
        if (teardownRan.setOnce()) {
            val result = syncManager.markFailed(exception) // awaits stream completion
            log.info { "Calling teardown with failure result $result" }
            destinationWriter.teardown(result)
            exceptionHandler.handleTeardownComplete()
        } else {
            log.info { "Teardown already ran, doing nothing." }
        }
    }
}

interface FailSyncTaskFactory {
    fun make(
        exceptionHandler: DestinationTaskExceptionHandler<*>,
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
        exceptionHandler: DestinationTaskExceptionHandler<*>,
        exception: Exception
    ): FailSyncTask {
        return DefaultFailSyncTask(exceptionHandler, destinationWriter, exception, syncManager)
    }
}
