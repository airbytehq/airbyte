/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.operation

import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.operation.SyncOperation
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.stream.Stream

private val LOGGER = KotlinLogging.logger {}

class DefaultFlush(
    override val optimalBatchSizeBytes: Long,
    private val syncOperation: SyncOperation
) : DestinationFlushFunction {
    override fun flush(streamDescriptor: StreamDescriptor, stream: Stream<PartialAirbyteMessage>) {
        LOGGER.info { "SGX syncOperation.class=${syncOperation.javaClass}" }
        syncOperation.flushStream(streamDescriptor, stream)
    }
}
