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
import java.util.concurrent.ConcurrentLinkedQueue
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.CompletableDeferred

sealed interface StreamResult

data class StreamProcessingFailed(val streamException: Exception) : StreamResult

data object StreamProcessingSucceeded : StreamResult

@JvmInline value class CheckpointId(val id: Int)

/** Manages the state of a single stream. */
interface StreamManager {
    /**
     * Count incoming record and return the record's *index*. If [markEndOfStream] has been called,
     * this should throw an exception.
     */
    fun incrementReadCount(): Long
    fun readCount(): Long

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

    /**
     * Return a monotonically increasing id of the checkpointed batch of records on which we're
     * working.
     *
     * This will be incremented each time `markCheckpoint` is called.
     */
    fun getNextCheckpointId(): CheckpointId

    /** Update the counts of persisted for a given checkpoint. */
    fun incrementPersistedCount(checkpointId: CheckpointId, count: Long)

    /** Update the counts of completed for a given checkpoint. */
    fun incrementCompletedCount(checkpointId: CheckpointId, count: Long)

    /**
     * True if persisted counts for each checkpoint up to and including [checkpointId] match the
     * number of records read for that id.
     */
    fun areRecordsPersistedUntilCheckpoint(checkpointId: CheckpointId): Boolean

    /**
     * True if all records in the stream have been marked as completed AND the stream has been
     * marked as complete.
     */
    fun isBatchProcessingCompleteForCheckpoints(): Boolean
}

class DefaultStreamManager(
    val stream: DestinationStream,
) : StreamManager {
    private val streamResult = CompletableDeferred<StreamResult>()

    data class CachedRanges(val state: Batch.State, val ranges: RangeSet<Long>)

    private val cachedRangesById = ConcurrentHashMap<String, CachedRanges>()

    private val log = KotlinLogging.logger {}

    private val recordCount = AtomicLong(0)

    private val markedEndOfStream = AtomicBoolean(false)
    private val receivedComplete = AtomicBoolean(false)

    private val rangesState: ConcurrentHashMap<Batch.State, RangeSet<Long>> = ConcurrentHashMap()

    data class CheckpointCounts(
        val recordsRead: Long = 0L,
        val recordsPersisted: AtomicLong = AtomicLong(0L),
        val recordsCompleted: AtomicLong = AtomicLong(0L),
    )
    private val lastCheckpointRecordIndex = AtomicLong(0L)
    private val checkpointCounts: ConcurrentLinkedQueue<CheckpointCounts> = ConcurrentLinkedQueue()

    init {
        Batch.State.entries.forEach { rangesState[it] = TreeRangeSet.create() }
    }

    override fun incrementReadCount(): Long {
        if (markedEndOfStream.get()) {
            throw IllegalStateException("Stream is closed for reading")
        }

        return recordCount.getAndIncrement()
    }

    override fun readCount(): Long {
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
        val recordIndex = recordCount.get()
        val count = recordIndex - lastCheckpointRecordIndex.getAndSet(recordIndex)
        checkpointCounts.add(CheckpointCounts(count))
        return Pair(recordIndex, count)
    }

    override fun <B : Batch> updateBatchState(batch: BatchEnvelope<B>) {
        rangesState[batch.batch.state]
            ?: throw IllegalArgumentException("Invalid batch state: ${batch.batch.state}")

        val stateRangesToAdd = mutableListOf(batch.batch.state to batch.ranges)

        // If the batch is part of a group, update all ranges associated with its groupId
        // to the most advanced state. Otherwise, just use the ranges provided.
        val fromCache =
            batch.batch.groupId?.let { groupId ->
                val cachedRangesMaybe = cachedRangesById[groupId]
                val cachedSet = cachedRangesMaybe?.ranges?.asRanges() ?: emptySet()
                val newRanges = TreeRangeSet.create(cachedSet + batch.ranges.asRanges()).merged()
                val newCachedRanges = CachedRanges(state = batch.batch.state, ranges = newRanges)
                cachedRangesById[groupId] = newCachedRanges
                if (cachedRangesMaybe != null && cachedRangesMaybe.state != batch.batch.state) {
                    stateRangesToAdd.add(batch.batch.state to newRanges)
                    stateRangesToAdd.add(cachedRangesMaybe.state to batch.ranges)
                }
                cachedRangesMaybe
            }

        stateRangesToAdd.forEach { (stateToSet, rangesToUpdate) ->
            when (stateToSet) {
                Batch.State.COMPLETE -> {
                    // A COMPLETED state implies PERSISTED, so also mark PERSISTED.
                    addAndMarge(Batch.State.PERSISTED, rangesToUpdate)
                    addAndMarge(Batch.State.COMPLETE, rangesToUpdate)
                }
                else -> {
                    // For all other states, just mark the state.
                    addAndMarge(stateToSet, rangesToUpdate)
                }
            }
        }

        log.info {
            "Added ${batch.batch.state}->${batch.ranges} (groupId=${batch.batch.groupId}) to ${stream.descriptor.namespace}.${stream.descriptor.name}=>${rangesState[batch.batch.state]}"
        }
        log.debug {
            val groupLineMaybe =
                if (fromCache != null) {
                    "\n                From group cache: ${fromCache.state}->${fromCache.ranges}"
                } else {
                    ""
                }
            val stateRangesJoined =
                stateRangesToAdd.joinToString(",") { "${it.first}->${it.second}" }
            val readRange = TreeRangeSet.create(listOf(Range.closed(0, recordCount.get())))
            """ Added $stateRangesJoined to ${stream.descriptor.namespace}.${stream.descriptor.name}$groupLineMaybe
            READ:      $readRange (complete=${markedEndOfStream.get()})
            PROCESSED: ${rangesState[Batch.State.PROCESSED]}
            STAGED:    ${rangesState[Batch.State.STAGED]}
            PERSISTED: ${rangesState[Batch.State.PERSISTED]}
            COMPLETE:  ${rangesState[Batch.State.COMPLETE]}
        """.trimIndent()
        }
    }

    private fun RangeSet<Long>.merged(): RangeSet<Long> {
        val newRanges = this.asRanges().toMutableSet()
        this.asRanges().forEach { oldRange ->
            newRanges
                .find { newRange ->
                    oldRange.upperEndpoint() + 1 == newRange.lowerEndpoint() ||
                        newRange.upperEndpoint() + 1 == oldRange.lowerEndpoint()
                }
                ?.let { newRange ->
                    newRanges.remove(oldRange)
                    newRanges.remove(newRange)
                    val lower = minOf(oldRange.lowerEndpoint(), newRange.lowerEndpoint())
                    val upper = maxOf(oldRange.upperEndpoint(), newRange.upperEndpoint())
                    newRanges.add(Range.closed(lower, upper))
                }
        }
        return TreeRangeSet.create(newRanges)
    }

    private fun addAndMarge(state: Batch.State, ranges: RangeSet<Long>) {
        rangesState[state] =
            (rangesState[state]?.let {
                    it.addAll(ranges)
                    it
                }
                    ?: ranges)
                .merged()
    }

    /** True if all records in `[0, index)` have reached the given state. */
    private fun isProcessingCompleteForState(index: Long, state: Batch.State): Boolean {
        val completeRanges = rangesState[state]!!

        // Force the ranges to overlap at their endpoints, in order to work around
        // the behavior of `.encloses`, which otherwise would not consider adjacent ranges as
        // contiguous.
        // This ensures that a state message received at eg, index 10 (after messages 0..9 have
        // been received), will pass `{'[0..5]','[6..9]'}.encloses('[0..10)')`.
        val expanded =
            completeRanges.asRanges().map { it.span(Range.singleton(it.upperEndpoint() + 1)) }
        val expandedSet = TreeRangeSet.create(expanded)

        if (index == 0L && recordCount.get() == 0L) {
            return true
        }

        return expandedSet.encloses(Range.closedOpen(0L, index))
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

    override fun getNextCheckpointId(): CheckpointId {
        return CheckpointId(checkpointCounts.size)
    }

    override fun incrementPersistedCount(checkpointId: CheckpointId, count: Long) {
        checkpointCounts.elementAtOrNull(checkpointId.id)?.let {
            val result = it.recordsPersisted.addAndGet(count)
            if (result > it.recordsRead) {
                throw IllegalStateException(
                    "Persisted count $result for $checkpointId exceeds read count ${it.recordsRead}"
                )
            }
        }
            ?: throw IllegalStateException("No checkpoint found for $checkpointId")
    }

    override fun incrementCompletedCount(checkpointId: CheckpointId, count: Long) {
        checkpointCounts.elementAtOrNull(checkpointId.id)?.let {
            val result = it.recordsCompleted.addAndGet(count)
            if (result > it.recordsRead) {
                throw IllegalStateException(
                    "Completed count $result for $checkpointId exceeds read count ${it.recordsRead}"
                )
            }
        }
            ?: throw IllegalStateException("No checkpoint found for $checkpointId")
    }

    override fun areRecordsPersistedUntilCheckpoint(checkpointId: CheckpointId): Boolean {
        val (readCount, persistedCount, completedCount) =
            checkpointCounts.take(checkpointId.id + 1).fold(Triple(0L, 0L, 0L)) {
                acc,
                checkpointCount ->
                Triple(
                    acc.first + checkpointCount.recordsRead,
                    acc.second + checkpointCount.recordsPersisted.get(),
                    acc.third + checkpointCount.recordsCompleted.get(),
                )
            }
        if (persistedCount == readCount) {
            return true
        }
        // Completed implies persisted.
        return completedCount == readCount
    }

    override fun isBatchProcessingCompleteForCheckpoints(): Boolean {
        if (!markedEndOfStream.get()) {
            return false
        }

        val readCount = recordCount.get()
        if (readCount == 0L) {
            return true
        }

        val completedCount = checkpointCounts.sumOf { it.recordsCompleted.get() }
        return completedCount == readCount
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
