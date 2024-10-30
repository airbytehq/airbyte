/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import com.google.common.collect.Range
import com.google.common.collect.RangeSet
import com.google.common.collect.TreeRangeSet
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.CompletableDeferred

sealed interface StreamResult

sealed interface StreamIncompleteResult : StreamResult

data class StreamFailed(val streamException: Exception) : StreamIncompleteResult

data class StreamKilled(val syncException: Exception) : StreamIncompleteResult

data object StreamSucceeded : StreamResult

/** Manages the state of a single stream. */
interface StreamManager {
    /**
     * Count incoming record and return the record's *index*. If [markEndOfStream] has been called,
     * this should throw an exception.
     */
    fun countRecordIn(): Long
    fun recordCount(): Long

    /**
     * Mark the end-of-stream and return the record count. Expect this exactly once. Expect no
     * further `countRecordIn`, and expect that [markSucceeded] or [markFailed] or [markKilled] will
     * alway occur after this.
     */
    fun markEndOfStream(): Long
    fun endOfStreamRead(): Boolean

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
    fun markSucceeded()

    /**
     * Mark that the stream was killed due to failure elsewhere. Returns false if task was already
     * complete.
     */
    fun markKilled(causedBy: Exception): Boolean

    /** Mark that the stream itself failed. Return false if task was already complete */
    fun markFailed(causedBy: Exception): Boolean

    /** Suspend until the stream completes, returning the result. */
    suspend fun awaitStreamResult(): StreamResult

    /** True if the stream has not yet been marked successful, failed, or killed. */
    fun isActive(): Boolean
}

class DefaultStreamManager(
    val stream: DestinationStream,
) : StreamManager {
    private val streamResult = CompletableDeferred<StreamResult>()

    private val log = KotlinLogging.logger {}

    private val recordCount = AtomicLong(0)
    private val lastCheckpoint = AtomicLong(0L)

    private val markedEndOfStream = AtomicBoolean(false)

    private val rangesState: ConcurrentHashMap<Batch.State, RangeSet<Long>> = ConcurrentHashMap()

    init {
        Batch.State.entries.forEach { rangesState[it] = TreeRangeSet.create() }
    }

    override fun countRecordIn(): Long {
        if (markedEndOfStream.get()) {
            throw IllegalStateException("Stream is closed for reading")
        }

        return recordCount.getAndIncrement()
    }

    override fun recordCount(): Long {
        return recordCount.get()
    }

    override fun markEndOfStream(): Long {
        if (markedEndOfStream.getAndSet(true)) {
            throw IllegalStateException("Stream is closed for reading")
        }

        return recordCount.get()
    }

    override fun endOfStreamRead(): Boolean {
        return markedEndOfStream.get()
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
        log.info { "Updated ranges for ${stream.descriptor}[${batch.batch.state}]: $stateRanges" }
    }

    /** True if all records in `[0, index)` have reached the given state. */
    private fun isProcessingCompleteForState(index: Long, state: Batch.State): Boolean {
        val completeRanges = rangesState[state]!!

        return completeRanges.encloses(Range.closedOpen(0L, index))
    }

    override fun isBatchProcessingComplete(): Boolean {
        /* If the stream hasn't been fully read, it can't be done. */
        if (!markedEndOfStream.get()) {
            return false
        }

        return isProcessingCompleteForState(recordCount.get(), Batch.State.COMPLETE)
    }

    /** TODO: Handle conflating PERSISTED w/ COMPLETE upstream, to allow for overlap? */
    override fun areRecordsPersistedUntil(index: Long): Boolean {
        return isProcessingCompleteForState(index, Batch.State.PERSISTED) ||
            isProcessingCompleteForState(index, Batch.State.COMPLETE) // complete => persisted
    }

    override fun markSucceeded() {
        if (!markedEndOfStream.get()) {
            throw IllegalStateException("Stream is not closed for reading")
        }
        streamResult.complete(StreamSucceeded)
    }

    override fun markKilled(causedBy: Exception): Boolean {
        return streamResult.complete(StreamKilled(causedBy))
    }

    override fun markFailed(causedBy: Exception): Boolean {
        return streamResult.complete(StreamFailed(causedBy))
    }

    override suspend fun awaitStreamResult(): StreamResult {
        return streamResult.await()
    }

    override fun isActive(): Boolean {
        return streamResult.isActive
    }
}

interface StreamManagerFactory {
    fun create(stream: DestinationStream): StreamManager
}

@Singleton
@Secondary
class DefaultStreamManagerFactory : StreamManagerFactory {
    override fun create(stream: DestinationStream): StreamManager {
        return DefaultStreamManager(stream)
    }
}
