/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.BatchState
import io.airbyte.cdk.load.task.implementor.CloseStreamTask
import io.airbyte.cdk.load.task.implementor.FailStreamTask
import io.airbyte.cdk.load.util.setOnce
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.math.max
import kotlinx.coroutines.CompletableDeferred

sealed interface StreamResult

data class StreamProcessingFailed(val streamException: Exception) : StreamResult

data object StreamProcessingSucceeded : StreamResult

/**
 * For tracking counts against checkpoints of records read and persisted. Currently it only tracks
 * row count, but could be extended to track bytes moved if needed.
 */
data class CheckpointValue(
    val records: Long,
    val serializedBytes: Long,
    val rejectedRecords: Long = 0, // TODO there should not be a default here
) {
    operator fun plus(other: CheckpointValue): CheckpointValue {
        return CheckpointValue(
            records = records + other.records,
            serializedBytes = serializedBytes + other.serializedBytes,
            rejectedRecords = rejectedRecords + other.rejectedRecords,
        )
    }

    override fun equals(other: Any?): Boolean {
        if (other != null && other is CheckpointValue) {
            return this.records == other.records &&
                this.serializedBytes == other.serializedBytes &&
                this.rejectedRecords == other.rejectedRecords
        }
        return false
    }
}

/** Manages the state of a single stream. */
class StreamManager(
    val stream: DestinationStream,
) {
    private val streamResult = CompletableDeferred<StreamResult>()
    private val markedEndOfStream = AtomicBoolean(false)
    private val receivedComplete = AtomicBoolean(false)
    private val isClosed = AtomicBoolean(false)

    private val recordsReadPerCheckpoint: ConcurrentHashMap<CheckpointId, Long> =
        ConcurrentHashMap()
    private val bytesPerCheckpoint: ConcurrentHashMap<CheckpointId, Long> = ConcurrentHashMap()
    private val checkpointCountsByState:
        ConcurrentHashMap<BatchState, ConcurrentHashMap<CheckpointId, CheckpointValue>> =
        ConcurrentHashMap()

    /**
     * Count incoming record and return the record's *index*. If [markEndOfStream] has been called,
     * this should throw an exception.
     */
    fun incrementReadCount(checkpointId: CheckpointId): Long {
        if (markedEndOfStream.get()) error("Stream is closed for reading")
        return recordsReadPerCheckpoint.merge(checkpointId, 1L, Long::plus)!!
    }

    fun incrementByteCount(bytes: Long, checkpointId: CheckpointId): Long {
        if (markedEndOfStream.get()) error("Stream is closed for reading")
        return bytesPerCheckpoint.merge(checkpointId, bytes, Long::plus)!!
    }

    fun readCount(): Long = recordsReadPerCheckpoint.values.sumOf { it }
    fun byteCount(): Long = bytesPerCheckpoint.values.sumOf { it }

    /**
     * Mark the end-of-stream, set the end of stream variant (complete or incomplete) and return the
     * record count. Expect this exactly once. Expect no further `countRecordIn`, and expect that
     * [markProcessingSucceeded] will always occur after this, while [markProcessingFailed] can
     * occur before or after.
     */
    fun markEndOfStream(receivedStreamCompleteMessage: Boolean): Long {
        if (markedEndOfStream.getAndSet(true)) {
            throw IllegalStateException("Stream is closed for reading")
        }
        receivedComplete.getAndSet(receivedStreamCompleteMessage)

        return readCount()
    }

    fun endOfStreamRead(): Boolean {
        return markedEndOfStream.get()
    }

    /** Whether we received a stream complete message for the managed stream. */
    fun receivedStreamComplete(): Boolean {
        return receivedComplete.get()
    }

    /**
     * Mark this stream manager as having initiated a terminal task (i.e. [CloseStreamTask] or
     * [FailStreamTask]).
     *
     * @return `true` if this stream manager was not already terminating; `false` if another thread
     * has already invoked `setClosed` on this stream manager
     */
    fun setClosed(): Boolean {
        return isClosed.setOnce()
    }

    /**
     * Indicates destination processing of the stream succeeded, regardless of complete/incomplete
     * status. This should only be called after all records and end of stream messages have been
     * read.
     */
    fun markProcessingSucceeded() {
        if (!markedEndOfStream.get()) {
            throw IllegalStateException("Stream is not closed for reading")
        }
        streamResult.complete(StreamProcessingSucceeded)
    }

    /**
     * Indicates destination processing of the stream failed. Returns false if task was already
     * complete
     */
    fun markProcessingFailed(causedBy: Exception): Boolean {
        return streamResult.complete(StreamProcessingFailed(causedBy))
    }

    /** Suspend until the stream completes, returning the result. */
    suspend fun awaitStreamResult(): StreamResult {
        return streamResult.await()
    }

    /** True if the stream processing has not yet been marked as successful or failed. */
    fun isActive(): Boolean {
        return streamResult.isActive
    }

    fun incrementCheckpointCounts(
        state: BatchState,
        checkpointCounts: Map<CheckpointId, CheckpointValue>,
    ) {
        val idToValue = checkpointCountsByState.getOrPut(state) { ConcurrentHashMap() }

        checkpointCounts.forEach { (checkpointId, count) ->
            idToValue.merge(checkpointId, count) { old, new -> old.plus(new) }
        }
    }

    private fun countByStateForCheckpoint(
        checkpointId: CheckpointId,
        state: BatchState
    ): CheckpointValue {
        val countsForState = checkpointCountsByState.filter { (it.key == state) }.values
        val recordCount = countsForState.sumOf { it[checkpointId]?.records ?: 0L }
        val serializedBytes = countsForState.sumOf { it[checkpointId]?.serializedBytes ?: 0L }
        val rejectedRecords = countsForState.sumOf { it[checkpointId]?.rejectedRecords ?: 0L }
        return CheckpointValue(
            records = recordCount,
            serializedBytes = serializedBytes,
            rejectedRecords = rejectedRecords,
        )
    }

    fun committedCount(checkpointId: CheckpointId): CheckpointValue {
        val persistedCount = countByStateForCheckpoint(checkpointId, BatchState.PERSISTED)
        val completedCount = countByStateForCheckpoint(checkpointId, BatchState.COMPLETE)

        val records = maxOf(persistedCount.records, completedCount.records)
        val bytes = maxOf(persistedCount.serializedBytes, completedCount.serializedBytes)
        val rejectedRecords = maxOf(persistedCount.rejectedRecords, completedCount.rejectedRecords)

        val checkpointValue =
            CheckpointValue(
                records = records,
                serializedBytes = bytes,
                rejectedRecords = rejectedRecords,
            )
        return checkpointValue
    }

    /**
     * True if persisted counts associated with the index [checkpointId] are equal to the number of
     * records read.
     */
    fun areRecordsPersistedForCheckpoint(checkpointId: CheckpointId): Boolean {
        val readCount = recordsReadPerCheckpoint[checkpointId] ?: 0L

        val persistedRecordCount = persistedRecordCountForCheckpoint(checkpointId)
        val persisted = persistedRecordCount == readCount
        return persisted
    }

    /**
     * True if all records in the stream have been marked as completed AND the stream has been
     * marked as complete.
     */
    fun isBatchProcessingCompleteForCheckpoints(): Boolean {
        if (!markedEndOfStream.get()) {
            return false
        }

        val readCount = readCount()
        if (readCount == 0L) {
            return true
        }

        val completedCount =
            checkpointCountsByState
                .filter { (state, _) -> state == BatchState.COMPLETE }
                .values
                .flatMap { it.values }
                // Make sure to consider rejected records as well for completion
                .sumOf { it.records + it.rejectedRecords }

        return completedCount == readCount
    }

    /**
     * Some destinations need to perform expensive post-processing at the end of a sync, but can
     * skip that post-processing if the sync had 0 records. So we should tell the destination
     * whether any records were processed.
     */
    fun hadNonzeroRecords(): Boolean {
        return readCount() > 0
    }

    fun persistedRecordCountForCheckpoint(checkpointId: CheckpointId): Long {
        val persistedCount =
            checkpointCountsByState[BatchState.PERSISTED]?.get(checkpointId)?.let {
                it.records + it.rejectedRecords
            }
                ?: 0L
        val completeCount =
            checkpointCountsByState[BatchState.COMPLETE]?.get(checkpointId)?.let {
                it.records + it.rejectedRecords
            }
                ?: 0L
        return max(persistedCount, completeCount)
    }

    fun readCountForCheckpoint(checkpointId: CheckpointId): Long? {
        return recordsReadPerCheckpoint[checkpointId]
    }
}
