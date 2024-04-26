/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.StreamStateValue
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.AirbyteStreamState

private typealias NameKey = AirbyteStreamNameNamespacePair

/** Singleton object which tracks the state of an ongoing READ operation. */
class StateManager(
    initialGlobal: State<GlobalKey>?,
    initialStreams: Collection<State<StreamKey>>,
) {

    private val global: GlobalStateManager?
    private val nonGlobal: Map<NameKey, NonGlobalStreamStateManager>

    init {
        val streamMap: Map<NameKey, State<StreamKey>> =
            initialStreams.associateBy { it.key.namePair }
        if (initialGlobal == null) {
            global = null
            nonGlobal = streamMap.mapValues { NonGlobalStreamStateManager(it.value) }
        } else {
            val globalStreams: Map<NameKey, State<StreamKey>> =
                initialGlobal.key.streamKeys
                    .mapNotNull { streamMap[it.namePair] }
                    .associateBy { it.key.namePair }
            global =
                GlobalStateManager(
                    initialGlobalState = initialGlobal,
                    initialStreamStates = globalStreams.values
                )
            nonGlobal =
                streamMap
                    .filterKeys { !globalStreams.containsKey(it) }
                    .mapValues { NonGlobalStreamStateManager(it.value) }
        }
    }

    /** Returns the starting point of a new READ operation. */
    fun currentStates(): List<State<out Key>> =
        listOfNotNull(global?.state()) +
            (global?.streamStateManagers?.values ?: listOf()).map { it.state() } +
            nonGlobal.values.map { it.state() }

    /** Updates the internal state of the [StateManager] with a [GlobalState]. */
    fun set(state: GlobalState, numRecords: Long) {
        global?.set(state, numRecords)
    }

    /** Updates the internal state of the [StateManager] with a [StreamState]. */
    fun set(state: StreamState, numRecords: Long) {
        global?.streamStateManagers?.get(state.key.namePair)?.set(state, numRecords)
        nonGlobal[state.key.namePair]?.set(state, numRecords)
    }

    /**
     * Returns the Airbyte STATE messages which checkpoint the progress of the READ in the platform.
     * Updates the internal state of the [StateManager] to ensure idempotency (no redundant messages
     * are emitted).
     */
    fun checkpoint(): List<AirbyteStateMessage> =
        listOfNotNull(global?.checkpoint()) + nonGlobal.mapNotNull { it.value.checkpoint() }

    private sealed class BaseStateManager<S : Key>(
        initialState: State<S>,
        private val isCheckpointUnique: Boolean = true
    ) {

        val key: S = initialState.key

        private var current: State<S> = initialState
        private var pending: State<S> = initialState
        private var pendingNumRecords: Long = 0L

        fun state(): State<S> = synchronized(this) { current }

        fun set(state: State<S>, numRecords: Long) {
            synchronized(this) {
                pending = state
                pendingNumRecords += numRecords
            }
        }

        protected fun swap(): Pair<SerializableState<S>, Long>? {
            synchronized(this) {
                if (isCheckpointUnique && pendingNumRecords == 0L && pending == current) {
                    return null
                }
                return when (val pendingState: State<S> = pending) {
                    is SerializableState<S> ->
                        (pendingState to pendingNumRecords).also {
                            current = pendingState
                            pendingNumRecords = 0L
                        }
                    else -> null
                }
            }
        }
    }

    private class GlobalStateManager(
        initialGlobalState: State<GlobalKey>,
        initialStreamStates: Collection<State<StreamKey>>
    ) : BaseStateManager<GlobalKey>(initialGlobalState) {

        val streamStateManagers: Map<NameKey, GlobalStreamStateManager> =
            initialStreamStates.associate { it.key.namePair to GlobalStreamStateManager(it) }

        fun checkpoint(): AirbyteStateMessage? {
            val (state: SerializableState<GlobalKey>, numRecords: Long) = swap() ?: return null
            var totalNumRecords: Long = numRecords
            val streamStates = mutableListOf<AirbyteStreamState>()
            for ((_, streamStateManager) in streamStateManagers) {
                val (streamState, streamNumRecords) = streamStateManager.checkpointGlobalStream()
                streamStates.add(streamState)
                totalNumRecords += streamNumRecords
            }
            val airbyteGlobalState =
                AirbyteGlobalState()
                    .withSharedState(
                        Jsons.jsonNode((state as SerializableGlobalState).toGlobalStateValue())
                    )
                    .withStreamStates(streamStates)
            return AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                .withGlobal(airbyteGlobalState)
                .withSourceStats(AirbyteStateStats().withRecordCount(totalNumRecords.toDouble()))
        }
    }

    private class GlobalStreamStateManager(initialState: State<StreamKey>) :
        BaseStateManager<StreamKey>(initialState, isCheckpointUnique = false) {

        fun checkpointGlobalStream(): Pair<AirbyteStreamState, Long> {
            val (state: SerializableState<StreamKey>?, numRecords: Long) = swap() ?: (null to 0L)
            val value: StreamStateValue? = (state as? SerializableStreamState)?.toStreamStateValue()
            return AirbyteStreamState()
                .withStreamDescriptor(key.streamDescriptor)
                .withStreamState(value?.let { Jsons.jsonNode(it) }) to numRecords
        }
    }

    private class NonGlobalStreamStateManager(initialState: State<StreamKey>) :
        BaseStateManager<StreamKey>(initialState) {

        fun checkpoint(): AirbyteStateMessage? {
            val (state: SerializableState<StreamKey>, numRecords: Long) = swap() ?: return null
            val airbyteStreamState =
                AirbyteStreamState()
                    .withStreamDescriptor(key.streamDescriptor)
                    .withStreamState(
                        Jsons.jsonNode((state as SerializableStreamState).toStreamStateValue())
                    )
            return AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(airbyteStreamState)
                .withSourceStats(AirbyteStateStats().withRecordCount(numRecords.toDouble()))
        }
    }
}
