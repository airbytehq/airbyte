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
import io.airbyte.cdk.output.OutputConsumer
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentLinkedQueue
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.delay
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

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
@Singleton
class CheckpointManager<T>(
    val catalog: DestinationCatalog,
    val syncManager: SyncManager,
    val outputConsumer: suspend (T) -> Unit,
    val timeProvider: TimeProvider,
) {
    private val log = KotlinLogging.logger {}
    private val flushLock = Mutex()
    protected val lastFlushTimeMs = AtomicLong(0L)

    data class GlobalCheckpoint<T>(
        val streamCheckpoints: List<Pair<DestinationStream.Descriptor, CheckpointId>>,
        val checkpointMessage: T
    )

    private val checkpointsAreGlobal: AtomicReference<Boolean?> = AtomicReference(null)
    private val streamCheckpoints:
        ConcurrentHashMap<
            DestinationStream.Descriptor, ConcurrentLinkedQueue<Pair<CheckpointId, T>>> =
        ConcurrentHashMap()
    private val globalCheckpoints: ConcurrentLinkedQueue<GlobalCheckpoint<T>> =
        ConcurrentLinkedQueue()
    private val lastCheckpointIdEmitted =
        ConcurrentHashMap<DestinationStream.Descriptor, CheckpointId>()

    init {
        lastFlushTimeMs.set(timeProvider.currentTimeMillis())
    }

    suspend fun addStreamCheckpoint(
        key: DestinationStream.Descriptor,
        checkpointId: CheckpointId,
        checkpointMessage: T
    ) {
        flushLock.withLock {
            if (checkpointsAreGlobal.updateAndGet { it == true } != false) {
                throw IllegalStateException(
                    "Global checkpoints cannot be mixed with non-global checkpoints"
                )
            }

            val indexedMessages: ConcurrentLinkedQueue<Pair<CheckpointId, T>> =
                streamCheckpoints.getOrPut(key) { ConcurrentLinkedQueue() }
            if (indexedMessages.isNotEmpty()) {
                // Make sure the messages are coming in order
                val (latestIndex, _) = indexedMessages.last()!!
                if (latestIndex.id > checkpointId.id) {
                    throw IllegalStateException(
                        "Checkpoint message received out of order ($latestIndex before $checkpointId)"
                    )
                }
            }
            indexedMessages.add(checkpointId to checkpointMessage)

            log.info { "Added checkpoint for stream: $key at index: $checkpointId" }
        }
    }

    // TODO: Is it an error if we don't get all the streams every time?
    suspend fun addGlobalCheckpoint(
        keyIndexes: List<Pair<DestinationStream.Descriptor, CheckpointId>>,
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
                val keyCheckpointsByStream = keyIndexes.associate { it.first to it.second }
                head.streamCheckpoints.forEach {
                    if (keyCheckpointsByStream[it.first]!!.id < it.second.id) {
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

    suspend fun flushReadyCheckpointMessages() {
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
        if (globalCheckpoints.isEmpty()) {
            log.info { "No global checkpoints to flush" }
            return
        }
        while (!globalCheckpoints.isEmpty()) {
            val head = globalCheckpoints.peek()
            val allStreamsPersisted =
                head.streamCheckpoints.all { (stream, checkpointId) ->
                    syncManager
                        .getStreamManager(stream)
                        .areRecordsPersistedUntilCheckpoint(checkpointId)
                }
            if (allStreamsPersisted) {
                log.info {
                    "Flushing global checkpoint with stream indexes: ${head.streamCheckpoints}"
                }
                validateAndSendMessage(head.checkpointMessage, head.streamCheckpoints)
                globalCheckpoints.poll() // don't remove until after we've successfully sent
            } else {
                log.info {
                    "Not flushing global checkpoint with stream indexes: ${head.streamCheckpoints}"
                }
                break
            }
        }
    }

    private suspend fun flushStreamCheckpoints() {
        val noCheckpointStreams = mutableSetOf<DestinationStream.Descriptor>()
        for (stream in catalog.streams) {

            val manager = syncManager.getStreamManager(stream.descriptor)
            val streamCheckpoints = streamCheckpoints[stream.descriptor]
            if (streamCheckpoints == null) {
                noCheckpointStreams.add(stream.descriptor)

                continue
            }
            while (true) {
                val (nextCheckpointId, nextMessage) = streamCheckpoints.peek() ?: break
                val persisted = manager.areRecordsPersistedUntilCheckpoint(nextCheckpointId)
                if (persisted) {

                    log.info {
                        "Flushing checkpoint for stream: ${stream.descriptor} at index: $nextCheckpointId"
                    }
                    validateAndSendMessage(
                        nextMessage,
                        listOf(stream.descriptor to nextCheckpointId)
                    )
                    streamCheckpoints.poll() // don't remove until after we've successfully sent
                } else {
                    log.info { "Not flushing next checkpoint for index $nextCheckpointId" }
                    break
                }
            }
        }
        if (noCheckpointStreams.isNotEmpty()) {
            log.info { "No checkpoints for streams: $noCheckpointStreams" }
        }
    }

    private suspend fun validateAndSendMessage(
        checkpointMessage: T,
        streamCheckpoints: List<Pair<DestinationStream.Descriptor, CheckpointId>>
    ) {
        streamCheckpoints.forEach { (stream, checkpointId) ->
            val lastCheckpoint = lastCheckpointIdEmitted[stream]
            if (lastCheckpoint != null && checkpointId.id < lastCheckpoint.id) {
                throw IllegalStateException(
                    "Checkpoint message for $stream emitted out of order (emitting $checkpointId after $lastCheckpoint)"
                )
            }
            lastCheckpointIdEmitted[stream] = checkpointId
        }

        lastFlushTimeMs.set(timeProvider.currentTimeMillis())
        outputConsumer.invoke(checkpointMessage)
    }

    suspend fun awaitAllCheckpointsFlushed() {
        while (true) {
            val allCheckpointsFlushed =
                flushLock.withLock {
                    globalCheckpoints.isEmpty() && streamCheckpoints.all { it.value.isEmpty() }
                }
            if (allCheckpointsFlushed) {
                log.info { "All checkpoints flushed" }
                break
            }
            log.info { "Waiting for all checkpoints to flush" }
            // Not usually a fan of busywaiting, but it's extremely unlikely we
            // get here without more than a handful of stragglers
            delay(1000L)
            flushReadyCheckpointMessages()
        }
    }
}

@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "message is guaranteed to be non-null by Kotlin's type system"
)
@Singleton
class FreeingCheckpointConsumer(private val consumer: OutputConsumer) :
    suspend (Reserved<CheckpointMessage>) -> Unit {
    override suspend fun invoke(message: Reserved<CheckpointMessage>) {
        message.use {
            val outMessage = it.value.asProtocolMessage()
            consumer.accept(outMessage)
        }
    }
}
