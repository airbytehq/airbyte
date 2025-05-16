/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.BatchState
import io.airbyte.cdk.load.task.implementor.CloseStreamTask
import io.airbyte.cdk.load.task.implementor.FailStreamTask
import io.airbyte.cdk.load.util.setOnce
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.CompletableDeferred

sealed interface StreamResult

data class StreamProcessingFailed(val streamException: Exception) : StreamResult

data object StreamProcessingSucceeded : StreamResult

@JvmInline value class CheckpointId(val id: Int)

data class CheckpointValue(
    val records: Long,
// TODO: File bytes moved
) {
    operator fun plus(other: CheckpointValue): CheckpointValue {
        return CheckpointValue(records + other.records)
    }
}

/** Manages the state of a single stream. */
class StreamManager(
    val stream: DestinationStream,
) {
    private val streamResult = CompletableDeferred<StreamResult>()

    private val log = KotlinLogging.logger {}

    private val recordCount = AtomicLong(0)

    private val markedEndOfStream = AtomicBoolean(false)
    private val receivedComplete = AtomicBoolean(false)

    private val isClosed = AtomicBoolean(false)

    private val nextCheckpointId = AtomicLong(0L)
    private val lastCheckpointRecordIndex = AtomicLong(0L)
    private val recordsReadPerCheckpoint: ConcurrentHashMap<CheckpointId, CheckpointValue> =
        ConcurrentHashMap()
    data class TaskKey(val name: String, val part: Int)
    private val namedCheckpointCounts:
        ConcurrentHashMap<
            Pair<TaskKey, BatchState>, ConcurrentHashMap<CheckpointId, CheckpointValue>> =
        ConcurrentHashMap()
    private val taskInputCounts = ConcurrentHashMap<TaskKey, Long>()
    private val taskCompletionCounts = ConcurrentHashMap<TaskKey, Long>()

    /**
     * Count incoming record and return the record's *index*. If [markEndOfStream] has been called,
     * this should throw an exception.
     */
    fun incrementReadCount(): Long {
        if (markedEndOfStream.get()) {
            throw IllegalStateException("Stream is closed for reading")
        }

        return recordCount.getAndIncrement()
    }

    fun readCount(): Long {
        return recordCount.get()
    }

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

        return recordCount.get()
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
     * Mark a checkpoint in the stream and return the current index and the number of records since
     * the last one.
     *
     * NOTE: Single-writer. If in the future multiple threads set checkpoints, this method should be
     * synchronized.
     */
    fun markCheckpoint(): Pair<Long, Long> {
        val recordIndex = recordCount.get()
        val count = recordIndex - lastCheckpointRecordIndex.getAndSet(recordIndex)

        val checkpointId = CheckpointId(nextCheckpointId.getAndIncrement().toInt())
        recordsReadPerCheckpoint.merge(checkpointId, CheckpointValue(records = count)) { old, _ ->
            if (old.records > 0) {
                throw IllegalStateException("Checkpoint $old already exists")
            }
            old.copy(records = count)
        }

        return Pair(recordIndex, count)
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

    /**
     * Return a monotonically increasing id of the checkpointed batch of records on which we're
     * working.
     *
     * This will be incremented each time `markCheckpoint` is called.
     */
    fun getCurrentCheckpointId(): CheckpointId {
        return CheckpointId(nextCheckpointId.get().toInt())
    }

    fun incrementCheckpointCounts(
        taskName: String,
        part: Int,
        state: BatchState,
        checkpointCounts: Map<CheckpointId, Long>,
        inputCount: Long
    ) {
        val taskKey = TaskKey(taskName, part)
        check(!taskCompletionCounts.containsKey(taskKey)) {
            """"$taskKey received input after seeing end-of-stream
                    (checkpointCounts=$checkpointCounts, inputCount=$inputCount, sawEosAt=${taskCompletionCounts[taskKey]})
                    This indicates data was processed out of order and future bookkeeping might be corrupt. Failing hard."""
        }
        val idToValue =
            namedCheckpointCounts.getOrPut(TaskKey(taskName, part) to state) { ConcurrentHashMap() }

        checkpointCounts.forEach { (checkpointId, recordCount) ->
            idToValue.merge(checkpointId, CheckpointValue(recordCount)) { old, new -> old + new }
        }

        taskInputCounts.merge(TaskKey(taskName, part), inputCount) { old, new -> old + new }
    }

    fun markTaskEndOfStream(taskName: String, part: Int, finalInputCount: Long) {
        taskCompletionCounts.putIfAbsent(TaskKey(taskName, part), finalInputCount)?.let {
            throw IllegalStateException(
                "End-of-stream reported at $finalInputCount already seen for $taskName[$part] at $it"
            )
        }
    }

    private fun countByStateUpToInclusive(
        checkpointId: CheckpointId,
        state: BatchState
    ): CheckpointValue {
        return namedCheckpointCounts
            .filter { (key, _) -> key.second == state }
            .values
            .fold(CheckpointValue(records = 0)) { totalValue, checkpointIdToValue ->
                totalValue +
                    checkpointIdToValue
                        .filterKeys { it.id <= checkpointId.id }
                        .values
                        .fold(CheckpointValue(records = 0)) { z, x -> z + x }
            }
    }

    /**
     * True if persisted counts for each checkpoint up to and including [checkpointId] match the
     * number of records read for that id.
     */
    fun areRecordsPersistedUntilCheckpoint(checkpointId: CheckpointId): Boolean {
        val counts = recordsReadPerCheckpoint.filter { it.key.id <= checkpointId.id }
        if (counts.size < checkpointId.id + 1) {
            return false
        }

        val readCount = counts.map { it.value.records }.sum()
        val persistedCount = countByStateUpToInclusive(checkpointId, BatchState.PERSISTED).records
        val completedCount = countByStateUpToInclusive(checkpointId, BatchState.COMPLETE).records

        if (persistedCount == readCount) {
            return true
        }

        // Completed implies persisted.
        return completedCount == readCount
    }

    /**
     * True if all records in the stream have been marked as completed AND the stream has been
     * marked as complete.
     */
    fun isBatchProcessingCompleteForCheckpoints(): Boolean {
        if (!markedEndOfStream.get()) {
            return false
        }

        val readCount = recordCount.get()
        if (readCount == 0L) {
            return true
        }

        // Detailed debug logging for completeness checks. It's a little verbose but is only emitted
        // per-batch (every 10-20mb in most cases).
        // TODO: A more user-friendly aggregated version of this on a regular cadence?
        log.info {
            val header =
                "\nStream ${stream.descriptor.namespace}:${stream.descriptor.name}: Records Read: $readCount (done: ${markedEndOfStream.get()})"
            val byPart =
                namedCheckpointCounts.map { (key, value) ->
                    val (taskKey, state) = key
                    val recordCount = value.values.sumOf { it.records }
                    val inputCount = taskInputCounts[taskKey] ?: 0L
                    val isCompleteCount = taskCompletionCounts[taskKey]
                    Triple(taskKey, state, Triple(recordCount, inputCount, isCompleteCount))
                }
            val byTask =
                byPart
                    .groupBy { TaskKey(it.first.name, 999) }
                    .mapValues {
                        it.value.fold(Triple(BatchState.PROCESSED, Pair(0L, 0L), null as Long?)) {
                            z,
                            x ->
                            Triple(
                                x.second,
                                Pair(
                                    z.second.first + x.third.first,
                                    z.second.second + x.third.second
                                ),
                                (z.third?.plus(x.third.third ?: 0L)) ?: x.third.third
                            )
                        }
                    }
                    .map { (taskKey, stateAndCountsAndComplete) ->
                        val (state, counts, isCompleteCount) = stateAndCountsAndComplete
                        Triple(taskKey, state, Triple(counts.first, counts.second, isCompleteCount))
                    }
            val sortedAndFormatted =
                (byPart + byTask)
                    .sortedBy { (taskKey, state, _) -> state.ordinal * 1_000 + taskKey.part }
                    .map { (taskKey, state, countsAndComplete) ->
                        val (recordCount, inputCount, isCompleteCount) = countsAndComplete
                        val partString = if (taskKey.part == 999) "[TOTAL]" else "[${taskKey.part}]"
                        val inputString =
                            if (recordCount == inputCount) "(" else " (inputs: $inputCount, "
                        val completeString =
                            if (isCompleteCount == null) "false"
                            else "true, saw eos at input $isCompleteCount"
                        "${taskKey.name}$partString($state): $recordCount records ${inputString}done: $completeString)"
                    }
            (listOf(header) + sortedAndFormatted).joinToString(separator = "\n")
        }

        val completedCount =
            namedCheckpointCounts
                .filter { (key, _) -> key.second == BatchState.COMPLETE }
                .values
                .flatMap { it.values }
                .sumOf { it.records }

        return completedCount == readCount
    }

    /**
     * Some destinations need to perform expensive post-processing at the end of a sync, but can
     * skip that post-processing if the sync had 0 records. So we should tell the destination
     * whether any records were processed.
     */
    fun hadNonzeroRecords(): Boolean {
        return recordCount.get() > 0
    }
}
