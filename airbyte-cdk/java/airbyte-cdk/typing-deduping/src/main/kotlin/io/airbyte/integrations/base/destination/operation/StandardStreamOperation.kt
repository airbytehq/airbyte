/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.operation

import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import java.util.stream.Stream

/**
 * This is a pass through stream operation which hands off the [Stream] of messages to the
 * [StorageOperation.writeToStage]
 */
class StandardStreamOperation<DestinationState : MinimumDestinationState>(
    private val storageOperation: StorageOperation<Stream<PartialAirbyteMessage>>,
    destinationInitialStatus: DestinationInitialStatus<DestinationState>,
    disableTypeDedupe: Boolean = false
) :
    AbstractStreamOperation<DestinationState, Stream<PartialAirbyteMessage>>(
        storageOperation,
        destinationInitialStatus,
        disableTypeDedupe
    ) {
    override fun writeRecords(streamConfig: StreamConfig, stream: Stream<PartialAirbyteMessage>) {
        storageOperation.writeToStage(streamConfig, stream)
    }
}
