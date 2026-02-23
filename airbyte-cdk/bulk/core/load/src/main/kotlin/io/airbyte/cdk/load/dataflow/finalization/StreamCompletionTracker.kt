/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.finalization

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

/**
 * Tracks whether we've received stream complete messages for streams in the catalog.
 *
 * "Input complete" means the source has sent DestinationRecordStreamComplete — all records for that
 * stream have been received. This is used by [DestinationLifecycle] to determine which streams
 * should receive the [StreamLoader.onStreamFlushed] callback after the pipeline finishes.
 */
@Singleton
class StreamCompletionTracker(
    catalog: DestinationCatalog,
) {
    private val expectedStreams: Set<DestinationStream.Descriptor> =
        catalog.streams.map { it.mappedDescriptor }.toSet()

    private val inputCompleteStreams: MutableSet<DestinationStream.Descriptor> =
        ConcurrentHashMap.newKeySet()

    /** Called when the source sends DestinationRecordStreamComplete for a stream. */
    fun accept(msg: DestinationRecordStreamComplete) {
        inputCompleteStreams.add(msg.stream.mappedDescriptor)
    }

    /** Returns true if the source has finished sending records for the given stream. */
    fun isInputComplete(descriptor: DestinationStream.Descriptor): Boolean =
        inputCompleteStreams.contains(descriptor)

    fun allStreamsComplete() = inputCompleteStreams.containsAll(expectedStreams)
}
