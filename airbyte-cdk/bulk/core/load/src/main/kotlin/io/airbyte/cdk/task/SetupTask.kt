/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.write.Destination
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

/**
 * Wraps @[Destination.setup] and starts the open stream tasks.
 *
 * TODO: This should call something like "TaskLauncher.setupComplete" and let it decide what to do
 * next.
 */
class SetupTask(
    private val destination: Destination,
    private val taskLauncher: DestinationTaskLauncher
) : Task {
    override suspend fun execute() {
        destination.setup()
        taskLauncher.startOpenStreamTasks()
    }
}

@Singleton
@Secondary
class SetupTaskFactory(
    private val destination: Destination,
) {
    fun make(taskLauncher: DestinationTaskLauncher): SetupTask {
        return SetupTask(destination, taskLauncher)
    }
}
