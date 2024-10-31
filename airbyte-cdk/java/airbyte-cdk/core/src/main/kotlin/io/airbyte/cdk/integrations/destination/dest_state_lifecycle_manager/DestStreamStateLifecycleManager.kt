/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.dest_state_lifecycle_manager

import com.google.common.annotations.VisibleForTesting
import com.google.common.base.Preconditions
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.*

/**
 * This [DestStateLifecycleManager] handles any state where the state messages are scoped by stream.
 * In these cases, at each state of the process, it tracks the LAST state message for EACH stream
 * (no duplicates!).
 *
 * Guaranteed to output state messages in order relative to other messages of the SAME state. Does
 * NOT guarantee that state messages of different streams will be output in the order in which they
 * were received. State messages across streams will be emitted in alphabetical order (primary sort
 * on namespace, secondary on name).
 */
class DestStreamStateLifecycleManager(private val defaultNamespace: String?) :
    DestStateLifecycleManager {
    private val streamToLastPendingState: MutableMap<StreamDescriptor, AirbyteMessage> = HashMap()
    private val streamToLastFlushedState: MutableMap<StreamDescriptor, AirbyteMessage> = HashMap()
    private val streamToLastCommittedState: MutableMap<StreamDescriptor, AirbyteMessage> = HashMap()

    override fun addState(message: AirbyteMessage) {
        Preconditions.checkArgument(
            message.state.type == AirbyteStateMessage.AirbyteStateType.STREAM
        )
        val originalStreamId = message.state.stream.streamDescriptor
        val actualStreamId: StreamDescriptor
        val namespace = originalStreamId.namespace
        actualStreamId =
            if (namespace == null || namespace.isEmpty()) {
                // If the state's namespace is null/empty, we need to be able to find it using the
                // default namespace
                // (because many destinations actually set records' namespace to the default
                // namespace before
                // they make it into this class).
                // Clone the streamdescriptor so that we don't modify the original state message.
                StreamDescriptor().withName(originalStreamId.name).withNamespace(defaultNamespace)
            } else {
                originalStreamId
            }
        streamToLastPendingState[actualStreamId] = message
    }

    @VisibleForTesting
    fun listPending(): Queue<AirbyteMessage> {
        return listStatesInOrder(streamToLastPendingState)
    }

    /*
     * Similar to #markFlushedAsCommmitted, this method should no longer be used to align with the
     * changes to destination checkpointing where flush/commit operations will be bundled
     */
    @Deprecated("")
    override fun markPendingAsFlushed() {
        moveToNextPhase(streamToLastPendingState, streamToLastFlushedState)
    }

    override fun listFlushed(): Queue<AirbyteMessage> {
        return listStatesInOrder(streamToLastFlushedState)
    }

    /*
     * During the process of migration to destination checkpointing, this method should no longer be in
     * use in favor of #markPendingAsCommitted where states will be flushed/committed as a singular
     * transaction
     */
    @Deprecated("")
    override fun markFlushedAsCommitted() {
        moveToNextPhase(streamToLastFlushedState, streamToLastCommittedState)
    }

    override fun clearCommitted() {
        streamToLastCommittedState.clear()
    }

    override fun markPendingAsCommitted() {
        moveToNextPhase(streamToLastPendingState, streamToLastCommittedState)
    }

    override fun markPendingAsCommitted(stream: AirbyteStreamNameNamespacePair) {
        // streamToLastCommittedState is keyed using defaultNamespace instead of namespace=null.
        // (see
        // #addState)
        // Many destinations actually modify the records' namespace immediately after reading them
        // from
        // stdin,
        // but we should have a null-check here just in case.
        val actualNamespace = if (stream.namespace == null) defaultNamespace else stream.namespace
        val sd = StreamDescriptor().withName(stream.name).withNamespace(actualNamespace)
        val lastPendingState = streamToLastPendingState.remove(sd)
        if (lastPendingState != null) {
            streamToLastCommittedState[sd] = lastPendingState
        }
    }

    override fun listCommitted(): Queue<AirbyteMessage> {
        return listStatesInOrder(streamToLastCommittedState)
    }

    override fun supportsPerStreamFlush(): Boolean {
        return true
    }

    companion object {
        /**
         * Lists out the states in the stream to state maps. Guarantees a deterministic sort order,
         * which is handy because we are going from a map (unsorted) to a queue. The sort order
         * primary sort on namespace (with null at the top) followed by secondary sort on name. This
         * maps onto the pretty common order that we list streams elsewhere.
         *
         * @param streamToState
         * - map of stream descriptor to its last state
         * @return queue with the states ordered per the sort mentioned above
         */
        private fun listStatesInOrder(
            streamToState: Map<StreamDescriptor, AirbyteMessage>
        ): Queue<AirbyteMessage> {
            return LinkedList(
                streamToState.entries

                    // typically, we support by namespace and then stream name, so we retain
                    // that pattern here.
                    .sortedWith(
                        Comparator.comparing<Map.Entry<StreamDescriptor, AirbyteMessage>, String>(
                                { entry: Map.Entry<StreamDescriptor, AirbyteMessage> ->
                                    entry.key.namespace
                                },
                                Comparator.nullsFirst<String>(Comparator.naturalOrder<String>())
                            ) // namespace is allowed to be null
                            .thenComparing<String> {
                                entry: Map.Entry<StreamDescriptor, AirbyteMessage> ->
                                entry.key.name
                            }
                    )
                    .map { obj: Map.Entry<StreamDescriptor, AirbyteMessage> -> obj.value }
            )
        }

        /**
         * Moves all state messages from previous phase into next phase.
         *
         * @param prevPhase
         * - map of stream to state messages for previous phase that will be moved to next phase.
         * when this method returns this map will be empty.
         * @param nextPhase
         * - map into which state messages from prevPhase will be added.
         */
        private fun moveToNextPhase(
            prevPhase: MutableMap<StreamDescriptor, AirbyteMessage>,
            nextPhase: MutableMap<StreamDescriptor, AirbyteMessage>
        ) {
            if (!prevPhase.isEmpty()) {
                nextPhase.putAll(prevPhase)
                prevPhase.clear()
            }
        }
    }
}
