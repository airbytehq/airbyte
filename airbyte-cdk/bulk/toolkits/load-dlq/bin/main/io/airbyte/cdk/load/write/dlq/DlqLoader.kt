/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.dlq

import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey

/**
 * DeadLetterQueueLoader interface.
 *
 * A DeadLetterQueueLoader is a Loader that can return records for a dead letter queue.
 *
 * The Loader is expected to write the record into a destination. The batching strategy remains
 * entirely up to the Loader implementation. To support batching, the Loader can declare its own
 * state [S].
 */
interface DlqLoader<S> : AutoCloseable {

    sealed interface DlqLoadResult
    data object Incomplete : DlqLoadResult
    data class Complete(val rejectedRecords: List<DestinationRecordRaw>? = null) : DlqLoadResult

    /** Called when starting a batch. */
    fun start(key: StreamKey, part: Int): S

    /**
     * Accept is the main method called for every [record] to process. [state] is the current state
     * associated with the record. Note that in this context, [state] refers to the output from the
     * most recent [start] call. This is not an [AirbyteState].
     *
     * Returns
     * - [Complete] if data was loaded completely. [accept] may return rejected records for the dead
     * letter queue. Note that the CDK will only checkpoint when the all the records for a given
     * AirbyteState are either loaded in the destination or written to the dead letter queue.
     * - [Incomplete] if the record was staged.
     */
    fun accept(record: DestinationRecordRaw, state: S): DlqLoadResult

    /**
     * Called when the data needs to be persisted. The CDK will call this if data hasn't been
     * persisted for a given amount of time or when under memory pressure in an attempt to reclaim
     * some memory to continue processing.
     */
    fun finish(state: S): Complete
}
