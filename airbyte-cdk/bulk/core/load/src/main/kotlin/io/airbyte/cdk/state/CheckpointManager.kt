/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.state

import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.message.CheckpointMessage
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
 * Interface for checkpoint management. Should accept stream and global checkpoints, as well as
 * requests to flush all data-sufficient checkpoints.
 */
interface CheckpointManager<K, T> {
    fun addStreamCheckpoint(key: K, index: Long, checkpointMessage: T)
    fun addGlobalCheckpoint(keyIndexes: List<Pair<K, Long>>, checkpointMessage: T)
    suspend fun flushReadyCheckpointMessages()
}

/**
 * Message-type agnostic streams checkpoint manager.
 *
 * Accepts global and stream checkpoints, and enforces that stream and global checkpoints are not
 * mixed. Determines ready checkpoints by querying the StreamsManager for the checkpoint of the
 * record index range associated with each checkpoint message.
 *
 * TODO: Force flush on a configured schedule
 *
 * TODO: Ensure that checkpoint is flushed at the end, and require that all checkpoints be flushed
 * before the destination can succeed.
 */
abstract class StreamsCheckpointManager<T, U>() : CheckpointManager<DestinationStream, T> {
    private val log = KotlinLogging.logger {}

    abstract val catalog: DestinationCatalog
    abstract val streamsManager: StreamsManager
    abstract val outputFactory: MessageConverter<T, U>
    abstract val outputConsumer: Consumer<U>

    data class GlobalCheckpoint<T>(
        val streamIndexes: List<Pair<DestinationStream, Long>>,
        val checkpointMessage: T
    )

    private val checkpointsAreGlobal: AtomicReference<Boolean?> = AtomicReference(null)
    private val streamCheckpoints:
        ConcurrentHashMap<DestinationStream, ConcurrentLinkedHashMap<Long, T>> =
        ConcurrentHashMap()
    private val globalCheckpoints: ConcurrentLinkedQueue<GlobalCheckpoint<T>> =
        ConcurrentLinkedQueue()

    override fun addStreamCheckpoint(key: DestinationStream, index: Long, checkpointMessage: T) {
        if (checkpointsAreGlobal.updateAndGet { it == true } != false) {
            throw IllegalStateException(
                "Global checkpoints cannot be mixed with non-global checkpoints"
            )
        }

        streamCheckpoints.compute(key) { _, indexToMessage ->
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
                                "Checkpoint message received out of order ($oldestIndex before $index)"
                            )
                        }
                    }
                    indexToMessage
                }
            // Actually add the message
            map[index] = checkpointMessage
            map
        }

        log.info { "Added checkpoint for stream: $key at index: $index" }
    }

    // TODO: Is it an error if we don't get all the streams every time?
    override fun addGlobalCheckpoint(
        keyIndexes: List<Pair<DestinationStream, Long>>,
        checkpointMessage: T
    ) {
        if (checkpointsAreGlobal.updateAndGet { it != false } != true) {
            throw IllegalStateException(
                "Global checkpoint cannot be mixed with non-global checkpoints"
            )
        }

        val head = globalCheckpoints.peek()
        if (head != null) {
            val keyIndexesByStream = keyIndexes.associate { it.first to it.second }
            head.streamIndexes.forEach {
                if (keyIndexesByStream[it.first]!! < it.second) {
                    throw IllegalStateException("Global checkpoint message received out of order")
                }
            }
        }

        globalCheckpoints.add(GlobalCheckpoint(keyIndexes, checkpointMessage))
        log.info { "Added global checkpoint with stream indexes: $keyIndexes" }
    }

    override suspend fun flushReadyCheckpointMessages() {
        /*
           Iterate over the checkpoints in order, evicting each that passes
           the persistence check. If a checkpoint is not persisted, then
           we can break the loop since the checkpoints are ordered. For global
           checkpoints, all streams must be persisted up to the checkpoint.
        */
        when (checkpointsAreGlobal.get()) {
            null -> log.info { "No checkpoints to flush" }
            true -> flushGlobalCheckpoints()
            false -> flushStreamCheckpoints()
        }
    }

    private fun flushGlobalCheckpoints() {
        while (!globalCheckpoints.isEmpty()) {
            val head = globalCheckpoints.peek()
            val allStreamsPersisted =
                head.streamIndexes.all { (stream, index) ->
                    streamsManager.getManager(stream).areRecordsPersistedUntil(index)
                }
            if (allStreamsPersisted) {
                globalCheckpoints.poll()
                val outMessage = outputFactory.from(head.checkpointMessage)
                outputConsumer.accept(outMessage)
            } else {
                break
            }
        }
    }

    private fun flushStreamCheckpoints() {
        for (stream in catalog.streams) {
            val manager = streamsManager.getManager(stream)
            val streamCheckpoints = streamCheckpoints[stream] ?: return
            for (index in streamCheckpoints.keys) {
                if (manager.areRecordsPersistedUntil(index)) {
                    val checkpointMessage =
                        streamCheckpoints.remove(index)
                            ?: throw IllegalStateException("Checkpoint not found for index: $index")
                    log.info { "Flushing checkpoint for stream: $stream at index: $index" }
                    val outMessage = outputFactory.from(checkpointMessage)
                    outputConsumer.accept(outMessage)
                } else {
                    break
                }
            }
        }
    }
}

@Singleton
class DefaultCheckpointManager(
    override val catalog: DestinationCatalog,
    override val streamsManager: StreamsManager,
    override val outputFactory: MessageConverter<CheckpointMessage, AirbyteMessage>,
    override val outputConsumer: Consumer<AirbyteMessage>
) : StreamsCheckpointManager<CheckpointMessage, AirbyteMessage>()
