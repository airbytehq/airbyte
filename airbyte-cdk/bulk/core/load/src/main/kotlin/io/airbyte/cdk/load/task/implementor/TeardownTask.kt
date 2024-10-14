/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.ShutdownScope
import io.airbyte.cdk.load.task.SyncLevel
import io.airbyte.cdk.load.util.setOnce
import io.airbyte.cdk.load.write.DestinationWriter
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean

interface TeardownTask : SyncLevel, ShutdownScope

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

    companion object {
        private val teardownHasRun = AtomicBoolean(false)
    }

    override suspend fun execute() {
        // Run the task exactly once, and only after all streams have closed.
        if (teardownHasRun.setOnce()) {
            syncManager.awaitInputProcessingComplete()
            checkpointManager.awaitAllCheckpointsFlushed()

            log.info { "Teardown task awaiting stream completion" }
            if (!syncManager.awaitAllStreamsCompletedSuccessfully()) {
                log.info { "Streams failed to complete successfully, doing nothing." }
                return
            }

            log.info { "Starting teardown task" }
            destination.teardown()
            log.info { "Teardown task complete, marking sync succeeded." }
            syncManager.markSucceeded()
            taskLauncher.handleTeardownComplete()
        } else {
            log.info { "Teardown already initiated, doing nothing." }
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
