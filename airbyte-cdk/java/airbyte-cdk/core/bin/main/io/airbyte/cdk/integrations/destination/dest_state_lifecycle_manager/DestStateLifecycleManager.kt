/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.dest_state_lifecycle_manager

import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import java.util.*

/**
 * This class manages the lifecycle of state message. It tracks state messages that are in 3 states:
 *
 * 1. pending - associated records have been accepted by the connector but has NOT been pushed to
 * the destination
 * 1. flushed - associated records have been flushed to tmp storage in the destination but have NOT
 * been committed
 * 1. committed - associated records have been committed
 */
interface DestStateLifecycleManager {
    /**
     * Accepts a state into the manager. The state starts in a pending state.
     *
     * @param message
     * - airbyte message of type state
     */
    fun addState(message: AirbyteMessage)

    /**
     * Moves any tracked state messages that are currently pending to flushed.
     *
     * @Deprecated since destination checkpointing will be bundling flush & commit into the same
     * operation
     */
    fun markPendingAsFlushed()

    /**
     * List all tracked state messages that are flushed.
     *
     * @return list of state messages
     */
    fun listFlushed(): Queue<AirbyteMessage>

    /**
     * Moves any tracked state messages that are currently flushed to committed.
     *
     * @Deprecated since destination checkpointing will be bundling flush and commit into the same
     * operation
     */
    fun markFlushedAsCommitted()

    /**
     * Clears any committed state messages, this is called after returning the state message to the
     * platform. The rationale behind this logic is to avoid returning duplicated state messages
     * that would otherwise be held in the `committed` state
     */
    fun clearCommitted()

    /**
     * Moves any tracked state messages that are currently pending to committed.
     *
     * Note: that this is skipping "flushed" state since flushed meant that this was using a staging
     * area to hold onto files, for the changes with checkpointing this step is skipped. It follows
     * under the guiding principle that destination needs to commit
     * [io.airbyte.protocol.models.AirbyteRecordMessage] more frequently to checkpoint. The new
     * transaction logic will be:
     *
     * Buffer -(flush)-> Staging (Blob Storage) -(commit to airbyte_raw)-> Destination table
     */
    fun markPendingAsCommitted()

    /** Mark all pending states for the given stream as committed. */
    fun markPendingAsCommitted(stream: AirbyteStreamNameNamespacePair)

    /**
     * List all tracked state messages that are committed.
     *
     * @return list of state messages
     */
    fun listCommitted(): Queue<AirbyteMessage>?

    fun supportsPerStreamFlush(): Boolean
}
