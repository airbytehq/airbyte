/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.asProtocolStreamDescriptor
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamState

/** A [StateQuerier] is like a read-only [StateManager]. */
interface StateQuerier {
    /** [feeds] is all the [Feed]s in the configured catalog passed via the CLI. */
    val feeds: List<Feed>

    /** Returns the current state value for the given [feed]. */
    fun current(feed: Feed): OpaqueStateValue?
}

/** Singleton object which tracks the state of an ongoing READ operation. */
class StateManager(
    global: Global? = null,
    initialGlobalState: OpaqueStateValue? = null,
    initialStreamStates: Map<Stream, OpaqueStateValue?> = mapOf(),
) : StateQuerier {
    private val global: GlobalStateManager?
    private val nonGlobal: Map<StreamIdentifier, NonGlobalStreamStateManager>

    init {
        if (global == null) {
            this.global = null
            nonGlobal =
                initialStreamStates
                    .mapValues { NonGlobalStreamStateManager(it.key, it.value) }
                    .mapKeys { it.key.id }
        } else {
            val globalStreams: Map<Stream, OpaqueStateValue?> =
                global.streams.associateWith { initialStreamStates[it] }
            this.global =
                GlobalStateManager(
                    global = global,
                    initialGlobalState = initialGlobalState,
                    initialStreamStates = globalStreams,
                )
            nonGlobal =
                initialStreamStates
                    .filterKeys { !globalStreams.containsKey(it) }
                    .mapValues { NonGlobalStreamStateManager(it.key, it.value) }
                    .mapKeys { it.key.id }
        }
    }

    override val feeds: List<Feed> =
        listOfNotNull(this.global?.feed) +
            (this.global?.streamStateManagers?.values?.map { it.feed } ?: listOf()) +
            nonGlobal.values.map { it.feed }

    override fun current(feed: Feed): OpaqueStateValue? = scoped(feed).current()

    /** Returns a [StateManagerScopedToFeed] instance scoped to this [feed]. */
    fun scoped(feed: Feed): StateManagerScopedToFeed =
        when (feed) {
            is Global -> global ?: throw IllegalArgumentException("unknown global key")
            is Stream -> global?.streamStateManagers?.get(feed.id)
                    ?: nonGlobal[feed.id] ?: throw IllegalArgumentException("unknown stream key")
        }

    interface StateManagerScopedToFeed {
        /**
         * The [Feed] to which the [StateManager] is scoped in this instance of
         * [StateManagerScopedToFeed].
         */
        val feed: Feed

        /** Returns the current state value in the [StateManager] for this [feed]. */
        fun current(): OpaqueStateValue?

        /** Updates the current state value in the [StateManager] for this [feed]. */
        fun set(
            state: OpaqueStateValue,
            numRecords: Long,
        )
    }

    /**
     * Returns the Airbyte STATE messages which checkpoint the progress of the READ in the platform.
     * Updates the internal state of the [StateManager] to ensure idempotency (no redundant messages
     * are emitted).
     */
    fun checkpoint(): List<AirbyteStateMessage> =
        listOfNotNull(global?.checkpoint()) + nonGlobal.mapNotNull { it.value.checkpoint() }

    private sealed class BaseStateManager<K : Feed>(
        override val feed: K,
        initialState: OpaqueStateValue?,
    ) : StateManagerScopedToFeed {
        private var currentStateValue: OpaqueStateValue? = initialState
        private var pendingStateValue: OpaqueStateValue? = initialState
        private var pendingNumRecords: Long = 0L

        @Synchronized override fun current(): OpaqueStateValue? = currentStateValue

        @Synchronized
        override fun set(
            state: OpaqueStateValue,
            numRecords: Long,
        ) {
            pendingStateValue = state
            pendingNumRecords += numRecords
        }

        /**
         * Called by [StateManager.checkpoint] to generate the Airbyte STATE messages for the
         * checkpoint.
         *
         * The return value is either [Fresh] or [Stale] depending on whether [set] has been called
         * since the last call to [takeForCheckpoint], or not, respectively.
         *
         * [Stale] messages are simply ignored when dealing only with [Stream] feeds, however these
         * may be required when emitting Airbyte STATE messages of type GLOBAL.
         */
        @Synchronized
        fun takeForCheckpoint(): StateForCheckpoint {
            // Check if there is a pending state value or not.
            // If not, then set() HASN'T been called since the last call to takeForCheckpoint(),
            // because set() can only accept non-null state values.
            //
            // This means that there is nothing worth checkpointing for this particular feed.
            // In that case, exit early with the current state value.
            val freshStateValue: OpaqueStateValue =
                pendingStateValue ?: return Stale(currentStateValue)
            // This point is reached in the case where there is a pending state value.
            // This means that set() HAS been called since the last call to takeForCheckpoint().
            //
            // Keep a copy of the total number of records registered in all calls to set() since the
            // last call to takeForCheckpoint(), this number will be returned.
            val freshNumRecords: Long = pendingNumRecords
            // Update current state value.
            currentStateValue = freshStateValue
            // Reset the pending state, which will be overwritten by the next call to set().
            pendingStateValue = null
            pendingNumRecords = 0L
            // Return the latest state value as well as the total number of records seen since the
            // last call to takeForCheckpoint().
            return Fresh(freshStateValue, freshNumRecords)
        }
    }

    /** Return value type for [BaseStateManager.takeForCheckpoint]. */
    private sealed interface StateForCheckpoint {
        val opaqueStateValue: OpaqueStateValue?
        val numRecords: Long
    }

    /**
     * [StateForCheckpoint] implementation for when [StateManagerScopedToFeed.set] has been called
     * since the last call to [BaseStateManager.takeForCheckpoint].
     */
    private data class Fresh(
        override val opaqueStateValue: OpaqueStateValue,
        override val numRecords: Long,
    ) : StateForCheckpoint

    /**
     * [StateForCheckpoint] implementation for when [StateManagerScopedToFeed.set] has NOT been
     * called since the last call to [BaseStateManager.takeForCheckpoint].
     */
    private data class Stale(
        override val opaqueStateValue: OpaqueStateValue?,
    ) : StateForCheckpoint {
        override val numRecords: Long
            get() = 0L
    }

    private class GlobalStateManager(
        global: Global,
        initialGlobalState: OpaqueStateValue?,
        initialStreamStates: Map<Stream, OpaqueStateValue?>,
    ) : BaseStateManager<Global>(global, initialGlobalState) {
        val streamStateManagers: Map<StreamIdentifier, GlobalStreamStateManager> =
            initialStreamStates
                .mapValues { GlobalStreamStateManager(it.key, it.value) }
                .mapKeys { it.key.id }

        fun checkpoint(): AirbyteStateMessage? {
            var shouldCheckpoint = false
            var totalNumRecords = 0L
            val globalStateForCheckpoint: StateForCheckpoint = takeForCheckpoint()
            totalNumRecords += globalStateForCheckpoint.numRecords
            if (globalStateForCheckpoint is Fresh) shouldCheckpoint = true
            val streamStates = mutableListOf<AirbyteStreamState>()
            for ((_, streamStateManager) in streamStateManagers) {
                val streamStateForCheckpoint: StateForCheckpoint =
                    streamStateManager.takeForCheckpoint()
                totalNumRecords += streamStateForCheckpoint.numRecords
                if (streamStateForCheckpoint is Fresh) shouldCheckpoint = true
                val streamID: StreamIdentifier = streamStateManager.feed.id
                streamStates.add(
                    AirbyteStreamState()
                        .withStreamDescriptor(streamID.asProtocolStreamDescriptor())
                        .withStreamState(streamStateForCheckpoint.opaqueStateValue),
                )
            }
            if (!shouldCheckpoint) {
                return null
            }
            val airbyteGlobalState =
                AirbyteGlobalState()
                    .withSharedState(globalStateForCheckpoint.opaqueStateValue)
                    .withStreamStates(streamStates)
            return AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                .withGlobal(airbyteGlobalState)
                .withSourceStats(AirbyteStateStats().withRecordCount(totalNumRecords.toDouble()))
        }
    }

    private class GlobalStreamStateManager(
        stream: Stream,
        initialState: OpaqueStateValue?,
    ) : BaseStateManager<Stream>(stream, initialState)

    private class NonGlobalStreamStateManager(
        stream: Stream,
        initialState: OpaqueStateValue?,
    ) : BaseStateManager<Stream>(stream, initialState) {
        fun checkpoint(): AirbyteStateMessage? {
            val streamStateForCheckpoint: StateForCheckpoint = takeForCheckpoint()
            if (streamStateForCheckpoint is Stale) {
                return null
            }
            val airbyteStreamState =
                AirbyteStreamState()
                    .withStreamDescriptor(feed.id.asProtocolStreamDescriptor())
                    .withStreamState(streamStateForCheckpoint.opaqueStateValue)
            return AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(airbyteStreamState)
                .withSourceStats(
                    AirbyteStateStats()
                        .withRecordCount(streamStateForCheckpoint.numRecords.toDouble())
                )
        }
    }
}
