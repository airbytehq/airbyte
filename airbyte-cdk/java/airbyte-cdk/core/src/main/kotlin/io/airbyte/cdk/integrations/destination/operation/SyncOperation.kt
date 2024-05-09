/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.operation

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.stream.Stream

/** Connector sync operations */
interface SyncOperation {

    /** DestinationFlush function sends per stream with descriptor. */
    fun flushStream(descriptor: StreamDescriptor, stream: Stream<PartialAirbyteMessage>)
    fun finalizeStreams(streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary>)
}
