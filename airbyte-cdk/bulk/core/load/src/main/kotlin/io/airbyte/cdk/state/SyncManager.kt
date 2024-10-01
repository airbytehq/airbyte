/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.state

import com.google.common.collect.Range
import com.google.common.collect.RangeSet
import com.google.common.collect.TreeRangeSet
import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.message.Batch
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.channels.Channel

/** Manages the state of all streams in the destination. */
interface SyncManager {
    /** Get the manager for the given stream. Throws an exception if the stream is not found. */
    fun getStreamManager(stream: DestinationStream.Descriptor): StreamManager

    fun registerStartedStreamLoader(streamLoader: StreamLoader)
    suspend fun getOrAwaitStreamLoader(stream: DestinationStream.Descriptor): StreamLoader

    /** Suspend until all streams are closed. */
    suspend fun awaitAllStreamsClosed()
}

class DefaultSyncManager(
    private val streamManagers: ConcurrentHashMap<DestinationStream.Descriptor, StreamManager>
) : SyncManager {
    private val streamLoaders =
        ConcurrentHashMap<DestinationStream.Descriptor, CompletableDeferred<StreamLoader>>()

    override fun getStreamManager(stream: DestinationStream.Descriptor): StreamManager {
        return streamManagers[stream] ?: throw IllegalArgumentException("Stream not found: $stream")
    }

    override fun registerStartedStreamLoader(streamLoader: StreamLoader) {
        streamLoaders
            .getOrPut(streamLoader.stream.descriptor) { CompletableDeferred() }
            .complete(streamLoader)
    }

    override suspend fun getOrAwaitStreamLoader(
        stream: DestinationStream.Descriptor
    ): StreamLoader {
        return streamLoaders.getOrPut(stream) { CompletableDeferred() }.await()
    }

    override suspend fun awaitAllStreamsClosed() {
        streamManagers.forEach { (_, manager) -> manager.awaitStreamClosed() }
    }
}

/** Manages the state of a single stream. */
interface StreamManager {
    /** Count incoming record and return the record's *index*. */
    fun countRecordIn(): Long

    /**
     * Count the end-of-stream. Expect this exactly once. Expect no further `countRecordIn`, and
     * expect that `markClosed` will always occur after this.
     */
    fun countEndOfStream(): Long

    /**
     * Mark a checkpoint in the stream and return the current index and the number of records since
     * the last one.
     *
     * NOTE: Single-writer. If in the future multiple threads set checkpoints, this method should be
     * synchronized.
     */
    fun markCheckpoint(): Pair<Long, Long>

    /** Record that the given batch's state has been reached for the associated range(s). */
    fun <B : Batch> updateBatchState(batch: BatchEnvelope<B>)

    /**
     * True if all are true:
     * * all records have been seen (ie, we've counted an end-of-stream)
     * * a [Batch.State.COMPLETE] batch range has been seen covering every record
     *
     * Does NOT require that the stream be closed.
     */
    fun isBatchProcessingComplete(): Boolean

    /**
     * True if all records in [0, index] have at least reached [Batch.State.PERSISTED]. This is
     * implicitly true if they have all reached [Batch.State.COMPLETE].
     */
    fun areRecordsPersistedUntil(index: Long): Boolean

    /** Mark the stream as closed. This should only be called after all records have been read. */
    fun markClosed()

    /** True if the stream has been marked as closed. */
    fun streamIsClosed(): Boolean

    /** Suspend until the stream is closed. */
    suspend fun awaitStreamClosed()
}

class DefaultStreamManager(
    val stream: DestinationStream,
) : StreamManager {
    private val log = KotlinLogging.logger {}

    private val recordCount = AtomicLong(0)
    private val lastCheckpoint = AtomicLong(0L)
    private val readIsClosed = AtomicBoolean(false)
    private val streamIsClosed = AtomicBoolean(false)
    private val closedLock = Channel<Unit>()

    private val rangesState: ConcurrentHashMap<Batch.State, RangeSet<Long>> = ConcurrentHashMap()

    init {
        Batch.State.entries.forEach { rangesState[it] = TreeRangeSet.create() }
    }

    override fun countRecordIn(): Long {
        if (readIsClosed.get()) {
            throw IllegalStateException("Stream is closed for reading")
        }

        return recordCount.getAndIncrement()
    }

    override fun countEndOfStream(): Long {
        if (readIsClosed.getAndSet(true)) {
            throw IllegalStateException("Stream is closed for reading")
        }

        return recordCount.get()
    }

    override fun markCheckpoint(): Pair<Long, Long> {
        val index = recordCount.get()
        val lastCheckpoint = lastCheckpoint.getAndSet(index)
        return Pair(index, index - lastCheckpoint)
    }

    override fun <B : Batch> updateBatchState(batch: BatchEnvelope<B>) {
        val stateRanges =
            rangesState[batch.batch.state]
                ?: throw IllegalArgumentException("Invalid batch state: ${batch.batch.state}")

        // Force the ranges to overlap at their endpoints, in order to work around
        // the behavior of `.encloses`, which otherwise would not consider adjacent ranges as
        // contiguous.
        // This ensures that a state message received at eg, index 10 (after messages 0..9 have
        // been received), will pass `{'[0..5]','[6..9]'}.encloses('[0..10)')`.
        val expanded =
            batch.ranges.asRanges().map { it.span(Range.singleton(it.upperEndpoint() + 1)) }

        stateRanges.addAll(expanded)
        log.info { "Updated ranges for $stream[${batch.batch.state}]: $stateRanges" }
    }

    /** True if all records in `[0, index)` have reached the given state. */
    private fun isProcessingCompleteForState(index: Long, state: Batch.State): Boolean {
        val completeRanges = rangesState[state]!!
        return completeRanges.encloses(Range.closedOpen(0L, index))
    }

    override fun isBatchProcessingComplete(): Boolean {
        /* If the stream hasn't been fully read, it can't be done. */
        if (!readIsClosed.get()) {
            return false
        }

        return isProcessingCompleteForState(recordCount.get(), Batch.State.COMPLETE)
    }

    /** TODO: Handle conflating PERSISTED w/ COMPLETE upstream, to allow for overlap? */
    override fun areRecordsPersistedUntil(index: Long): Boolean {
        return isProcessingCompleteForState(index, Batch.State.PERSISTED) ||
            isProcessingCompleteForState(index, Batch.State.COMPLETE) // complete => persisted
    }

    override fun markClosed() {
        if (!readIsClosed.get()) {
            throw IllegalStateException("Stream must be fully read before it can be closed")
        }

        if (streamIsClosed.compareAndSet(false, true)) {
            closedLock.trySend(Unit)
        }
    }

    override fun streamIsClosed(): Boolean {
        return streamIsClosed.get()
    }

    override suspend fun awaitStreamClosed() {
        if (!streamIsClosed.get()) {
            closedLock.receive()
        }
    }
}

@Factory
class SyncManagerFactory(
    private val catalog: DestinationCatalog,
) {
    @Singleton
    @Secondary
    fun make(): SyncManager {
        val hashMap = ConcurrentHashMap<DestinationStream.Descriptor, StreamManager>()
        catalog.streams.forEach { hashMap[it.descriptor] = DefaultStreamManager(it) }
        return DefaultSyncManager(hashMap)
    }
}
