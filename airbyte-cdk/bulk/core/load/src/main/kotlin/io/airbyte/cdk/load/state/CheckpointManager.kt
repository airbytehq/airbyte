/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.util.use
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import io.micronaut.core.util.clhm.ConcurrentLinkedHashMap
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentLinkedQueue
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import java.util.function.Consumer
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

/**
 * Interface for checkpoint management. Should accept stream and global checkpoints, as well as
 * requests to flush all data-sufficient checkpoints.
 */
interface CheckpointManager<K, T> {
    suspend fun addStreamCheckpoint(key: K, index: Long, checkpointMessage: T)
    suspend fun addGlobalCheckpoint(keyIndexes: List<Pair<K, Long>>, checkpointMessage: T)
    suspend fun flushReadyCheckpointMessages()
    suspend fun getLastSuccessfulFlushTimeMs(): Long
    suspend fun getNextCheckpointIndexes(): Map<K, Long>
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
abstract class StreamsCheckpointManager<T> : CheckpointManager<DestinationStream.Descriptor, T> {

    private val log = KotlinLogging.logger {}
    private val flushLock = Mutex()
    protected val lastFlushTimeMs = AtomicLong(0L)

    abstract val catalog: DestinationCatalog
    abstract val syncManager: SyncManager
    abstract val outputConsumer: suspend (T) -> Unit
    abstract val timeProvider: TimeProvider

    data class GlobalCheckpoint<T>(
        val streamIndexes: List<Pair<DestinationStream.Descriptor, Long>>,
        val checkpointMessage: T
    )

    private val checkpointsAreGlobal: AtomicReference<Boolean?> = AtomicReference(null)
    private val streamCheckpoints:
        ConcurrentHashMap<DestinationStream.Descriptor, ConcurrentLinkedHashMap<Long, T>> =
        ConcurrentHashMap()
    private val globalCheckpoints: ConcurrentLinkedQueue<GlobalCheckpoint<T>> =
        ConcurrentLinkedQueue()

    override suspend fun addStreamCheckpoint(
        key: DestinationStream.Descriptor,
        index: Long,
        checkpointMessage: T
    ) {
        flushLock.withLock {
            if (checkpointsAreGlobal.updateAndGet { it == true } != false) {
                throw IllegalStateException(
                    "Global checkpoints cannot be mixed with non-global checkpoints"
                )
            }

            streamCheckpoints.compute(key) { _, indexToMessage ->
                val map =
                    if (indexToMessage == null) {
                        // If the map doesn't exist yet, build it.
                        ConcurrentLinkedHashMap.Builder<Long, T>()
                            .maximumWeightedCapacity(1000)
                            .build()
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
    }

    // TODO: Is it an error if we don't get all the streams every time?
    override suspend fun addGlobalCheckpoint(
        keyIndexes: List<Pair<DestinationStream.Descriptor, Long>>,
        checkpointMessage: T
    ) {
        flushLock.withLock {
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
                        throw IllegalStateException(
                            "Global checkpoint message received out of order"
                        )
                    }
                }
            }

            globalCheckpoints.add(GlobalCheckpoint(keyIndexes, checkpointMessage))
            log.info { "Added global checkpoint with stream indexes: $keyIndexes" }
        }
    }

    override suspend fun flushReadyCheckpointMessages() {
        flushLock.withLock {
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
    }

    private suspend fun flushGlobalCheckpoints() {
        while (!globalCheckpoints.isEmpty()) {
            val head = globalCheckpoints.peek()
            val allStreamsPersisted =
                head.streamIndexes.all { (stream, index) ->
                    syncManager.getStreamManager(stream).areRecordsPersistedUntil(index)
                }
            if (allStreamsPersisted) {
                globalCheckpoints.poll()
                sendMessage(head.checkpointMessage)
            } else {
                break
            }
        }
    }

    private suspend fun flushStreamCheckpoints() {
        for (stream in catalog.streams) {
            val manager = syncManager.getStreamManager(stream.descriptor)
            val streamCheckpoints = streamCheckpoints[stream.descriptor] ?: return
            for (index in streamCheckpoints.keys) {
                if (manager.areRecordsPersistedUntil(index)) {
                    val checkpointMessage =
                        streamCheckpoints.remove(index)
                            ?: throw IllegalStateException("Checkpoint not found for index: $index")
                    log.info { "Flushing checkpoint for stream: $stream at index: $index" }
                    sendMessage(checkpointMessage)
                } else {
                    break
                }
            }
        }
    }

    private suspend fun sendMessage(checkpointMessage: T) {
        lastFlushTimeMs.set(timeProvider.currentTimeMillis())
        outputConsumer.invoke(checkpointMessage)
    }

    override suspend fun getLastSuccessfulFlushTimeMs(): Long =
        // Return inside the lock to ensure the value reflects flushes in progress
        flushLock.withLock { lastFlushTimeMs.get() }

    override suspend fun getNextCheckpointIndexes(): Map<DestinationStream.Descriptor, Long> {
        flushLock.withLock {
            return when (checkpointsAreGlobal.get()) {
                null -> {
                    emptyMap()
                }
                true -> {
                    val head = globalCheckpoints.peek()
                    head?.streamIndexes?.associate { it } ?: emptyMap()
                }
                false -> {
                    streamCheckpoints
                        .mapValues { it.value.ascendingKeySet().firstOrNull() }
                        .filterValues { it != null }
                        .mapValues { it.value!! }
                }
            }
        }
    }
}

@Singleton
@Secondary
class DefaultCheckpointManager(
    override val catalog: DestinationCatalog,
    override val syncManager: SyncManager,
    override val outputConsumer: suspend (Reserved<CheckpointMessage>) -> Unit,
    override val timeProvider: TimeProvider
) : StreamsCheckpointManager<Reserved<CheckpointMessage>>() {
    init {
        lastFlushTimeMs.set(timeProvider.currentTimeMillis())
    }
}

@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "message is guaranteed to be non-null by Kotlin's type system"
)
@Singleton
@Secondary
class FreeingCheckpointConsumer(private val consumer: Consumer<AirbyteMessage>) :
    suspend (Reserved<CheckpointMessage>) -> Unit {
    override suspend fun invoke(message: Reserved<CheckpointMessage>) {
        message.use {
            val outMessage = it.value.asProtocolMessage()
            consumer.accept(outMessage)
        }
    }
}
