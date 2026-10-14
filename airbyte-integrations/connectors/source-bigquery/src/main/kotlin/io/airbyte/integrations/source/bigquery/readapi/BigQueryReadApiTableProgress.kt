/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery.readapi

import io.airbyte.cdk.StreamIdentifier
import jakarta.inject.Singleton
import java.time.Instant
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLongArray

/**
 * Progress of the read streams of one table's session, shared by the partition readers of that
 * table and by the successive partition creation rounds of the READ.
 *
 * Every reader records its row offset after each Arrow batch and marks its read stream complete at
 * the end, so that every checkpoint, whichever reader produces it, describes the whole table.
 */
class BigQueryReadApiTableProgress(
    val session: BigQueryReadSession,
    initial: BigQueryReadApiState? = null,
    snapshotTime: Instant? = null,
    cursorUpperBound: BigQueryReadApiState.CursorBound? = null,
) {
    private val rows = AtomicLongArray(session.readStreams.size)
    private val complete = java.util.concurrent.atomic.AtomicIntegerArray(session.readStreams.size)

    /** The instant the session reads the table as of (incremental initial snapshot only). */
    val snapshotTime: Instant? = snapshotTime ?: initial?.snapshotTimeInstant

    /** The maximum cursor value as of [snapshotTime] (incremental initial snapshot only). */
    val cursorUpperBound: BigQueryReadApiState.CursorBound? =
        cursorUpperBound ?: initial?.cursorUpperBound

    init {
        if (initial != null && initial.session.name == session.name) {
            for ((index, offset) in initial.offsets) {
                index.toIntOrNull()?.let { if (it in indices) rows.set(it, offset) }
            }
            for (index in indices) {
                if (index <= initial.completedThrough || index in initial.complete) {
                    complete.set(index, 1)
                }
            }
        }
    }

    private val indices: IntRange
        get() = session.readStreams.indices

    fun rowsRead(index: Int): Long = rows.get(index)

    fun isComplete(index: Int): Boolean = complete.get(index) == 1

    fun recordRows(index: Int, rowsRead: Long) {
        rows.set(index, rowsRead)
    }

    fun markComplete(index: Int) {
        complete.set(index, 1)
    }

    val isComplete: Boolean
        get() = indices.all { isComplete(it) }

    /** The read streams not complete yet, in index order, each at its current offset. */
    fun remainingWork(): List<BigQueryReadApiState.ReadStreamWork> =
        indices
            .filterNot { isComplete(it) }
            .map { BigQueryReadApiState.ReadStreamWork(it, session.readStreams[it], rows.get(it)) }

    /** A consistent snapshot of the progress as a state value. */
    fun snapshot(): BigQueryReadApiState {
        var completedThrough = -1
        for (index in indices) {
            if (isComplete(index)) completedThrough = index else break
        }
        val completeAbove: List<Int> = indices.filter { it > completedThrough && isComplete(it) }
        val offsets: Map<String, Long> =
            indices
                .filter { it > completedThrough && !isComplete(it) && rows.get(it) > 0L }
                .associate { it.toString() to rows.get(it) }
        return BigQueryReadApiState(
            session = BigQueryReadApiState.of(session),
            completedThrough = completedThrough,
            complete = completeAbove,
            offsets = offsets,
            snapshotTime = snapshotTime?.toString(),
            cursorUpperBound = cursorUpperBound,
        )
    }
}

/** The [BigQueryReadApiTableProgress] of every table being read, for the whole READ. */
@Singleton
class BigQueryReadApiProgressRegistry {
    private val byStream = ConcurrentHashMap<StreamIdentifier, BigQueryReadApiTableProgress>()

    fun get(streamID: StreamIdentifier): BigQueryReadApiTableProgress? = byStream[streamID]

    fun put(streamID: StreamIdentifier, progress: BigQueryReadApiTableProgress) {
        byStream[streamID] = progress
    }

    fun remove(streamID: StreamIdentifier) {
        byStream.remove(streamID)
    }
}
