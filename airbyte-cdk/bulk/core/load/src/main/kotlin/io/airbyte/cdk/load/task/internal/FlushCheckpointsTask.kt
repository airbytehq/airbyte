/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface FlushCheckpointsTask : Task

class DefaultFlushCheckpointsTask(
    private val checkpointManager: CheckpointManager<*, *>,
) : FlushCheckpointsTask {
    override val terminalCondition: TerminalCondition = SelfTerminating

    override suspend fun execute() {
        checkpointManager.flushReadyCheckpointMessages()
    }
}

interface FlushCheckpointsTaskFactory {
    fun make(): FlushCheckpointsTask
}

@Singleton
@Secondary
class DefaultFlushCheckpointsTaskFactory(
    private val checkpointManager: CheckpointManager<*, *>,
) : FlushCheckpointsTaskFactory {
    override fun make(): FlushCheckpointsTask {
        return DefaultFlushCheckpointsTask(checkpointManager)
    }
}
