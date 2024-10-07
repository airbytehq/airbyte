/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationConfiguration
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.state.MemoryManager
import io.airbyte.cdk.state.Reserved
import io.airbyte.cdk.state.SyncManager
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking

/** A publishing interface for writing messages to a message queue. */
interface MessageQueueWriter<T : Any> {
    suspend fun publish(message: T, sizeBytes: Long)
}

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
class DestinationMessageQueueWriter(
    private val config: DestinationConfiguration,
    private val catalog: DestinationCatalog,
    private val recordQueueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationRecordWrapped>>,
    private val checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>>,
    private val syncManager: SyncManager,
    systemMemoryManager: MemoryManager
) : MessageQueueWriter<DestinationMessage> {
    private val queueReservation = runBlocking {
        systemMemoryManager.reserveRatio(config.maxMessageQueueMemoryUsageRatio, this)
    }
    private val memoryManager = queueReservation.getReservationManager()

    private suspend fun <T : Sized> reserve(sized: T) =
        memoryManager.reserveBlocking(
            (sized.sizeBytes * config.estimatedRecordMemoryOverheadRatio).toLong(),
            sized
        )

    /**
     * Deserialize and route the message to the appropriate channel.
     *
     * NOTE: Not thread-safe! Only a single writer should publish to the queue.
     */
    override suspend fun publish(message: DestinationMessage, sizeBytes: Long) {
        when (message) {
            /* If the input message represents a record. */
            is DestinationStreamAffinedMessage -> {
                val manager = syncManager.getStreamManager(message.stream)
                when (message) {
                    /* If a data record */
                    is DestinationRecord -> {
                        val wrapped =
                            StreamRecordWrapped(
                                index = manager.countRecordIn(),
                                sizeBytes = sizeBytes,
                                record = message
                            )
                        recordQueueSupplier.get(message.stream).publish(reserve(wrapped))
                    }

                    /* If an end-of-stream marker. */
                    is DestinationStreamComplete,
                    is DestinationStreamIncomplete -> {
                        val wrapped = StreamCompleteWrapped(index = manager.markEndOfStream())
                        val queue = recordQueueSupplier.get(message.stream)
                        queue.publish(memoryManager.reserveBlocking(0L, wrapped))
                        queue.close()
                        if (
                            catalog.streams.all {
                                syncManager.getStreamManager(it.descriptor).endOfStreamRead()
                            }
                        ) {
                            checkpointQueue.close()
                        }
                    }
                }
            }
            is CheckpointMessage -> {
                when (message) {
                    /**
                     * For a stream state message, mark the checkpoint and add the message with
                     * index and count to the state manager. Also, add the count to the destination
                     * stats.
                     */
                    is StreamCheckpoint -> {
                        val stream = message.checkpoint.stream
                        val manager = syncManager.getStreamManager(stream)
                        val (currentIndex, countSinceLast) = manager.markCheckpoint()
                        val messageWithCount =
                            message.withDestinationStats(CheckpointMessage.Stats(countSinceLast))
                        checkpointQueue.publish(
                            reserve(
                                StreamCheckpointWrapped(
                                    sizeBytes,
                                    stream,
                                    currentIndex,
                                    messageWithCount
                                )
                            )
                        )
                    }
                    /**
                     * For a global state message, collect the index per stream, but add the total
                     * count to the destination stats.
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
                            message.withDestinationStats(CheckpointMessage.Stats(totalCount))
                        val streamIndexes =
                            streamWithIndexAndCount.map { it.first.descriptor to it.second }
                        checkpointQueue.publish(
                            reserve(
                                GlobalCheckpointWrapped(sizeBytes, streamIndexes, messageWithCount)
                            )
                        )
                    }
                }
            }
            is Undefined -> {} // Do nothing
        }
    }
}
