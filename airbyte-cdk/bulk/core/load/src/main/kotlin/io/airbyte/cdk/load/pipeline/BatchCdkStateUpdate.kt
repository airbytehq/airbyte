/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.BatchCdkState
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.CheckpointValue

/** Used internally by the CDK to track record ranges to ack. */
sealed interface BatchUpdate {
    val stream: DestinationStream.Descriptor
    val taskName: String
    val part: Int
}

data class BatchCdkStateUpdate(
    override val stream: DestinationStream.Descriptor,
    val checkpointCounts: Map<CheckpointId, CheckpointValue>,
    val cdkState: BatchCdkState,
    override val taskName: String,
    override val part: Int,
    val inputCount: Long = 0L
) : BatchUpdate

data class BatchEndOfStream(
    override val stream: DestinationStream.Descriptor,
    override val taskName: String,
    override val part: Int,
    val totalInputCount: Long
) : BatchUpdate
