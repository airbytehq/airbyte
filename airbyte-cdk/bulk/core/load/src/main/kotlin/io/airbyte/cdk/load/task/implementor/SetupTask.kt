/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.DestinationWriter
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface SetupTask : Task

/** Wraps @[DestinationWriter.setup] and starts the open stream tasks. */
class DefaultSetupTask(
    private val destination: DestinationWriter,
    private val taskLauncher: DestinationTaskLauncher,
) : SetupTask {
    override val terminalCondition: TerminalCondition = SelfTerminating

    override suspend fun execute() {
        destination.setup()
        taskLauncher.handleSetupComplete()
    }
}

interface SetupTaskFactory {
    fun make(taskLauncher: DestinationTaskLauncher): SetupTask
}

@Singleton
@Secondary
class DefaultSetupTaskFactory(
    private val destination: DestinationWriter,
) : SetupTaskFactory {
    override fun make(taskLauncher: DestinationTaskLauncher): SetupTask {
        return DefaultSetupTask(destination, taskLauncher)
    }
}
