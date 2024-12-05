/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.dest_state_lifecycle_manager

import com.google.common.annotations.VisibleForTesting
import com.google.common.base.Preconditions
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import java.util.*
import java.util.function.Supplier

/**
 * Detects the type of the state being received by anchoring on the first state type it sees. Fail
 * if receives states of multiple types--each instance of this class can only support state messages
 * of one type. The protocol specifies that a source should emit state messages of a single type
 * during a sync, so a single instance of this manager is sufficient for a destination to track
 * state during a sync.
 *
 * Strategy: Delegates state messages of each type to a StateManager that is appropriate to that
 * state type.
 *
 * Per the protocol, if state type is not set, assumes the LEGACY state type.
 */
class DefaultDestStateLifecycleManager
@VisibleForTesting
internal constructor(
    singleStateManager: DestStateLifecycleManager,
    streamStateManager: DestStateLifecycleManager
) : DestStateLifecycleManager {
    private var stateType: AirbyteStateMessage.AirbyteStateType? = null

    // allows us to delegate calls to the appropriate underlying state manager.
    private val internalStateManagerSupplier = Supplier {
        if (
            stateType == AirbyteStateMessage.AirbyteStateType.GLOBAL ||
                stateType == AirbyteStateMessage.AirbyteStateType.LEGACY ||
                stateType == null
        ) {
            return@Supplier singleStateManager
        } else if (stateType == AirbyteStateMessage.AirbyteStateType.STREAM) {
            return@Supplier streamStateManager
        } else {
            throw IllegalArgumentException("unrecognized state type")
        }
    }

    constructor(
        defaultNamespace: String?
    ) : this(DestSingleStateLifecycleManager(), DestStreamStateLifecycleManager(defaultNamespace))

    override fun addState(message: AirbyteMessage) {
        Preconditions.checkArgument(
            message.type == AirbyteMessage.Type.STATE,
            "Messages passed to State Manager must be of type STATE."
        )
        Preconditions.checkArgument(isStateTypeCompatible(stateType, message.state.type))

        setManagerStateTypeIfNotSet(message)

        internalStateManagerSupplier.get().addState(message)
    }

    /**
     * If the state type for the manager is not set, sets it using the state type from the message.
     * If the type on the message is null, we assume it is LEGACY. After the first, state message is
     * added to the manager, the state type is set and is immutable.
     *
     * @param message
     * - state message whose state will be used if internal state type is not set
     */
    private fun setManagerStateTypeIfNotSet(message: AirbyteMessage) {
        // detect and set state type.
        if (stateType == null) {
            stateType =
                if (message.state.type == null) {
                    AirbyteStateMessage.AirbyteStateType.LEGACY
                } else {
                    message.state.type
                }
        }
    }

    override fun markPendingAsFlushed() {
        internalStateManagerSupplier.get().markPendingAsFlushed()
    }

    override fun listFlushed(): Queue<AirbyteMessage> {
        return internalStateManagerSupplier.get().listFlushed()
    }

    override fun markFlushedAsCommitted() {
        internalStateManagerSupplier.get().markFlushedAsCommitted()
    }

    override fun markPendingAsCommitted() {
        internalStateManagerSupplier.get().markPendingAsCommitted()
    }

    override fun markPendingAsCommitted(stream: AirbyteStreamNameNamespacePair) {
        internalStateManagerSupplier.get().markPendingAsCommitted(stream)
    }

    override fun clearCommitted() {
        internalStateManagerSupplier.get().clearCommitted()
    }

    override fun listCommitted(): Queue<AirbyteMessage>? {
        return internalStateManagerSupplier.get().listCommitted()
    }

    override fun supportsPerStreamFlush(): Boolean {
        return internalStateManagerSupplier.get().supportsPerStreamFlush()
    }

    companion object {
        /**
         * Given the type of previously recorded state by the state manager, determines if a newly
         * added state message's type is compatible. Based on the previously set state type,
         * determines if a new one is compatible. If the previous state is null, any new state is
         * compatible. If new state type is null, it should be treated as LEGACY. Thus,
         * previousStateType == LEGACY and newStateType == null IS compatible. All other state types
         * are compatible based on equality.
         *
         * @param previousStateType
         * - state type previously recorded by the state manager
         * @param newStateType
         * - state message of a newly added message
         * @return true if compatible, otherwise false
         */
        private fun isStateTypeCompatible(
            previousStateType: AirbyteStateMessage.AirbyteStateType?,
            newStateType: AirbyteStateMessage.AirbyteStateType?
        ): Boolean {
            return previousStateType == null ||
                previousStateType == AirbyteStateMessage.AirbyteStateType.LEGACY &&
                    newStateType == null ||
                previousStateType == newStateType
        }
    }
}
