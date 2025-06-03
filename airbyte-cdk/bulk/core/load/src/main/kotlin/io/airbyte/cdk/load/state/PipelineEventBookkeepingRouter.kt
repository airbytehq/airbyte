/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.config.PipelineInputEvent
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationFileStreamComplete
import io.airbyte.cdk.load.message.DestinationFileStreamIncomplete
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.DestinationRecordStreamIncomplete
import io.airbyte.cdk.load.message.DestinationStreamAffinedMessage
import io.airbyte.cdk.load.message.FileTransferQueueEndOfStream
import io.airbyte.cdk.load.message.FileTransferQueueMessage
import io.airbyte.cdk.load.message.FileTransferQueueRecord
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.GlobalCheckpointWrapped
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpointWrapped
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.util.CloseableCoroutine
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger

/**
 * The stdio and socket input channel differ in subtle and critical ways
 * - record-wise, sockets are cold flows, stdio publishes to a partitioned channel
 * - sockets receive checkpointId on the record, stdio infers from state message order
 * - speed will receive complete/incomplete on all sockets (no need to publish)
 * - because they are flows, sockets don't need memory management; the buffer can serve as the
 * ```
 *    backpressure scheme (note: the exception to this is for file transfer, which forwards the
 *    record after handling the file; and of course obviously for state)
 * ```
 * These differences might diverge/converge as we tune (ie, because of lock contention with multiple
 * sockets, or because the socket pattern ends up working for stdio as well). For now, since the
 * main difference is what is done with the pipeline events, we'll consolidate bookkeeping into a
 * single class that yields events from DestinationMessage(s). CheckpointIds can be inferred iff the
 * record does not provide one.
 */
@Singleton
class PipelineEventBookkeepingRouter(
    private val catalog: DestinationCatalog,
    private val syncManager: SyncManager,
    private val checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>>,
    private val openStreamQueue: QueueWriter<DestinationStream>,
    private val fileTransferQueue: MessageQueue<FileTransferQueueMessage>,
    @Named("numDataChannels") numDataChannels: Int,
) : CloseableCoroutine {
    private val log = KotlinLogging.logger {}

    private val clientCount = AtomicInteger(numDataChannels)

    // With sockets, multiple reader threads run in parallel. Source will send end-of-stream to all
    // threads. This ensures that only the last one to recieve end-of-stream actually closes the
    // stream. (However all will forward end-of-stream to cause their thread to flush and finish
    // work.)
    private val streamCompletionCountdownLatches =
        ConcurrentHashMap(
            catalog.streams.associate { it.descriptor to AtomicInteger(numDataChannels) }
        )

    init {
        log.info { "Creating bookkeeping router for $numDataChannels data channels" }
    }

    suspend fun handleStreamMessage(
        message: DestinationStreamAffinedMessage,
        postProcessingCallback: suspend () -> Unit = {},
        unopenedStreams: MutableSet<DestinationStream.Descriptor>
    ): PipelineInputEvent {
        val stream = message.stream
        if (unopenedStreams.remove(stream.descriptor)) {
            log.info { "Saw first record for stream ${stream.descriptor}; awaiting setup complete" }
            syncManager.awaitSetupComplete()
            log.info { "Setup complete, starting stream ${stream.descriptor}" }
            openStreamQueue.publish(stream)
            syncManager.getOrAwaitStreamLoader(stream.descriptor)
            log.info { "Initialization for stream ${stream.descriptor} complete" }
        }
        val manager = syncManager.getStreamManager(stream.descriptor)

        return when (message) {
            is DestinationRecord -> {
                val record = message.asDestinationRecordRaw()
                manager.incrementReadCount()
                manager.incrementByteCount(record.serializedSizeBytes)
                // Fallback to the manager if the record doesn't have a checkpointId
                // This should only happen in STDIO mode.
                val checkpointId =
                    record.checkpointId ?: manager.inferNextCheckpointKey().checkpointId
                PipelineMessage(
                    mapOf(checkpointId to Pair(1, record.serializedSizeBytes)),
                    StreamKey(stream.descriptor),
                    record,
                    postProcessingCallback
                )
            }
            is DestinationRecordStreamComplete -> {
                log.info { "Read COMPLETE for stream ${stream.descriptor}" }
                if (streamCompletionCountdownLatches[stream.descriptor]!!.decrementAndGet() == 0) {
                    manager.markEndOfStream(true)
                }
                PipelineEndOfStream(stream.descriptor)
            }
            is DestinationRecordStreamIncomplete -> {
                log.info { "Read INCOMPLETE for stream ${stream.descriptor}" }
                if (streamCompletionCountdownLatches[stream.descriptor]!!.decrementAndGet() == 0) {
                    manager.markEndOfStream(false)
                }
                PipelineEndOfStream(stream.descriptor)
            }

            // DEPRECATED: Legacy file transfer
            is DestinationFile -> {
                val index = manager.incrementReadCount()
                val checkpointId = manager.inferNextCheckpointKey().checkpointId
                fileTransferQueue.publish(
                    FileTransferQueueRecord(stream, message, index, checkpointId)
                )
                PipelineHeartbeat()
            }
            is DestinationFileStreamComplete -> {
                manager.markEndOfStream(true)
                fileTransferQueue.publish(FileTransferQueueEndOfStream(stream))
                PipelineHeartbeat()
            }
            is DestinationFileStreamIncomplete ->
                throw IllegalStateException(
                    "File stream ${stream.descriptor} failed upstream, cannot continue."
                )
        }
    }

    suspend fun handleCheckpoint(reservation: Reserved<CheckpointMessage>) {
        when (val checkpoint = reservation.value) {
            is StreamCheckpoint -> {
                val stream = checkpoint.checkpoint.stream
                val manager = syncManager.getStreamManager(stream)
                val (checkpointKey, checkpointRecordCount) = getKeyAndCounts(checkpoint, manager)
                val messageWithCount =
                    checkpoint.withDestinationStats(CheckpointMessage.Stats(checkpointRecordCount))
                checkpointQueue.publish(
                    reservation.replace(
                        StreamCheckpointWrapped(stream, checkpointKey, messageWithCount)
                    )
                )
            }

            /** For a global state message, gather the */
            is GlobalCheckpoint -> {
                val (checkpointKey, checkpointRecordCount) =
                    if (checkpoint.checkpointKey == null) {
                        val streamWithKeyAndCount =
                            catalog.streams.map { stream ->
                                val manager = syncManager.getStreamManager(stream.descriptor)
                                getKeyAndCounts(checkpoint, manager)
                            }
                        val singleKey =
                            streamWithKeyAndCount.map { (key, _) -> key }.toSet().singleOrNull()
                        check(singleKey != null) {
                            "For global state, all streams should have the same key: $streamWithKeyAndCount"
                        }
                        val totalCounts = streamWithKeyAndCount.sumOf { (_, count) -> count }
                        Pair(singleKey, totalCounts)
                    } else {
                        Pair(checkpoint.checkpointKey!!, checkpoint.sourceStats?.recordCount ?: 0L)
                    }

                val messageWithCount =
                    checkpoint.withDestinationStats(CheckpointMessage.Stats(checkpointRecordCount))
                checkpointQueue.publish(
                    reservation.replace(GlobalCheckpointWrapped(checkpointKey, messageWithCount))
                )
            }
        }
    }

    // If the key is not on the record, assume we're expected to generate it.
    private fun getKeyAndCounts(
        checkpoint: CheckpointMessage,
        manager: StreamManager
    ): Pair<CheckpointKey, Long> {
        // If the key is not on the record, assume we're expected to generate it.
        // (Assume its presence will be appropriately enforced.)
        return if (checkpoint.checkpointKey == null) {
            val key = manager.inferNextCheckpointKey()
            val (_, countSinceLast) = manager.markCheckpoint()
            Pair(key, countSinceLast)
        } else {
            Pair(checkpoint.checkpointKey!!, checkpoint.sourceStats?.recordCount ?: 0L)
        }
    }

    override suspend fun close() {
        log.info { "Maybe closing bookkeeping router ${clientCount.get()}" }
        if (clientCount.decrementAndGet() == 0) {
            log.info { "Closing internal control channels" }
            fileTransferQueue.close()
            checkpointQueue.close()
            openStreamQueue.close()
            syncManager.markInputConsumed()
        }
    }
}
