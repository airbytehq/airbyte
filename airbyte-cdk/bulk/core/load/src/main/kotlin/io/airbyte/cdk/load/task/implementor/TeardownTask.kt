/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.ImplementorScope
import io.airbyte.cdk.load.task.SyncLevel
import io.airbyte.cdk.load.write.DestinationWriter
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface TeardownTask : SyncLevel, ImplementorScope

/**
 * Wraps @[DestinationWriter.teardown] and stops the task launcher.
 *
 * TODO: Report teardown-complete and let the task launcher decide what to do next.
 */
class DefaultTeardownTask(
    private val checkpointManager: CheckpointManager<*, *>,
    private val syncManager: SyncManager,
    private val destination: DestinationWriter,
    private val taskLauncher: DestinationTaskLauncher,
) : TeardownTask {
    val log = KotlinLogging.logger {}

    override suspend fun execute() {
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
