/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.task.Task

/** Used internally by the CDK to track record ranges to ack. */
sealed interface BatchUpdate {
    val stream: DestinationStream.Descriptor
    val task: Task
}

data class BatchStateUpdate(
    override val stream: DestinationStream.Descriptor,
    val checkpointCounts: Map<CheckpointId, Long>,
    val state: Batch.State,
    override val task: Task,
) : BatchUpdate

data class BatchEndOfStream(
    override val stream: DestinationStream.Descriptor,
    override val task: Task,
) : BatchUpdate
