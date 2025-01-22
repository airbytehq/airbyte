/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

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
) : SetupTask {
    override val terminalCondition: TerminalCondition = SelfTerminating

    override suspend fun execute() {
        destination.setup()
    }
}

interface SetupTaskFactory {
    fun make(): SetupTask
}

@Singleton
@Secondary
class DefaultSetupTaskFactory(
    private val destination: DestinationWriter,
) : SetupTaskFactory {
    override fun make(): SetupTask {
        return DefaultSetupTask(destination)
    }
}
