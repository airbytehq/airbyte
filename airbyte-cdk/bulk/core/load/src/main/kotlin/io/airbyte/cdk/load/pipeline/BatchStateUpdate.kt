/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import com.google.common.collect.RangeSet
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch

/** Used internally by the CDK to track record ranges to ack. */
sealed interface BatchUpdate {
    val stream: DestinationStream.Descriptor
}

data class BatchStateUpdate(
    override val stream: DestinationStream.Descriptor,
    val indexRange: RangeSet<Long>,
    val state: Batch.State,
) : BatchUpdate

data class BatchEndOfStream(
    override val stream: DestinationStream.Descriptor,
) : BatchUpdate
