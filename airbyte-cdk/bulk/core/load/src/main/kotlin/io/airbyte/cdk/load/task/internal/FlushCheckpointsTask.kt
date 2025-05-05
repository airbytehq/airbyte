/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import jakarta.inject.Singleton

@Singleton
class FlushCheckpointsTask(
    private val checkpointManager: CheckpointManager<*>,
) : Task() {
    override val terminalCondition: TerminalCondition = SelfTerminating

    override suspend fun execute() {
        checkpointManager.flushReadyCheckpointMessages()
    }
}
