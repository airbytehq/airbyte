/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.state.CheckpointManager
import io.airbyte.cdk.state.SyncManager
import io.airbyte.cdk.write.DestinationWriter
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean

interface TeardownTask : SyncTask

/**
 * Wraps @[DestinationWriter.teardown] and stops the task launcher.
 *
 * TODO: Report teardown-complete and let the task launcher decide what to do next.
 */
class DefaultTeardownTask(
    private val checkpointManager: CheckpointManager<*, *>,
    private val syncManager: SyncManager,
    private val destination: DestinationWriter,
    private val taskLauncher: DestinationTaskLauncher
) : TeardownTask {
    val log = KotlinLogging.logger {}

    private val teardownHasRun = AtomicBoolean(false)

    override suspend fun execute() {
        // TODO: This should be its own task, dispatched on a timer or something.
        checkpointManager.flushReadyCheckpointMessages()

        // Run the task exactly once, and only after all streams have closed.
        if (teardownHasRun.compareAndSet(false, true)) {
            syncManager.awaitAllStreamsClosed()
            log.info { "Starting teardown task" }

            destination.teardown()
            taskLauncher.handleTeardownComplete()
        }
    }
}

interface TeardownTaskFactory {
    fun make(taskLauncher: DestinationTaskLauncher): TeardownTask
}

@Singleton
@Secondary
class DefaultTeardownTaskFactory(
    private val checkpointManager: CheckpointManager<*, *>,
    private val syncManager: SyncManager,
    private val destination: DestinationWriter,
) : TeardownTaskFactory {
    override fun make(taskLauncher: DestinationTaskLauncher): TeardownTask {
        return DefaultTeardownTask(checkpointManager, syncManager, destination, taskLauncher)
    }
}
