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

data class StreamProcessingFailed(val streamException: Exception) : StreamResult

data object StreamProcessingSucceeded : StreamResult

/** Manages the state of a single stream. */
interface StreamManager {
    /**
     * Count incoming record and return the record's *index*. If [markEndOfStream] has been called,
     * this should throw an exception.
     */
    fun countRecordIn(): Long
    fun recordCount(): Long

    /**
     * Mark the end-of-stream, set the end of stream variant (complete or incomplete) and return the
     * record count. Expect this exactly once. Expect no further `countRecordIn`, and expect that
     * [markProcessingSucceeded] will always occur after this, while [markProcessingFailed] can
     * occur before or after.
     */
    fun markEndOfStream(receivedStreamCompleteMessage: Boolean): Long
    fun endOfStreamRead(): Boolean

    /** Whether we received a stream complete message for the managed stream. */
    fun isComplete(): Boolean

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

    /**
     * Indicates destination processing of the stream succeeded, regardless of complete/incomplete
     * status. This should only be called after all records and end of stream messages have been
     * read.
     */
    fun markProcessingSucceeded()

    /**
     * Indicates destination processing of the stream failed. Returns false if task was already
     * complete
     */
    fun markProcessingFailed(causedBy: Exception): Boolean

    /** Suspend until the stream completes, returning the result. */
    suspend fun awaitStreamResult(): StreamResult

    /** True if the stream processing has not yet been marked as successful or failed. */
    fun isActive(): Boolean
}

class DefaultStreamManager(
    val stream: DestinationStream,
) : StreamManager {
    private val streamResult = CompletableDeferred<StreamResult>()

    data class CachedRanges(val state: Batch.State, val ranges: RangeSet<Long>)
    private val cachedRangesById = ConcurrentHashMap<String, CachedRanges>()

    private val log = KotlinLogging.logger {}

    private val recordCount = AtomicLong(0)
    private val lastCheckpoint = AtomicLong(0L)

    private val markedEndOfStream = AtomicBoolean(false)
    private val receivedComplete = AtomicBoolean(false)

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

    override fun markEndOfStream(receivedStreamCompleteMessage: Boolean): Long {
        if (markedEndOfStream.getAndSet(true)) {
            throw IllegalStateException("Stream is closed for reading")
        }
        receivedComplete.getAndSet(receivedStreamCompleteMessage)

        return recordCount.get()
    }

    override fun endOfStreamRead(): Boolean {
        return markedEndOfStream.get()
    }

    override fun isComplete(): Boolean {
        return receivedComplete.get()
    }

    override fun markCheckpoint(): Pair<Long, Long> {
        val index = recordCount.get()
        val lastCheckpoint = lastCheckpoint.getAndSet(index)
        return Pair(index, index - lastCheckpoint)
    }

    override fun <B : Batch> updateBatchState(batch: BatchEnvelope<B>) {

        rangesState[batch.batch.state]
            ?: throw IllegalArgumentException("Invalid batch state: ${batch.batch.state}")

        // If the batch is part of a group, update all ranges associated with its groupId
        // to the most advanced state. Otherwise, just use the ranges provided.
        val cachedRangesMaybe = batch.batch.groupId?.let { cachedRangesById[batch.batch.groupId] }

        log.info {
            "Updating state for stream ${stream.descriptor} with batch $batch using cached ranges $cachedRangesMaybe"
        }

        val stateToSet =
            cachedRangesMaybe?.state?.let { maxOf(it, batch.batch.state) } ?: batch.batch.state
        val rangesToUpdate = TreeRangeSet.create(batch.ranges)
        cachedRangesMaybe?.ranges?.also { rangesToUpdate.addAll(it) }

        log.info { "Marking ranges for stream ${stream.descriptor} $rangesToUpdate as $stateToSet" }

        // Force the ranges to overlap at their endpoints, in order to work around
        // the behavior of `.encloses`, which otherwise would not consider adjacent ranges as
        // contiguous.
        // This ensures that a state message received at eg, index 10 (after messages 0..9 have
        // been received), will pass `{'[0..5]','[6..9]'}.encloses('[0..10)')`.
        val expanded =
            rangesToUpdate.asRanges().map { it.span(Range.singleton(it.upperEndpoint() + 1)) }

        when (stateToSet) {
            Batch.State.PERSISTED -> {
                rangesState[Batch.State.PERSISTED]?.addAll(expanded)
            }
            Batch.State.COMPLETE -> {
                // A COMPLETED state implies PERSISTED, so also mark PERSISTED.
                rangesState[Batch.State.PERSISTED]?.addAll(expanded)
                rangesState[Batch.State.COMPLETE]?.addAll(expanded)
            }
            else -> Unit
        }

        log.info {
            "Updated ranges for ${stream.descriptor}[${batch.batch.state}]: $expanded. PERSISTED is also updated on COMPLETE."
        }

        batch.batch.groupId?.also {
            cachedRangesById[it] = CachedRanges(stateToSet, rangesToUpdate)
        }
    }

    /** True if all records in `[0, index)` have reached the given state. */
    private fun isProcessingCompleteForState(index: Long, state: Batch.State): Boolean {
        val completeRanges = rangesState[state]!!

        if (index == 0L && recordCount.get() == 0L) {
            return true
        }

        return completeRanges.encloses(Range.closedOpen(0L, index))
    }

    override fun isBatchProcessingComplete(): Boolean {
        /* If the stream hasn't been fully read, it can't be done. */
        if (!markedEndOfStream.get()) {
            return false
        }

        /* A closed empty stream is always complete. */
        if (recordCount.get() == 0L) {
            return true
        }

        return isProcessingCompleteForState(recordCount.get(), Batch.State.COMPLETE)
    }

    override fun areRecordsPersistedUntil(index: Long): Boolean {
        return isProcessingCompleteForState(index, Batch.State.PERSISTED)
    }

    override fun markProcessingSucceeded() {
        if (!markedEndOfStream.get()) {
            throw IllegalStateException("Stream is not closed for reading")
        }
        streamResult.complete(StreamProcessingSucceeded)
    }

    override fun markProcessingFailed(causedBy: Exception): Boolean {
        return streamResult.complete(StreamProcessingFailed(causedBy))
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
