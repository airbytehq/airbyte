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
import jakarta.inject.Singleton

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
) : CloseableCoroutine {
    private val log = KotlinLogging.logger {}

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
                PipelineMessage(
                    mapOf(manager.getCurrentCheckpointId() to 1),
                    StreamKey(stream.descriptor),
                    record,
                    postProcessingCallback
                )
            }
            is DestinationRecordStreamComplete -> {
                manager.markEndOfStream(true)
                log.info { "Read COMPLETE for stream ${stream.descriptor}" }
                PipelineEndOfStream(stream.descriptor)
            }
            is DestinationRecordStreamIncomplete -> {
                manager.markEndOfStream(false)
                log.info { "Read INCOMPLETE for stream ${stream.descriptor}" }
                PipelineEndOfStream(stream.descriptor)
            }

            // DEPRECATED: Legacy file transfer
            is DestinationFile -> {
                val index = manager.incrementReadCount()
                val checkpointId = manager.getCurrentCheckpointId()
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
                val checkpointId = manager.getCurrentCheckpointId()
                val (_, countSinceLast) = manager.markCheckpoint()
                val messageWithCount =
                    checkpoint.withDestinationStats(CheckpointMessage.Stats(countSinceLast))
                checkpointQueue.publish(
                    reservation.replace(
                        StreamCheckpointWrapped(stream, checkpointId, messageWithCount)
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
                        val checkpointId = manager.getCurrentCheckpointId()
                        val (_, countSinceLast) = manager.markCheckpoint()
                        Triple(stream, checkpointId, countSinceLast)
                    }
                val totalCount = streamWithIndexAndCount.sumOf { it.third }
                val messageWithCount =
                    checkpoint.withDestinationStats(CheckpointMessage.Stats(totalCount))
                val streamIndexes = streamWithIndexAndCount.map { it.first.descriptor to it.second }
                checkpointQueue.publish(
                    reservation.replace(GlobalCheckpointWrapped(streamIndexes, messageWithCount))
                )
            }
        }
    }

    override suspend fun close() {
        fileTransferQueue.close()
        checkpointQueue.close()
        openStreamQueue.close()
        syncManager.markInputConsumed()
    }
}
