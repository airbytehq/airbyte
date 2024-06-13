/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.dest_state_lifecycle_manager

import com.google.common.annotations.VisibleForTesting
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import java.util.*

/**
 * This [DestStateLifecycleManager] handles any state where there is a guarantee that any single
 * state message represents the state for the ENTIRE connection. At the time of writing, GLOBAL and
 * LEGACY state types are the state type that match this pattern.
 *
 * Does NOT store duplicates. Because each state message represents the entire state for the
 * connection, it only stores (and emits) the LAST state it received at each phase.
 */
class DestSingleStateLifecycleManager : DestStateLifecycleManager {
    private var lastPendingState: AirbyteMessage? = null
    private var lastFlushedState: AirbyteMessage? = null
    private var lastCommittedState: AirbyteMessage? = null

    override fun addState(message: AirbyteMessage) {
        lastPendingState = message
    }

    @VisibleForTesting
    fun listPending(): Queue<AirbyteMessage> {
        return stateMessageToQueue(lastPendingState)
    }

    override fun markPendingAsFlushed() {
        if (lastPendingState != null) {
            lastFlushedState = lastPendingState
            lastPendingState = null
        }
    }

    override fun listFlushed(): Queue<AirbyteMessage> {
        return stateMessageToQueue(lastFlushedState)
    }

    override fun markFlushedAsCommitted() {
        if (lastFlushedState != null) {
            lastCommittedState = lastFlushedState
            lastFlushedState = null
        }
    }

    override fun clearCommitted() {
        lastCommittedState = null
    }

    override fun markPendingAsCommitted() {
        if (lastPendingState != null) {
            lastCommittedState = lastPendingState
            lastPendingState = null
        }
    }

    override fun markPendingAsCommitted(stream: AirbyteStreamNameNamespacePair) {
        // We declare supportsPerStreamFlush as false, so this method should never be called.
        throw IllegalStateException(
            "Committing a single stream state is not supported for this state type."
        )
    }

    override fun listCommitted(): Queue<AirbyteMessage> {
        return stateMessageToQueue(lastCommittedState)
    }

    override fun supportsPerStreamFlush(): Boolean {
        return false
    }

    companion object {
        private fun stateMessageToQueue(stateMessage: AirbyteMessage?): Queue<AirbyteMessage> {
            return LinkedList(
                if (stateMessage == null) emptyList<AirbyteMessage>() else listOf(stateMessage)
            )
        }
    }
}
