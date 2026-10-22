/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.Stream
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicInteger
import software.amazon.awssdk.services.dynamodb.model.AttributeValue

private val log = KotlinLogging.logger {}

/**
 * Progress of the scan of one table in this READ, shared by the partition readers of its segments.
 *
 * DynamoDB assigns every item to one of [totalSegments] segments by hashing its partition key, so
 * the segments are disjoint, cover the table, and cost nothing to compute; each has its own
 * `LastEvaluatedKey`, valid only for this segment count. The registry is seeded from the saved
 * state on the first round and is authoritative for the rest of the READ: every checkpoint is a
 * [snapshot] of the whole table, so every emitted state is a valid resume point (a key that is a
 * page behind only causes a re-read, never a gap).
 */
class DynamoDbTableScan(
    val stream: Stream,
    val totalSegments: Int,
    saved: List<DynamoDbStreamStateValue.SegmentProgress>?,
) {
    private class Segment(val index: Int) {
        var exclusiveStartKey: Map<String, AttributeValue>? = null
        var complete: Boolean = false
        var maxCursor: String? = null
        var maxCursorRecordCount: Long = 0L
    }

    /** Running maximum of one segment's cursor, as saved or observed so far. */
    data class SegmentCursor(val max: String?, val recordCount: Long)

    private val segments: List<Segment> = List(totalSegments) { Segment(it) }

    /** Readers of the current round that have started and not stopped yet. */
    private val runningReaders = AtomicInteger(0)

    /**
     * Whether the state the CDK applied last (the checkpoint of the last partition of the last
     * round) said the table was complete. Checkpoints are applied in partition order, so when the
     * last partition's snapshot predates the completion of another segment, the planner adds one
     * more partition that emits nothing but the terminal state.
     */
    @Volatile var terminalStateApplied: Boolean = false

    init {
        for (progress: DynamoDbStreamStateValue.SegmentProgress in saved.orEmpty()) {
            val segment: Segment = segments[progress.segment]
            segment.exclusiveStartKey =
                progress.exclusiveStartKey?.let(DynamoDbJson::itemFromDynamoDbJson)
            segment.complete = progress.complete == true
            segment.maxCursor = progress.maxCursor
            segment.maxCursorRecordCount = progress.maxCursorRecordCount ?: 0L
        }
    }

    @Synchronized fun isComplete(): Boolean = segments.all { it.complete }

    @Synchronized
    fun incompleteSegments(): List<Int> = segments.filterNot { it.complete }.map { it.index }

    @Synchronized
    fun startKey(segment: Int): Map<String, AttributeValue>? = segments[segment].exclusiveStartKey

    @Synchronized
    fun cursor(segment: Int): SegmentCursor =
        SegmentCursor(segments[segment].maxCursor, segments[segment].maxCursorRecordCount)

    /** A page of [segment] was fully emitted; [lastEvaluatedKey] is where the next one starts. */
    @Synchronized
    fun recordPage(
        segment: Int,
        lastEvaluatedKey: Map<String, AttributeValue>,
        cursor: SegmentCursor?,
    ) {
        val s: Segment = segments[segment]
        s.exclusiveStartKey = lastEvaluatedKey
        cursor?.let {
            s.maxCursor = it.max
            s.maxCursorRecordCount = it.recordCount
        }
    }

    /** [segment] was scanned to its end. */
    @Synchronized
    fun recordCompletion(segment: Int, cursor: SegmentCursor?) {
        val s: Segment = segments[segment]
        s.exclusiveStartKey = null
        s.complete = true
        cursor?.let {
            s.maxCursor = it.max
            s.maxCursorRecordCount = it.recordCount
        }
    }

    fun readerStarted() {
        runningReaders.incrementAndGet()
    }

    fun readerStopped() {
        runningReaders.decrementAndGet()
    }

    fun runningReaders(): Int = runningReaders.get()

    /** Called by the planner at the start of a round; nothing should be running then. */
    fun beginRound() {
        val stale: Int = runningReaders.getAndSet(0)
        if (stale != 0) {
            log.warn { "Table '${stream.name}': $stale reader(s) still counted as running." }
        }
    }

    /** The current state of the table's scan and whether it is the terminal one. */
    @Synchronized
    fun currentState(cursor: DynamoDbCursor?): Pair<OpaqueStateValue, Boolean> {
        val complete: Boolean = segments.all { it.complete }
        val state: DynamoDbStreamStateValue =
            when {
                cursor == null ->
                    if (complete) DynamoDbStreamStateValue.FULL_REFRESH_COMPLETE
                    else DynamoDbStreamStateValue(scan = scanProgress(withCursor = false))
                complete -> {
                    // Legacy DbStreamState shape: the new cursor is the highest value seen in any
                    // segment (or the saved one, when nothing newer was found).
                    val merged: SegmentCursor =
                        cursor.merge(
                            segments.map { SegmentCursor(it.maxCursor, it.maxCursorRecordCount) }
                        )
                    DynamoDbStreamStateValue(
                        cursorField = listOf(cursor.field),
                        cursor = merged.max,
                        cursorRecordCount = merged.recordCount.takeIf { it > 0L },
                    )
                }
                else ->
                    // Still filtering on the saved cursor; the running maxima travel along.
                    DynamoDbStreamStateValue(
                        cursorField = listOf(cursor.field),
                        cursor = cursor.lowerBound,
                        cursorRecordCount = cursor.lowerBoundRecordCount.takeIf { it > 0L },
                        scan = scanProgress(withCursor = true),
                    )
            }
        return state.toOpaqueStateValue() to complete
    }

    private fun scanProgress(withCursor: Boolean): DynamoDbStreamStateValue.ScanProgress =
        DynamoDbStreamStateValue.ScanProgress(
            totalSegments = totalSegments,
            segments =
                segments.map { s: Segment ->
                    val key: ObjectNode? =
                        s.exclusiveStartKey?.let(DynamoDbJson::itemToDynamoDbJson)
                    DynamoDbStreamStateValue.SegmentProgress(
                        segment = s.index,
                        exclusiveStartKey = key,
                        complete = true.takeIf { s.complete },
                        maxCursor = s.maxCursor.takeIf { withCursor },
                        maxCursorRecordCount =
                            s.maxCursorRecordCount.takeIf { withCursor && s.maxCursor != null },
                    )
                },
        )

    companion object {
        /**
         * How many segments to scan a table of [tableSizeBytes] with: one per [targetBytes], at
         * least 1 and at most [maxSegments]. Sized from `DescribeTable`, which costs nothing. AWS
         * refreshes `TableSizeBytes` only about every six hours, so a table loaded since then (or
         * an empty one) is reported at 0 bytes: such a table gets [unknownSizeSegments] segments
         * (the connector passes its concurrency), which costs one empty `Scan` request per segment
         * when the table really is empty and keeps a freshly loaded large table parallel.
         */
        fun segmentCount(
            tableSizeBytes: Long,
            targetBytes: Long,
            maxSegments: Int,
            unknownSizeSegments: Int = 1,
        ): Int {
            require(targetBytes > 0) { "segment target bytes must be positive, got $targetBytes" }
            require(maxSegments > 0) { "max segments must be positive, got $maxSegments" }
            if (tableSizeBytes <= 0L) return unknownSizeSegments.coerceIn(1, maxSegments)
            val wanted: Long = (tableSizeBytes + targetBytes - 1) / targetBytes
            return wanted.coerceIn(1L, maxSegments.toLong()).toInt()
        }
    }
}
