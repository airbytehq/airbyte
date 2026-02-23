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
 * Tracks whether we've received stream complete messages for all streams in the catalog, and
 * whether individual streams have been fully flushed (input complete + all aggregates drained).
 */
@Singleton
class StreamCompletionTracker(
    catalog: DestinationCatalog,
) {
    private val expectedStreams: Set<DestinationStream.Descriptor> =
        catalog.streams.map { it.mappedDescriptor }.toSet()

    /** Streams whose source has sent DestinationRecordStreamComplete (all records received). */
    private val inputCompleteStreams: MutableSet<DestinationStream.Descriptor> =
        ConcurrentHashMap.newKeySet()

    /**
     * Streams that are fully flushed: input complete AND all aggregates for the stream have been
     * drained and flushed. The [onStreamFullyFlushed] callback has been invoked for these.
     */
    private val fullyFlushedStreams: MutableSet<DestinationStream.Descriptor> =
        ConcurrentHashMap.newKeySet()

    /** Called when the source sends DestinationRecordStreamComplete for a stream. */
    fun accept(msg: DestinationRecordStreamComplete) {
        inputCompleteStreams.add(msg.stream.mappedDescriptor)
    }

    /** Returns true if the source has finished sending records for the given stream. */
    fun isInputComplete(descriptor: DestinationStream.Descriptor): Boolean =
        inputCompleteStreams.contains(descriptor)

    /**
     * Marks a stream as fully flushed (all aggregates drained after input completion). Returns true
     * if this was a new transition (i.e., the stream wasn't already marked as fully flushed).
     */
    fun markFullyFlushed(descriptor: DestinationStream.Descriptor): Boolean =
        fullyFlushedStreams.add(descriptor)

    /** Returns true if the given stream has been fully flushed. */
    fun isFullyFlushed(descriptor: DestinationStream.Descriptor): Boolean =
        fullyFlushedStreams.contains(descriptor)

    fun allStreamsComplete() = inputCompleteStreams.containsAll(expectedStreams)
}
