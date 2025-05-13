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
import io.airbyte.cdk.load.state.PipelineEventBookkeeper
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.OnSyncFailureOnly
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.util.use
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.flow.fold

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
    private val syncManager: SyncManager,
    private val pipelineInputQueue:
        PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    private val partitioner: InputPartitioner,
    private val pipelineEventBookkeeper: PipelineEventBookkeeper
) : Task {
    private val log = KotlinLogging.logger {}

    override val terminalCondition: TerminalCondition = OnSyncFailureOnly

    private suspend fun handleRecordForPipeline(
        reserved: Reserved<DestinationStreamAffinedMessage>,
        unopenedStreams: MutableSet<DestinationStream.Descriptor>,
    ) {
        val pipelineEvent = pipelineEventBookkeeper.handleStreamMessage(
            reserved.value,
            postProcessingCallback = { reserved.release() },
            unopenedStreams
        )
        when (pipelineEvent) {
            is PipelineMessage -> {
                val partition = partitioner.getPartition(pipelineEvent.value, pipelineInputQueue.partitions)
                pipelineInputQueue.publish(pipelineEvent, partition)
            }
            is PipelineEndOfStream -> {
                reserved.release()
                pipelineInputQueue.broadcast(pipelineEvent)
            }
            else -> reserved.release()
        }
    }

    /**
     * Deserialize and route the message to the appropriate channel.
     *
     * NOTE: Not thread-safe! Only a single writer should publish to the queue.
     */
    override suspend fun execute() {
        log.info { "Starting consuming messages from the input flow" }
        val unopenedStreams = catalog.streams.map { it.descriptor }.toMutableSet()
        pipelineInputQueue.use {
            pipelineEventBookkeeper.use {
                inputFlow.fold(unopenedStreams) { unopenedStreams, (_, reserved) ->
                    when (val message = reserved.value) {
                        is DestinationStreamAffinedMessage ->
                            handleRecordForPipeline(reserved.replace(message), unopenedStreams)
                        is CheckpointMessage ->
                            pipelineEventBookkeeper.handleCheckpoint(reserved.replace(message))
                        is Undefined ->
                            log.warn { "Unhandled message: $message" }
                    }
                    unopenedStreams
                }
            }
        }
    }
}
