/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.state

import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.message.DestinationStateMessage
import io.airbyte.cdk.message.MessageConverter
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.core.util.clhm.ConcurrentLinkedHashMap
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentLinkedQueue
import java.util.concurrent.atomic.AtomicReference
import java.util.function.Consumer

/**
 * Interface for state management. Should accept stream and global state, as well as requests to
 * flush all data-sufficient states.
 */
interface StateManager<K, T> {
    fun addStreamState(key: K, index: Long, stateMessage: T)
    fun addGlobalState(keyIndexes: List<Pair<K, Long>>, stateMessage: T)
    fun flushStates()
}

/**
 * Message-type agnostic streams state manager.
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
abstract class StreamsStateManager<T, U>() : StateManager<DestinationStream, T> {
    private val log = KotlinLogging.logger {}

    abstract val catalog: DestinationCatalog
    abstract val streamsManager: StreamsManager
    abstract val outputFactory: MessageConverter<T, U>
    abstract val outputConsumer: Consumer<U>

    data class GlobalState<T>(
        val streamIndexes: List<Pair<DestinationStream, Long>>,
        val stateMessage: T
    )

    private val stateIsGlobal: AtomicReference<Boolean?> = AtomicReference(null)
    private val streamStates:
        ConcurrentHashMap<DestinationStream, ConcurrentLinkedHashMap<Long, T>> =
        ConcurrentHashMap()
    private val globalStates: ConcurrentLinkedQueue<GlobalState<T>> = ConcurrentLinkedQueue()

    override fun addStreamState(key: DestinationStream, index: Long, stateMessage: T) {
        if (stateIsGlobal.updateAndGet { it == true } != false) {
            throw IllegalStateException("Global state cannot be mixed with non-global state")
        }

        streamStates.compute(key) { _, indexToMessage ->
            val map =
                if (indexToMessage == null) {
                    // If the map doesn't exist yet, build it.
                    ConcurrentLinkedHashMap.Builder<Long, T>().maximumWeightedCapacity(1000).build()
                } else {
                    if (indexToMessage.isNotEmpty()) {
                        // Make sure the messages are coming in order
                        val oldestIndex = indexToMessage.ascendingKeySet().first()
                        if (oldestIndex > index) {
                            throw IllegalStateException(
                                "State message received out of order ($oldestIndex before $index)"
                            )
                        }
                    }
                    indexToMessage
                }
            // Actually add the message
            map[index] = stateMessage
            map
        }

        log.info { "Added state for stream: $key at index: $index" }
    }

    // TODO: Is it an error if we don't get all the streams every time?
    override fun addGlobalState(keyIndexes: List<Pair<DestinationStream, Long>>, stateMessage: T) {
        if (stateIsGlobal.updateAndGet { it != false } != true) {
            throw IllegalStateException("Global state cannot be mixed with non-global state")
        }

        val head = globalStates.peek()
        if (head != null) {
            val keyIndexesByStream = keyIndexes.associate { it.first to it.second }
            head.streamIndexes.forEach {
                if (keyIndexesByStream[it.first]!! < it.second) {
                    throw IllegalStateException("Global state message received out of order")
                }
            }
        }

        globalStates.add(GlobalState(keyIndexes, stateMessage))
        log.info { "Added global state with stream indexes: $keyIndexes" }
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
        while (!globalStates.isEmpty()) {
            val head = globalStates.peek()
            val allStreamsPersisted =
                head.streamIndexes.all { (stream, index) ->
                    streamsManager.getManager(stream).areRecordsPersistedUntil(index)
                }
            if (allStreamsPersisted) {
                globalStates.poll()
                val outMessage = outputFactory.from(head.stateMessage)
                outputConsumer.accept(outMessage)
            } else {
                break
            }
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
                    val outMessage = outputFactory.from(stateMessage)
                    outputConsumer.accept(outMessage)
                } else {
                    break
                }
            }
        }
    }
}

@Singleton
class DefaultStateManager(
    override val catalog: DestinationCatalog,
    override val streamsManager: StreamsManager,
    override val outputFactory: MessageConverter<DestinationStateMessage, AirbyteMessage>,
    override val outputConsumer: Consumer<AirbyteMessage>
) : StreamsStateManager<DestinationStateMessage, AirbyteMessage>()
