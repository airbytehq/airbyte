/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationFileStreamComplete
import io.airbyte.cdk.load.message.DestinationFileStreamIncomplete
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.DestinationRecordStreamIncomplete
import io.airbyte.cdk.load.message.DestinationStreamAffinedMessage
import io.airbyte.cdk.load.message.FileTransferQueueEndOfStream
import io.airbyte.cdk.load.message.FileTransferQueueMessage
import io.airbyte.cdk.load.message.FileTransferQueueRecord
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.GlobalCheckpointWrapped
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpointWrapped
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.Undefined
import io.airbyte.cdk.load.pipeline.InputPartitioner
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.OnSyncFailureOnly
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.util.use
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import java.util.concurrent.ConcurrentHashMap

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
class InputConsumerTask(
    private val catalog: DestinationCatalog,
    private val inputFlow: ReservingDeserializingInputFlow,
    val checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>>,
    private val syncManager: SyncManager,
    @Named("fileMessageQueue")
    private val fileTransferQueue: MessageQueue<FileTransferQueueMessage>,
    @Named("pipelineInputQueue")
    private val pipelineInputQueue:
        PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    private val partitioner: InputPartitioner,
    private val openStreamQueue: QueueWriter<DestinationStream>
) : Task {
    private val log = KotlinLogging.logger {}

    override val terminalCondition: TerminalCondition = OnSyncFailureOnly

    private val unopenedStreams = ConcurrentHashMap(catalog.streams.associateBy { it.descriptor })

    private suspend fun handleRecordForPipeline(
        reserved: Reserved<DestinationStreamAffinedMessage>,
    ) {
        val stream = reserved.value.stream
        unopenedStreams.remove(stream.descriptor)?.let {
            log.info { "Saw first record for stream $stream; awaiting setup complete" }
            syncManager.awaitSetupComplete()
            // Note, since we're not spilling to disk, there is nothing to do with
            // any records before initialization is complete, so we'll wait here
            // for it to finish.
            log.info { "Setup complete, starting stream $stream" }
            openStreamQueue.publish(it)
            syncManager.getOrAwaitStreamLoader(stream.descriptor)
            log.info { "Initialization for stream $stream complete" }
        }
        val manager = syncManager.getStreamManager(stream.descriptor)
        when (val message = reserved.value) {
            is DestinationRecord -> {
                val record = message.asDestinationRecordRaw()
                manager.incrementReadCount()
                val pipelineMessage =
                    PipelineMessage(
                        mapOf(manager.getCurrentCheckpointId() to 1),
                        StreamKey(stream.descriptor),
                        record,
                        postProcessingCallback = { reserved.release() }
                    )
                val partition = partitioner.getPartition(record, pipelineInputQueue.partitions)
                pipelineInputQueue.publish(pipelineMessage, partition)
            }
            is DestinationRecordStreamComplete -> {
                manager.markEndOfStream(true)
                log.info { "Read COMPLETE for stream $stream" }
                pipelineInputQueue.broadcast(PipelineEndOfStream(stream.descriptor))
                reserved.release()
            }
            is DestinationRecordStreamIncomplete -> {
                manager.markEndOfStream(false)
                log.info { "Read INCOMPLETE for stream $stream" }
                pipelineInputQueue.broadcast(PipelineEndOfStream(stream.descriptor))
                reserved.release()
            }
            is DestinationFile -> {
                val index = manager.incrementReadCount()
                val checkpointId = manager.getCurrentCheckpointId()
                // destinationTaskLauncher.handleFile(stream, message, index)
                fileTransferQueue.publish(
                    FileTransferQueueRecord(stream, message, index, checkpointId)
                )
            }
            is DestinationFileStreamComplete -> {
                reserved.release() // safe because multiple calls conflate
                manager.markEndOfStream(true)
                fileTransferQueue.publish(FileTransferQueueEndOfStream(stream))
            }
            is DestinationFileStreamIncomplete ->
                throw IllegalStateException("File stream $stream failed upstream, cannot continue.")
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
                val checkpointId = manager.getCurrentCheckpointId()
                val (_, countSinceLast) = manager.markCheckpoint()
                val messageWithCount =
                    checkpoint.withDestinationStats(CheckpointMessage.Stats(countSinceLast))
                checkpointQueue.publish(
                    reservation.replace(
                        StreamCheckpointWrapped(sizeBytes, stream, checkpointId, messageWithCount)
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
                        is DestinationStreamAffinedMessage -> {
                            handleRecordForPipeline(reserved.replace(message))
                        }
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
            fileTransferQueue.close()
            pipelineInputQueue.close()
        }
    }
}
