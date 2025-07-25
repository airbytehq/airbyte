/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.asProtocolStreamDescriptor
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.StateManager.StateManagerScopedToFeed
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamState
import kotlin.collections.List
import kotlin.collections.mutableMapOf

/** Singleton object which tracks the state of an ongoing READ operation. */
class StateManager(
    global: Global? = null,
    initialGlobalState: OpaqueStateValue? = null,
    initialStreamStates: Map<Stream, OpaqueStateValue?> = mapOf(),
) {
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
                global.streams.associateWith { initialStreamStates[it] } +
                    initialStreamStates.filterKeys { global.streams.contains(it).not() }
            this.global =
                GlobalStateManager(
                    global = global,
                    initialGlobalState = initialGlobalState,
                    initialStreamStates = globalStreams,
                )
            nonGlobal = emptyMap()
        }
    }

    /** [feeds] is all the [Feed]s in the configured catalog passed via the CLI. */
    val feeds: List<Feed> =
        listOfNotNull(this.global?.feed) +
            (this.global?.streamStateManagers?.values?.map { it.feed } ?: listOf()) +
            nonGlobal.values.map { it.feed }

    /** Returns the current state value for the given [feed]. */
    fun current(feed: Feed): OpaqueStateValue? = scoped(feed).current()

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
            partitionId: String?,
            id: Int?,
        )

        /** Resets the current state value in the [StateManager] for this [feed] to zero. */
        fun reset()
    }

    /**
     * Returns the Airbyte STATE messages which checkpoint the progress of the READ in the platform.
     * Updates the internal state of the [StateManager] to ensure idempotency (no redundant messages
     * are emitted).
     */
    fun checkpoint(): List<AirbyteStateMessage> {
        return (global?.checkpoint()
            ?: emptyList()) +
            nonGlobal
                .mapNotNull { it.value.checkpoint()?.filter { it.stream.streamState.isNull.not() } }
                .flatten()
    }

    data class StateForCheckpointWithPartitionId(
        val pendingState: OpaqueStateValue,
        val partitionId: String?,
        val pendingNumRecords: Long,
        var id: Int?,
    )
}

private sealed class BaseStateManager<K : Feed>(
    override val feed: K,
    initialState: OpaqueStateValue?,
) : StateManagerScopedToFeed {
    private var currentStateValue: OpaqueStateValue? = initialState
    // Rather than the highest pending state, we want to buffer and emit all pending states
    // This is required by destinations in Socket mode
    private var pendingStateValues: MutableList<StateManager.StateForCheckpointWithPartitionId> =
        mutableListOf()
    @Synchronized override fun current(): OpaqueStateValue? = currentStateValue

    @Synchronized
    override fun set(
        state: OpaqueStateValue,
        numRecords: Long,
        partitionId: String?,
        id: Int?,
    ) {
        pendingStateValues.add(
            StateManager.StateForCheckpointWithPartitionId(state, partitionId, numRecords, id)
        )
    }

    @Synchronized
    override fun reset() {
        currentStateValue = null
        pendingStateValues.clear()
    }

    /**
     * Called by [StateManager.checkpoint] to generate the Airbyte STATE messages for the
     * checkpoint.
     *
     * The return value is either [Fresh] or [Stale] depending on whether [set] has been called
     * since the last call to [takeForCheckpoint], or not, respectively.
     *
     * [Stale] messages are simply ignored when dealing only with [Stream] feeds, however these may
     * be required when emitting Airbyte STATE messages of type GLOBAL.
     */
    @Synchronized
    fun takeForCheckpoint(): List<StateForCheckpoint> {
        val freshStates = mutableListOf<StateForCheckpoint>()
        // Check if there is a pending state value or not.
        // If not, then set() HASN'T been called since the last call to takeForCheckpoint(),
        // because set() can only accept non-null state values.
        //
        // This means that there is nothing worth checkpointing for this particular feed.
        // In that case, exit early with the current state value.
        pendingStateValues.ifEmpty {
            return listOf(Stale(currentStateValue))
        }
        pendingStateValues.forEach {
            val freshStateValue: OpaqueStateValue = it.pendingState
            val currentPartitionId: String? = it.partitionId
            // Update current state value.
            currentStateValue = freshStateValue
            // This point is reached in the case where there is a pending state value.
            // This means that set() HAS been called since the last call to takeForCheckpoint().
            //
            // Keep a copy of the total number of records registered in all calls to set() since the
            // last call to takeForCheckpoint(), this number will be returned.
            val freshNumRecords: Long = it.pendingNumRecords
            val currentId: Int? = it.id
            freshStates.add(Fresh(freshStateValue, freshNumRecords, currentPartitionId, currentId))
        }

        // Reset the pending states, which will be overwritten by the next call to set().
        pendingStateValues.clear()

        // Return the latest state value as well as the total number of records seen since the
        // last call to takeForCheckpoint().
        return freshStates
    }
}

/** Return value type for [BaseStateManager.takeForCheckpoint]. */
private sealed interface StateForCheckpoint {
    val opaqueStateValue: OpaqueStateValue?
    val numRecords: Long
    val partitionId: String?
    val id: Int?
}

/**
 * [StateForCheckpoint] implementation for when [StateManagerScopedToFeed.set] has been called since
 * the last call to [BaseStateManager.takeForCheckpoint].
 */
private data class Fresh(
    override val opaqueStateValue: OpaqueStateValue,
    override val numRecords: Long,
    override val partitionId: String?,
    override val id: Int?,
) : StateForCheckpoint

/**
 * [StateForCheckpoint] implementation for when [StateManagerScopedToFeed.set] has NOT been called
 * since the last call to [BaseStateManager.takeForCheckpoint].
 */
private data class Stale(
    override val opaqueStateValue: OpaqueStateValue?,
) : StateForCheckpoint {
    override val numRecords: Long
        get() = 0L
    override val id: Int?
        get() = null
    override val partitionId: String?
        get() = null
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

    /**
     * Builds for each stream queues of [Fresh] states, if there are pending, and a map of [Stale]
     * states.
     */
    private fun collectStatesForCheckpoints(
        pendingFreshStates: MutableMap<StreamIdentifier, ArrayDeque<StateForCheckpoint>>,
        staleStates: MutableMap<StreamIdentifier, StateForCheckpoint>
    ) {
        // ensure that all streams have at least stale checkpoint
        // if a fresh state happens to be pending for a stream, add to fresh queue
        streamStateManagers.keys.forEach { streamId ->
            while (staleStates.containsKey(streamId).not()) {
                streamStateManagers[streamId]!!.takeForCheckpoint().forEach { stateForCheckpoint ->
                    when (stateForCheckpoint) {
                        is Fresh ->
                            pendingFreshStates
                                .computeIfAbsent(streamId) { ArrayDeque() }
                                .add(stateForCheckpoint)
                        is Stale -> staleStates[streamId] = stateForCheckpoint
                    }
                }
            }
        }
    }
    fun checkpoint(): List<AirbyteStateMessage>? {

        var shouldCheckpoint = false
        var totalNumRecords = 0L
        // CDC partitions emit a single checkpoint
        val globalStateForCheckpoint: StateForCheckpoint = takeForCheckpoint().last()
        totalNumRecords += globalStateForCheckpoint.numRecords
        if (globalStateForCheckpoint is Fresh) shouldCheckpoint = true
        val stateMessages = mutableListOf<AirbyteStateMessage>()
        val multipleStreamsState = mutableListOf<MutableList<AirbyteStreamState>>()
        val recordCounts = mutableListOf<Long>()
        val pendingFreshStates = mutableMapOf<StreamIdentifier, ArrayDeque<StateForCheckpoint>>()
        val staleStates = mutableMapOf<StreamIdentifier, StateForCheckpoint>()
        collectStatesForCheckpoints(pendingFreshStates, staleStates)

        if (pendingFreshStates.isNotEmpty()) shouldCheckpoint = true

        if (!shouldCheckpoint) {
            return null
        }

        // The following loop is building the stream states for all pending stream states.
        // We need to collect at least one set of stale states to emit a global state message
        // When no stream is checkpointing.
        do {
            val streamStates = mutableListOf<AirbyteStreamState>()

            for (streamID in streamStateManagers.keys) {
                val streamStateForCheckpoint: StateForCheckpoint =
                    pendingFreshStates[streamID]?.removeFirstOrNull() ?: staleStates[streamID]!!
                totalNumRecords += streamStateForCheckpoint.numRecords
                streamStates.add(
                    AirbyteStreamState()
                        .withStreamDescriptor(streamID.asProtocolStreamDescriptor())
                        .withStreamState(
                            when (streamStateForCheckpoint.opaqueStateValue?.isNull) {
                                null,
                                true -> Jsons.objectNode()
                                false -> streamStateForCheckpoint.opaqueStateValue
                                        ?: Jsons.objectNode()
                            }
                        )
                        // Only add id and partition_id if they are not null (stdio mode
                        // compatibility).
                        .apply {
                            streamStateForCheckpoint.id?.let { id ->
                                withAdditionalProperty("id", id)
                            }
                        }
                        .apply {
                            streamStateForCheckpoint.partitionId?.let { partitionId ->
                                withAdditionalProperty("partition_id", partitionId)
                            }
                        },
                )
            }
            multipleStreamsState.add(streamStates)
            recordCounts.add(totalNumRecords)
            totalNumRecords = 0L
        } while (pendingFreshStates.any { it.value.isNotEmpty() })

        // Build a global state message for each set of stream states.
        multipleStreamsState.zip(recordCounts).forEach { (streamsState, recordCount) ->
            val airbyteGlobalState =
                AirbyteGlobalState()
                    .withSharedState(globalStateForCheckpoint.opaqueStateValue)
                    .withStreamStates(streamsState)

            val stateMessage =
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                    .withGlobal(airbyteGlobalState)
                    .withSourceStats(AirbyteStateStats().withRecordCount(recordCount.toDouble()))
                    // Only partition_id if not null (stdio mode compatibility).
                    // id is added before being sent to wire in FeedReader.maybeCheckpoint().
                    // As global state may be checkpointed multiple times, we use a unique id for
                    // each checkpoint.
                    .apply {
                        globalStateForCheckpoint.partitionId?.let { partitionId ->
                            withAdditionalProperty("partition_id", partitionId)
                        }
                    }
            stateMessages.add(stateMessage)
        }
        return stateMessages
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
    fun checkpoint(): List<AirbyteStateMessage>? {
        val streamStatesForCheckpoint: List<StateForCheckpoint> = takeForCheckpoint()
        if (
            streamStatesForCheckpoint.filter { it is Stale }.size == streamStatesForCheckpoint.size
        ) {
            return null
        }
        val stateMessages: MutableList<AirbyteStateMessage> = mutableListOf<AirbyteStateMessage>()
        streamStatesForCheckpoint.forEach {
            val airbyteStreamState =
                AirbyteStreamState()
                    .withStreamDescriptor(feed.id.asProtocolStreamDescriptor())
                    .withStreamState(it.opaqueStateValue ?: Jsons.objectNode())
            val airbyteStateMessage =
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                    .withStream(airbyteStreamState)
                    .withSourceStats(AirbyteStateStats().withRecordCount(it.numRecords.toDouble()))
                    // Only add id and partition_id if they are not null (stdio mode compatibility).
                    .apply { it.id?.let { id -> withAdditionalProperty("id", id) } }
                    .apply {
                        it.partitionId?.let { partitionId ->
                            withAdditionalProperty("partition_id", partitionId)
                        }
                    }
            stateMessages.add(airbyteStateMessage)
        }

        return stateMessages.ifEmpty {
            null // If no state messages were created, return null.
        }
    }
}
// }
