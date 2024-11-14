/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import com.google.common.collect.Range
import com.google.common.collect.RangeSet
import com.google.common.collect.TreeRangeSet

/**
 * Represents an accumulated batch of records in some stage of processing.
 *
 * Emitted by @[io.airbyte.cdk.write.StreamLoader.processRecords] to describe the batch accumulated.
 * Non-[State.COMPLETE] batches are routed to @[io.airbyte.cdk.write.StreamLoader.processBatch]
 * re-entrantly until completion.
 *
 * The framework will track the association between the Batch and the range of records it
 * represents, by [Batch.State]s. The [State.PERSISTED] state has special meaning: it indicates that
 * the associated ranges have been persisted remotely, and that platform checkpoint messages can be
 * emitted.
 *
 * [State.SPILLED] is used internally to indicate that records have been spooled to disk for
 * processing and should not be used by implementors.
 *
 * When a stream has been read to End-of-stream, and all ranges between 0 and End-of-stream are
 * [State.COMPLETE], then all records are considered to have been processed.
 *
 * The intended usage for implementors is to implement the provided interfaces in case classes that
 * contain the necessary metadata for processing, using them in @
 * [io.airbyte.cdk.write.StreamLoader.processBatch] to route to the appropriate handler(s).
 *
 * For example:
 *
 * ```kotlin
 * sealed class MyBatch: Batch
 * data class MyLocalFile(
 *   override val path: Path,
 *   override val totalSizeBytes: Long
 * ): StagedLocalFile
 * data class MyRemoteObject(
 *   override val key: String
 * ): RemoteObject
 * // etc...
 * ```
 */
interface Batch {
    enum class State {
        LOCAL,
        PERSISTED,
        COMPLETE
    }

    fun isPersisted(): Boolean =
        when (state) {
            State.PERSISTED,
            State.COMPLETE -> true
            else -> false
        }

    val state: State
}

/** Simple batch: use if you need no other metadata for processing. */
data class SimpleBatch(override val state: Batch.State) : Batch

/**
 * Internally-used wrapper for tracking the association between a batch and the range of records it
 * contains.
 */
data class BatchEnvelope<B : Batch>(
    val batch: B,
    val ranges: RangeSet<Long> = TreeRangeSet.create()
) {
    constructor(
        batch: B,
        range: Range<Long>
    ) : this(batch = batch, ranges = TreeRangeSet.create(listOf(range)))

    fun <C : Batch> withBatch(newBatch: C): BatchEnvelope<C> {
        return BatchEnvelope(newBatch, ranges)
    }
}
