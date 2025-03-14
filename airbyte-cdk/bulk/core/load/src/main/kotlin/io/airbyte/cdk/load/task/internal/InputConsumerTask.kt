/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
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
import io.airbyte.cdk.load.message.DestinationStreamEvent
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.GlobalCheckpointWrapped
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpointWrapped
import io.airbyte.cdk.load.message.StreamEndEvent
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.StreamRecordEvent
import io.airbyte.cdk.load.message.Undefined
import io.airbyte.cdk.load.pipeline.InputPartitioner
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.OnSyncFailureOnly
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.task.implementor.FileTransferQueueMessage
import io.airbyte.cdk.load.util.use
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

interface InputConsumerTask : Task

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
    private val inputFlow: ReservingDeserializingInputFlow,
    private val recordQueueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationStreamEvent>>,
    val checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>>,
    private val syncManager: SyncManager,
    private val destinationTaskLauncher: DestinationTaskLauncher,
    @Named("fileMessageQueue")
    private val fileTransferQueue: MessageQueue<FileTransferQueueMessage>,

    // Required by new interface
    @Named("recordQueue")
    private val recordQueueForPipeline:
        PartitionedQueue<Reserved<PipelineEvent<StreamKey, DestinationRecordRaw>>>,
    private val loadPipeline: LoadPipeline? = null,
    private val partitioner: InputPartitioner,
    private val openStreamQueue: QueueWriter<DestinationStream>
) : InputConsumerTask {
    private val log = KotlinLogging.logger {}

    override val terminalCondition: TerminalCondition = OnSyncFailureOnly

    private val unopenedStreams = ConcurrentHashMap(catalog.streams.associateBy { it.descriptor })

    private suspend fun handleRecord(
        reserved: Reserved<DestinationStreamAffinedMessage>,
        sizeBytes: Long
    ) {
        val stream = reserved.value.stream
        val manager = syncManager.getStreamManager(stream)
        val recordQueue = recordQueueSupplier.get(stream)
        when (val message = reserved.value) {
            is DestinationRecord -> {
                val wrapped =
                    StreamRecordEvent(
                        index = manager.incrementReadCount(),
                        sizeBytes = sizeBytes,
                        payload = message.asRecordSerialized()
                    )
                recordQueue.publish(reserved.replace(wrapped))
            }
            is DestinationRecordStreamComplete -> {
                reserved.release() // safe because multiple calls conflate
                val wrapped = StreamEndEvent(index = manager.markEndOfStream(true))
                log.info { "Read COMPLETE for stream $stream" }
                recordQueue.publish(reserved.replace(wrapped))
                recordQueue.close()
            }
            is DestinationRecordStreamIncomplete -> {
                reserved.release() // safe because multiple calls conflate
                val wrapped = StreamEndEvent(index = manager.markEndOfStream(false))
                log.info { "Read INCOMPLETE for stream $stream" }
                recordQueue.publish(reserved.replace(wrapped))
                recordQueue.close()
            }
            is DestinationFile -> {
                val index = manager.incrementReadCount()
                // destinationTaskLauncher.handleFile(stream, message, index)
                fileTransferQueue.publish(FileTransferQueueMessage(stream, message, index))
            }
            is DestinationFileStreamComplete -> {
                reserved.release() // safe because multiple calls conflate
                manager.markEndOfStream(true)
                val envelope =
                    BatchEnvelope(
                        SimpleBatch(Batch.State.COMPLETE),
                        streamDescriptor = message.stream,
                    )
                destinationTaskLauncher.handleNewBatch(stream, envelope)
            }
            is DestinationFileStreamIncomplete ->
                throw IllegalStateException("File stream $stream failed upstream, cannot continue.")
        }
    }

    private suspend fun handleRecordForPipeline(
        reserved: Reserved<DestinationStreamAffinedMessage>,
    ) {
        val stream = reserved.value.stream
        unopenedStreams.remove(stream)?.let {
            log.info { "Saw first record for stream $stream; initializing" }
            // Note, since we're not spilling to disk, there is nothing to do with
            // any records before initialization is complete, so we'll wait here
            // for it to finish.
            openStreamQueue.publish(it)
            syncManager.getOrAwaitStreamLoader(stream)
            log.info { "Initialization for stream $stream complete" }
        }
        val manager = syncManager.getStreamManager(stream)
        when (val message = reserved.value) {
            is DestinationRecord -> {
                val record = message.asDestinationRecordRaw()
                manager.incrementReadCount()
                val pipelineMessage =
                    PipelineMessage(
                        mapOf(manager.getCurrentCheckpointId() to 1),
                        StreamKey(stream),
                        record
                    )
                val partition = partitioner.getPartition(record, recordQueueForPipeline.partitions)
                recordQueueForPipeline.publish(reserved.replace(pipelineMessage), partition)
            }
            is DestinationRecordStreamComplete -> {
                manager.markEndOfStream(true)
                log.info { "Read COMPLETE for stream $stream" }
                recordQueueForPipeline.broadcast(reserved.replace(PipelineEndOfStream(stream)))
                reserved.release()
            }
            is DestinationRecordStreamIncomplete -> {
                manager.markEndOfStream(false)
                log.info { "Read INCOMPLETE for stream $stream" }
                recordQueueForPipeline.broadcast(reserved.replace(PipelineEndOfStream(stream)))
                reserved.release()
            }
            is DestinationFile -> {
                val index = manager.incrementReadCount()
                // destinationTaskLauncher.handleFile(stream, message, index)
                fileTransferQueue.publish(FileTransferQueueMessage(stream, message, index))
            }
            is DestinationFileStreamComplete -> {
                reserved.release() // safe because multiple calls conflate
                manager.markEndOfStream(true)
                val envelope =
                    BatchEnvelope(
                        SimpleBatch(Batch.State.COMPLETE),
                        streamDescriptor = message.stream,
                    )
                destinationTaskLauncher.handleNewBatch(stream, envelope)
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
                val (currentIndex, countSinceLast) = manager.markCheckpoint()
                val indexOrId =
                    if (loadPipeline == null) {
                        currentIndex
                    } else {
                        checkpointId.id.toLong()
                    }
                val messageWithCount =
                    checkpoint.withDestinationStats(CheckpointMessage.Stats(countSinceLast))
                checkpointQueue.publish(
                    reservation.replace(
                        StreamCheckpointWrapped(sizeBytes, stream, indexOrId, messageWithCount)
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
                        val (currentIndex, countSinceLast) = manager.markCheckpoint()
                        val indexOrId =
                            if (loadPipeline == null) {
                                currentIndex
                            } else {
                                checkpointId.id.toLong()
                            }
                        Triple(stream, indexOrId, countSinceLast)
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
                            if (loadPipeline != null) {
                                handleRecordForPipeline(reserved.replace(message))
                            } else {
                                handleRecord(reserved.replace(message), sizeBytes)
                            }
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
            catalog.streams.forEach { recordQueueSupplier.get(it.descriptor).close() }
            fileTransferQueue.close()
            recordQueueForPipeline.close()
        }
    }
}

interface InputConsumerTaskFactory {
    fun make(
        catalog: DestinationCatalog,
        inputFlow: ReservingDeserializingInputFlow,
        recordQueueSupplier:
            MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationStreamEvent>>,
        checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>>,
        destinationTaskLauncher: DestinationTaskLauncher,
        fileTransferQueue: MessageQueue<FileTransferQueueMessage>,

        // Required by new interface
        recordQueueForPipeline:
            PartitionedQueue<Reserved<PipelineEvent<StreamKey, DestinationRecordRaw>>>,
        loadPipeline: LoadPipeline?,
        partitioner: InputPartitioner,
        openStreamQueue: QueueWriter<DestinationStream>,
    ): InputConsumerTask
}

@Singleton
@Secondary
class DefaultInputConsumerTaskFactory(
    private val syncManager: SyncManager,
) : InputConsumerTaskFactory {
    override fun make(
        catalog: DestinationCatalog,
        inputFlow: ReservingDeserializingInputFlow,
        recordQueueSupplier:
            MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationStreamEvent>>,
        checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>>,
        destinationTaskLauncher: DestinationTaskLauncher,
        fileTransferQueue: MessageQueue<FileTransferQueueMessage>,

        // Required by new interface
        recordQueueForPipeline:
            PartitionedQueue<Reserved<PipelineEvent<StreamKey, DestinationRecordRaw>>>,
        loadPipeline: LoadPipeline?,
        partitioner: InputPartitioner,
        openStreamQueue: QueueWriter<DestinationStream>,
    ): InputConsumerTask {
        return DefaultInputConsumerTask(
            catalog,
            inputFlow,
            recordQueueSupplier,
            checkpointQueue,
            syncManager,
            destinationTaskLauncher,
            fileTransferQueue,

            // Required by new interface
            recordQueueForPipeline,
            loadPipeline,
            partitioner,
            openStreamQueue,
        )
    }
}
