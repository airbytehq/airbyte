/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import com.google.common.collect.Range
import com.google.common.collect.RangeSet
import com.google.common.collect.TreeRangeSet
import io.airbyte.cdk.load.command.DestinationStream

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
 * [State.STAGED] is used internally to indicate that records have been spooled to disk for
 * processing and should not be used by implementors.
 *
 * When a stream has been read to End-of-stream, and all ranges between 0 and End-of-stream are
 * [State.COMPLETE], then all records are considered to have been processed.
 *
 * A [Batch] may contain an optional `groupId`. If provided, the most advanced state provided for
 * any batch will apply to all batches with the same `groupId`. This is useful for a case where each
 * batch represents part of a larger work unit that is only completed when all parts are processed.
 * (We used most advanced instead of latest to avoid race conditions.)
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
    val groupId: String?

    enum class State {
        PROCESSED,
        STAGED,
        PERSISTED,
        COMPLETE;

        fun isPersisted(): Boolean =
            when (this) {
                PERSISTED,
                COMPLETE -> true
                else -> false
            }
    }

    fun isPersisted(): Boolean = state.isPersisted()

    val state: State

    /**
     * If a [Batch] is [State.COMPLETE], there's nothing further to do. If it is part of a group,
     * then its state will be updated by the next batch in the group that advances.
     */
    val requiresProcessing: Boolean
        get() = state != State.COMPLETE && groupId == null
}

/** Simple batch: use if you need no other metadata for processing. */
data class SimpleBatch(
    override val state: Batch.State,
    override val groupId: String? = null,
) : Batch

/**
 * Internally-used wrapper for tracking the association between a batch and the range of records it
 * contains.
 */
data class BatchEnvelope<B : Batch>(
    val batch: B,
    val ranges: RangeSet<Long> = TreeRangeSet.create(),
    val streamDescriptor: DestinationStream.Descriptor
) {
    constructor(
        batch: B,
        range: Range<Long>?,
        streamDescriptor: DestinationStream.Descriptor
    ) : this(
        batch = batch,
        ranges = range?.let { TreeRangeSet.create(listOf(range)) } ?: TreeRangeSet.create(),
        streamDescriptor = streamDescriptor
    )

    fun <C : Batch> withBatch(newBatch: C): BatchEnvelope<C> {
        return BatchEnvelope(newBatch, ranges, streamDescriptor)
    }
}
