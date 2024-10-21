/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.operation

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.stream.Stream

/**
 * Destination Connector sync operations Any initialization required for the connector should be
 * done as part of instantiation/init blocks
 */
interface SyncOperation {

    /**
     * This function is a shim for
     * [io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction] After the
     * method control is returned, it should be assumed that the data is committed to a durable
     * storage and send back any State message acknowledgements.
     */
    fun flushStream(descriptor: StreamDescriptor, stream: Stream<PartialAirbyteMessage>)

    /**
     * Finalize streams which could involve typing deduping or any other housekeeping tasks
     * required.
     */
    fun finalizeStreams(streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary>)
}
