/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.state

import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.message.AirbyteStateMessageFactory
import io.airbyte.cdk.message.DestinationStateMessage
import io.airbyte.cdk.output.OutputConsumer
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentLinkedQueue
import java.util.concurrent.atomic.AtomicReference

/**
 * Interface for state management. Should accept stream and global state, as well as requests to
 * flush all data-sufficient states.
 */
interface StateManager {
    fun addStreamState(
        stream: DestinationStream,
        index: Long,
        stateMessage: DestinationStateMessage
    )
    fun addGlobalState(
        streamIndexes: List<Pair<DestinationStream, Long>>,
        stateMessage: DestinationStateMessage
    )
    fun flushStates()
}

/**
 * Destination state manager.
 *
 * Accepts global and stream states, and enforces that stream and global state are not mixed.
 * Determines ready states by querying the StreamsManager for the state of the record index range
 * associated with each state message.
 *
 * TODO: Force flush on a configured schedule
 *
 * TODO: Ensure that state is flushed at the end, and require that all state be flushed before the
 * destination can succeed.
 */
@Singleton
class DefaultStateManager(
    private val catalog: DestinationCatalog,
    private val streamsManager: StreamsManager,
    private val stateMessageFactory: AirbyteStateMessageFactory,
    private val outputConsumer: OutputConsumer
) : StateManager {
    private val log = KotlinLogging.logger {}

    data class GlobalState(
        val streamIndexes: List<Pair<DestinationStream, Long>>,
        val stateMessage: DestinationStateMessage
    )

    private val stateIsGlobal: AtomicReference<Boolean?> = AtomicReference(null)
    private val streamStates:
        ConcurrentHashMap<DestinationStream, LinkedHashMap<Long, DestinationStateMessage>> =
        ConcurrentHashMap()
    private val globalStates: ConcurrentLinkedQueue<GlobalState> = ConcurrentLinkedQueue()

    override fun addStreamState(
        stream: DestinationStream,
        index: Long,
        stateMessage: DestinationStateMessage
    ) {
        if (stateIsGlobal.getAndSet(false) != false) {
            throw IllegalStateException("Global state cannot be mixed with non-global state")
        }

        val streamStates = streamStates.getOrPut(stream) { LinkedHashMap() }
        streamStates[index] = stateMessage
        log.info { "Added state for stream: $stream at index: $index" }
    }

    override fun addGlobalState(
        streamIndexes: List<Pair<DestinationStream, Long>>,
        stateMessage: DestinationStateMessage
    ) {
        if (stateIsGlobal.getAndSet(true) != true) {
            throw IllegalStateException("Global state cannot be mixed with non-global state")
        }

        globalStates.add(GlobalState(streamIndexes, stateMessage))
        log.info { "Added global state with stream indexes: $streamIndexes" }
    }

    override fun flushStates() {
        /*
           Iterate over the states in order, evicting each that passes
           the persistence check. If a state is not persisted, then
           we can break the loop since the states are ordered. For global
           states, all streams must be persisted up to the checkpoint.
        */
        when (stateIsGlobal.get()) {
            null -> log.info { "No states to flush" }
            true -> flushGlobalStates()
            false -> flushStreamStates()
        }
    }

    private fun flushGlobalStates() {
        if (globalStates.isEmpty()) {
            return
        }

        val head = globalStates.peek()
        val allStreamsPersisted =
            head.streamIndexes.all { (stream, index) ->
                streamsManager.getManager(stream).areRecordsPersistedUntil(index)
            }
        if (allStreamsPersisted) {
            globalStates.poll()
            val outMessage = stateMessageFactory.fromDestinationStateMessage(head.stateMessage)
            outputConsumer.accept(outMessage)
        }
    }

    private fun flushStreamStates() {
        for (stream in catalog.streams) {
            val manager = streamsManager.getManager(stream)
            val streamStates = streamStates[stream] ?: return
            for (index in streamStates.keys) {
                if (manager.areRecordsPersistedUntil(index)) {
                    val stateMessage =
                        streamStates.remove(index)
                            ?: throw IllegalStateException("State not found for index: $index")
                    log.info { "Flushing state for stream: $stream at index: $index" }
                    val outMessage = stateMessageFactory.fromDestinationStateMessage(stateMessage)
                    outputConsumer.accept(outMessage)
                } else {
                    break
                }
            }
        }
    }
}
