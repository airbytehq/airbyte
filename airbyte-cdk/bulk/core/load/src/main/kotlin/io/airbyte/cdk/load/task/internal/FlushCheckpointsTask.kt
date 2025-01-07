/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.task.InternalScope
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface FlushCheckpointsTask : InternalScope

class DefaultFlushCheckpointsTask(
    private val checkpointManager: CheckpointManager<*, *>,
) : FlushCheckpointsTask {
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
