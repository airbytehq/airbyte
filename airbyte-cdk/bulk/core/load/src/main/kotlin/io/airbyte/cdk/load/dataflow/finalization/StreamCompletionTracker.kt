/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.finalization

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

/** Tracks whether we've received stream complete messages for all streams in the catalog. */
@Singleton
class StreamCompletionTracker(
    catalog: DestinationCatalog,
) {
    private val expectedStreams: Set<DestinationStream.Descriptor> =
        catalog.streams.map { it.mappedDescriptor }.toSet()

    private val completedStreams: MutableSet<DestinationStream.Descriptor> =
        ConcurrentHashMap.newKeySet()

    fun accept(msg: DestinationRecordStreamComplete) {
        completedStreams.add(msg.stream.mappedDescriptor)
    }

    fun allStreamsComplete() = completedStreams.containsAll(expectedStreams)
}
