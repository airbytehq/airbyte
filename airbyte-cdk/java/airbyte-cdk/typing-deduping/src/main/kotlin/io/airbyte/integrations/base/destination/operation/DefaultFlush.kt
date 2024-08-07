/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.operation

import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.operation.SyncOperation
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.stream.Stream

class DefaultFlush(
    override val optimalBatchSizeBytes: Long,
    private val syncOperation: SyncOperation
) : DestinationFlushFunction {
    override fun flush(streamDescriptor: StreamDescriptor, stream: Stream<PartialAirbyteMessage>) {
        syncOperation.flushStream(streamDescriptor, stream)
    }
}
