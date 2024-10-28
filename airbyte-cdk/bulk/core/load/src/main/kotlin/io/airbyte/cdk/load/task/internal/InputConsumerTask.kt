/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.Deserializer
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordWrapped
import io.airbyte.cdk.load.message.DestinationStreamAffinedMessage
import io.airbyte.cdk.load.message.DestinationStreamComplete
import io.airbyte.cdk.load.message.DestinationStreamIncomplete
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.GlobalCheckpointWrapped
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpointWrapped
import io.airbyte.cdk.load.message.StreamCompleteWrapped
import io.airbyte.cdk.load.message.StreamRecordWrapped
import io.airbyte.cdk.load.message.Undefined
import io.airbyte.cdk.load.state.MemoryManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.InternalScope
import io.airbyte.cdk.load.task.SyncLevel
import io.airbyte.cdk.load.util.use
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.io.InputStream
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.FlowCollector

interface InputConsumerTask : SyncLevel, InternalScope

/**
 * Routes @[DestinationStreamAffinedMessage]s by stream to the appropriate channel and @
 * [CheckpointMessage]s to the state manager.
 *
 * TODO: Handle other message types.
 */
@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "message is guaranteed to be non-null by Kotlin's type system"
)
@Singleton
@Secondary
class DefaultInputConsumerTask(
    private val catalog: DestinationCatalog,
    private val inputFlow: SizedInputFlow<Reserved<DestinationMessage>>,
    private val recordQueueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationRecordWrapped>>,
    private val checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>>,
    private val syncManager: SyncManager,
) : InputConsumerTask {
    private val log = KotlinLogging.logger {}

    private suspend fun handleRecord(
        reserved: Reserved<DestinationStreamAffinedMessage>,
        sizeBytes: Long
    ) {
        val stream = reserved.value.stream
        val manager = syncManager.getStreamManager(stream)
        val queue = recordQueueSupplier.get(stream)
        when (val message = reserved.value) {
            is DestinationRecord -> {
                val wrapped =
                    StreamRecordWrapped(
                        index = manager.countRecordIn(),
                        sizeBytes = sizeBytes,
                        record = message
                    )
                queue.publish(reserved.replace(wrapped))
            }
            is DestinationStreamComplete -> {
                reserved.release() // safe because multiple calls conflate
                val wrapped = StreamCompleteWrapped(index = manager.markEndOfStream())
                queue.publish(reserved.replace(wrapped))
                queue.close()
            }
            is DestinationStreamIncomplete ->
                throw IllegalStateException("Stream $stream failed upstream, cannot continue.")
        }
    }

    private suspend fun handleCheckpoint(
        reservation: Reserved<CheckpointMessage>,
        sizeBytes: Long
    ) {
        when (val checkpoint = reservation.value) {
            /**
             * For a stream state message, mark the checkpoint and add the message with index and
             * count to the state manager. Also, add the count to the destination stats.
             */
            is StreamCheckpoint -> {
                val stream = checkpoint.checkpoint.stream
                val manager = syncManager.getStreamManager(stream)
                val (currentIndex, countSinceLast) = manager.markCheckpoint()
                val messageWithCount =
                    checkpoint.withDestinationStats(CheckpointMessage.Stats(countSinceLast))
                checkpointQueue.publish(
                    reservation.replace(
                        StreamCheckpointWrapped(sizeBytes, stream, currentIndex, messageWithCount)
                    )
                )
            }

            /**
             * For a global state message, collect the index per stream, but add the total count to
             * the destination stats.
             */
            is GlobalCheckpoint -> {
                val streamWithIndexAndCount =
                    catalog.streams.map { stream ->
                        val manager = syncManager.getStreamManager(stream.descriptor)
                        val (currentIndex, countSinceLast) = manager.markCheckpoint()
                        Triple(stream, currentIndex, countSinceLast)
                    }
                val totalCount = streamWithIndexAndCount.sumOf { it.third }
                val messageWithCount =
                    checkpoint.withDestinationStats(CheckpointMessage.Stats(totalCount))
                val streamIndexes = streamWithIndexAndCount.map { it.first.descriptor to it.second }
                checkpointQueue.publish(
                    reservation.replace(
                        GlobalCheckpointWrapped(sizeBytes, streamIndexes, messageWithCount)
                    )
                )
            }
        }
    }

    /**
     * Deserialize and route the message to the appropriate channel.
     *
     * NOTE: Not thread-safe! Only a single writer should publish to the queue.
     */
    override suspend fun execute() {
        log.info { "Starting consuming messages from the input flow" }
        try {
            checkpointQueue.use {
                inputFlow.collect { (sizeBytes, reserved) ->
                    when (val message = reserved.value) {
                        /* If the input message represents a record. */
                        is DestinationStreamAffinedMessage ->
                            handleRecord(reserved.replace(message), sizeBytes)
                        is CheckpointMessage ->
                            handleCheckpoint(reserved.replace(message), sizeBytes)
                        is Undefined -> {
                            log.warn { "Unhandled message: $message" }
                        }
                    }
                }
            }
            syncManager.markInputConsumed()
        } finally {
            log.info { "Closing record queues" }
            catalog.streams.forEach { recordQueueSupplier.get(it.descriptor).close() }
        }
    }
}

interface SizedInputFlow<T> : Flow<Pair<Long, T>>

abstract class ReservingDeserializingInputFlow<T : Any> : SizedInputFlow<Reserved<T>> {
    val log = KotlinLogging.logger {}

    abstract val config: DestinationConfiguration
    abstract val deserializer: Deserializer<T>
    abstract val memoryManager: MemoryManager
    abstract val inputStream: InputStream

    override suspend fun collect(collector: FlowCollector<Pair<Long, Reserved<T>>>) {
        val reservation = memoryManager.reserveRatio(config.maxMessageQueueMemoryUsageRatio, this)
        val reservationManager = reservation.getReservationManager()

        log.info { "Reserved ${reservation.bytesReserved/1024}mb memory for input processing" }

        reservation.use { _ ->
            inputStream.bufferedReader().lineSequence().forEachIndexed { index, line ->
                if (line.isEmpty()) {
                    return@forEachIndexed
                }

                val lineSize = line.length.toLong()
                val estimatedSize = lineSize * config.estimatedRecordMemoryOverheadRatio
                val reserved = reservationManager.reserveBlocking(estimatedSize.toLong(), line)
                val message = deserializer.deserialize(line)
                collector.emit(Pair(lineSize, reserved.replace(message)))

                if (index % 10_000 == 0) {
                    log.info { "Processed $index lines" }
                }
            }
        }

        log.info { "Finished processing input" }
    }
}

@Singleton
class DefaultInputFlow(
    override val config: DestinationConfiguration,
    override val deserializer: Deserializer<DestinationMessage>,
    override val memoryManager: MemoryManager,
    override val inputStream: InputStream
) : ReservingDeserializingInputFlow<DestinationMessage>()
