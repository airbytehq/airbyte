/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.DestinationWriter
import jakarta.inject.Singleton

/** Wraps @[DestinationWriter.setup] and starts the open stream tasks. */
@Singleton
class SetupTask(
    private val destination: DestinationWriter,
) : Task() {
    override val terminalCondition: TerminalCondition = SelfTerminating

    override suspend fun execute() {
        destination.setup()
        taskLauncher!!.handleSetupComplete()
    }
}
