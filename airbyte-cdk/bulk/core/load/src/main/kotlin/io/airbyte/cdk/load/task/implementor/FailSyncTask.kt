/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskExceptionHandler
import io.airbyte.cdk.load.task.ShutdownScope
import io.airbyte.cdk.load.util.setOnce
import io.airbyte.cdk.load.write.DestinationWriter
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean

interface FailSyncTask : ShutdownScope

/**
 * FailSyncTask is a task that is executed when a sync fails. It is responsible for cleaning up
 * resources and reporting the failure.
 */
class DefaultFailSyncTask(
    private val exceptionHandler: DestinationTaskExceptionHandler<*, *>,
    private val destinationWriter: DestinationWriter,
    private val exception: Exception,
    private val syncManager: SyncManager,
    private val checkpointManager: CheckpointManager<*, *>
) : FailSyncTask {
    private val log = KotlinLogging.logger {}

    companion object {
        private val syncFailedHasRun = AtomicBoolean(false)
    }

    override suspend fun execute() {
        if (syncFailedHasRun.setOnce()) {
            // Ensure any remaining ready state gets captured: don't waste work!
            checkpointManager.flushReadyCheckpointMessages()
            val result = syncManager.markFailed(exception) // awaits stream completion
            log.info { "Calling teardown with failure result $result" }
            exceptionHandler.handleSyncFailed()
            // Do this cleanup last, after all the tasks have had a decent chance to finish.
            destinationWriter.teardown(result)
        } else {
            log.info { "Fail sync task already initiated, doing nothing." }
        }
    }
}

interface FailSyncTaskFactory {
    fun make(
        exceptionHandler: DestinationTaskExceptionHandler<*, *>,
        exception: Exception
    ): FailSyncTask
}

@Singleton
@Secondary
class DefaultFailSyncTaskFactory(
    private val syncManager: SyncManager,
    private val checkpointManager: CheckpointManager<*, *>,
    private val destinationWriter: DestinationWriter
) : FailSyncTaskFactory {

    override fun make(
        exceptionHandler: DestinationTaskExceptionHandler<*, *>,
        exception: Exception
    ): FailSyncTask {
        return DefaultFailSyncTask(
            exceptionHandler,
            destinationWriter,
            exception,
            syncManager,
            checkpointManager
        )
    }
}
