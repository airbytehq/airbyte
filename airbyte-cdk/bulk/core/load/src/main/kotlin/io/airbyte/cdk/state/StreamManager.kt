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
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.CountDownLatch
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/** Manages the state of all streams in the destination. */
interface StreamsManager {
    fun getManager(stream: DestinationStream): StreamManager
    suspend fun awaitAllStreamsComplete()
}

class DefaultStreamsManager(
    private val streamManagers: ConcurrentHashMap<DestinationStream, StreamManager>
) : StreamsManager {
    override fun getManager(stream: DestinationStream): StreamManager {
        return streamManagers[stream] ?: throw IllegalArgumentException("Stream not found: $stream")
    }

    override suspend fun awaitAllStreamsComplete() {
        streamManagers.forEach { (_, manager) -> manager.awaitStreamClosed() }
    }
}

/** Manages the state of a single stream. */
interface StreamManager {
    fun countRecordIn(sizeBytes: Long): Long
    fun markCheckpoint(): Pair<Long, Long>
    fun <B : Batch> updateBatchState(batch: BatchEnvelope<B>)
    fun isBatchProcessingComplete(): Boolean
    fun areRecordsPersistedUntil(index: Long): Boolean

    fun markClosed()
    fun streamIsClosed(): Boolean
    suspend fun awaitStreamClosed()
}

/**
 * Maintains a map of stream -> status metadata, and a map of batch state -> record ranges for which
 * that state has been reached.
 *
 * TODO: Log a detailed report of the stream status on a regular cadence.
 */
class DefaultStreamManager(
    val stream: DestinationStream,
) : StreamManager {
    private val log = KotlinLogging.logger {}

    data class StreamStatus(
        val recordCount: AtomicLong = AtomicLong(0),
        val totalBytes: AtomicLong = AtomicLong(0),
        val enqueuedSize: AtomicLong = AtomicLong(0),
        val lastCheckpoint: AtomicLong = AtomicLong(0L),
        val closedLatch: CountDownLatch = CountDownLatch(1),
    )

    private val streamStatus: StreamStatus = StreamStatus()
    private val rangesState: ConcurrentHashMap<Batch.State, RangeSet<Long>> = ConcurrentHashMap()

    init {
        Batch.State.entries.forEach { rangesState[it] = TreeRangeSet.create() }
    }

    override fun countRecordIn(sizeBytes: Long): Long {
        val index = streamStatus.recordCount.getAndIncrement()
        streamStatus.totalBytes.addAndGet(sizeBytes)
        streamStatus.enqueuedSize.addAndGet(sizeBytes)
        return index
    }

    /**
     * Mark a checkpoint in the stream and return the current index and the number of records since
     * the last one.
     */
    override fun markCheckpoint(): Pair<Long, Long> {
        val index = streamStatus.recordCount.get()
        val lastCheckpoint = streamStatus.lastCheckpoint.getAndSet(index)
        return Pair(index, index - lastCheckpoint)
    }

    /** Record that the given batch's state has been reached for the associated range(s). */
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

    /** True if all records in [0, index] have reached the given state. */
    private fun isProcessingCompleteForState(index: Long, state: Batch.State): Boolean {

        val completeRanges = rangesState[state]!!
        return completeRanges.encloses(Range.closedOpen(0L, index))
    }

    /** True if all records have associated [Batch.State.COMPLETE] batches. */
    override fun isBatchProcessingComplete(): Boolean {
        return isProcessingCompleteForState(streamStatus.recordCount.get(), Batch.State.COMPLETE)
    }

    /**
     * True if all records in [0, index] have at least reached [Batch.State.PERSISTED]. This is
     * implicitly true if they have all reached [Batch.State.COMPLETE].
     */
    override fun areRecordsPersistedUntil(index: Long): Boolean {
        return isProcessingCompleteForState(index, Batch.State.PERSISTED) ||
            isProcessingCompleteForState(index, Batch.State.COMPLETE) // complete => persisted
    }

    override fun markClosed() {
        streamStatus.closedLatch.countDown()
    }

    override fun streamIsClosed(): Boolean {
        return streamStatus.closedLatch.count == 0L
    }

    override suspend fun awaitStreamClosed() {
        withContext(Dispatchers.IO) { streamStatus.closedLatch.await() }
    }
}

@Factory
class StreamsManagerFactory(
    private val catalog: DestinationCatalog,
) {
    @Singleton
    fun make(): StreamsManager {
        val hashMap = ConcurrentHashMap<DestinationStream, StreamManager>()
        catalog.streams.forEach { hashMap[it] = DefaultStreamManager(it) }
        return DefaultStreamsManager(hashMap)
    }
}
