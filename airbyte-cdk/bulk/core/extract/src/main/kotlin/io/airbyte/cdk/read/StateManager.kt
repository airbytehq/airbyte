/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
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
    private val nonGlobal: Map<AirbyteStreamNameNamespacePair, NonGlobalStreamStateManager>

    init {
        if (global == null) {
            this.global = null
            nonGlobal =
                initialStreamStates
                    .mapValues { NonGlobalStreamStateManager(it.key, it.value) }
                    .mapKeys { it.key.namePair }
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
                    .mapKeys { it.key.namePair }
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
            is Stream -> global?.streamStateManagers?.get(feed.namePair)
                    ?: nonGlobal[feed.namePair]
                        ?: throw IllegalArgumentException("unknown stream key")
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
        private val isCheckpointUnique: Boolean = true,
    ) : StateManagerScopedToFeed {
        private var current: OpaqueStateValue?
        private var pending: OpaqueStateValue?
        private var isPending: Boolean
        private var pendingNumRecords: Long

        init {
            synchronized(this) {
                current = initialState
                pending = initialState
                isPending = initialState != null
                pendingNumRecords = 0L
            }
        }

        override fun current(): OpaqueStateValue? = synchronized(this) { current }

        override fun set(
            state: OpaqueStateValue,
            numRecords: Long,
        ) {
            synchronized(this) {
                pending = state
                isPending = true
                pendingNumRecords += numRecords
            }
        }

        fun swap(): Pair<OpaqueStateValue?, Long>? {
            synchronized(this) {
                if (isCheckpointUnique && !isPending) {
                    return null
                }
                val returnValue: Pair<OpaqueStateValue?, Long> = pending to pendingNumRecords
                current = pending
                pendingNumRecords = 0L
                return returnValue
            }
        }
    }

    private class GlobalStateManager(
        global: Global,
        initialGlobalState: OpaqueStateValue?,
        initialStreamStates: Map<Stream, OpaqueStateValue?>,
    ) : BaseStateManager<Global>(global, initialGlobalState) {
        val streamStateManagers: Map<AirbyteStreamNameNamespacePair, GlobalStreamStateManager> =
            initialStreamStates
                .mapValues { GlobalStreamStateManager(it.key, it.value) }
                .mapKeys { it.key.namePair }

        fun checkpoint(): AirbyteStateMessage? {
            var numSwapped = 0
            var totalNumRecords: Long = 0L
            var globalStateValue: OpaqueStateValue? = current()
            val globalSwapped: Pair<OpaqueStateValue?, Long>? = swap()
            if (globalSwapped != null) {
                numSwapped++
                globalStateValue = globalSwapped.first
                totalNumRecords += globalSwapped.second
            }
            val streamStates = mutableListOf<AirbyteStreamState>()
            for ((_, streamStateManager) in streamStateManagers) {
                var streamStateValue: OpaqueStateValue? = streamStateManager.current()
                val globalStreamSwapped: Pair<OpaqueStateValue?, Long>? = streamStateManager.swap()
                if (globalStreamSwapped != null) {
                    numSwapped++
                    streamStateValue = globalStreamSwapped.first
                    totalNumRecords += globalStreamSwapped.second
                }
                streamStates.add(
                    AirbyteStreamState()
                        .withStreamDescriptor(streamStateManager.feed.streamDescriptor)
                        .withStreamState(streamStateValue),
                )
            }
            val airbyteGlobalState =
                AirbyteGlobalState()
                    .withSharedState(globalStateValue)
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
    ) : BaseStateManager<Stream>(stream, initialState, isCheckpointUnique = false)

    private class NonGlobalStreamStateManager(
        stream: Stream,
        initialState: OpaqueStateValue?,
    ) : BaseStateManager<Stream>(stream, initialState) {
        fun checkpoint(): AirbyteStateMessage? {
            val (opaqueStateValue: OpaqueStateValue?, numRecords: Long) = swap() ?: return null
            val airbyteStreamState =
                AirbyteStreamState()
                    .withStreamDescriptor(feed.streamDescriptor)
                    .withStreamState(opaqueStateValue)
            return AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(airbyteStreamState)
                .withSourceStats(AirbyteStateStats().withRecordCount(numRecords.toDouble()))
        }
    }
}
