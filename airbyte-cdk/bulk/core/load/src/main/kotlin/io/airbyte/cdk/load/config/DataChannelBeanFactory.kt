/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.config

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.FileTransferQueueMessage
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.StrictPartitionedQueue
import io.airbyte.cdk.load.pipeline.InputPartitioner
import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.internal.HeartbeatTask
import io.airbyte.cdk.load.task.internal.InputConsumerTask
import io.airbyte.cdk.load.task.internal.ReservingDeserializingInputFlow
import io.airbyte.cdk.load.write.LoadStrategy
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow

typealias PipelineInputEvent = PipelineEvent<StreamKey, DestinationRecordRaw>

/** Responsible for all wiring that depends directly on the data channel medium. */
@Factory
class DataChannelBeanFactory {
    /**
     * The medium uses for the data channel. One of [DataChannelMedium]. This value is determined
     * here in order to have a single source of truth.
     */
    @Singleton
    @Named("dataChannelMedium")
    fun dataChannelMedium(
        @Value("\${airbyte.destination.core.data-channel-medium}")
        dataChannelMedium: DataChannelMedium
    ): DataChannelMedium {
        return dataChannelMedium
    }

    /**
     * The number of input partitions used by the pipeline. For STDIO syncs, this is the number of
     * partitions to which the input stream is split. For SOCKETS syncs, this will be the number of
     * socket flows.
     */
    @Singleton
    @Named("numInputPartitions")
    fun numInputPartitions(
        loadStrategy: LoadStrategy? = null,
        @Named("isFileTransfer") isFileTransfer: Boolean = false,
    ): Int {
        return if (isFileTransfer) 1 else loadStrategy?.inputPartitions ?: 1
    }

    /**
     * PRIVATE: Do not use outside this factory.
     *
     * A record queue containing all streams, partitioned, for use in routing from smaller-
     * cardinality input sources (ie, STDIN pipe.)
     *
     * NOTE: The platform is sending STDOUT to both connectors to mean: "use standard streams"
     */
    @Singleton
    @Named("_pipelineInputQueue")
    @Requires(property = "airbyte.destination.core.data-channel-medium", value = "STDIO")
    fun pipelineInputQueue(
        @Named("numInputPartitions") numInputPartitions: Int,
    ): PartitionedQueue<PipelineInputEvent> {
        return StrictPartitionedQueue(
            Array(numInputPartitions) { ChannelMessageQueue(Channel(Channel.UNLIMITED)) }
        )
    }

    // DEPRECATED: Legacy file transfer.
    @Singleton
    @Named("fileMessageQueue")
    fun fileMessageQueue(
        config: DestinationConfiguration,
    ): MultiProducerChannel<FileTransferQueueMessage> {
        val channel = Channel<FileTransferQueueMessage>(config.batchQueueDepth)
        // There is only a single producer (InputConsumerTask) and there should only ever be one.
        // (Sockets will not support legacy file transfer.) There is likely no need for a multi-
        // producer channel, but this code is going to be thrown away soon anyway.
        return MultiProducerChannel(1, channel, "fileMessageQueue")
    }

    /**
     * The input flows from which the pipeline will read. The size of the array will always be equal
     * to @Named("numInputPartitions")[numInputPartitions].
     */
    @Singleton
    @Named("dataChannelInputFlows")
    fun dataChannelInputFlows(
        @Named("_pipelineInputQueue")
        pipelineInputQueue: PartitionedQueue<PipelineInputEvent>? = null,
        @Named("dataChannelMedium") dataChannelMedium: DataChannelMedium
    ): Array<Flow<PipelineInputEvent>> {
        when (dataChannelMedium) {
            DataChannelMedium.STDIO -> {
                check(pipelineInputQueue != null) {
                    "Pipeline input queue is not initialized. This should never happen in STDIO mode."
                }
                return pipelineInputQueue.asOrderedFlows()
            }
            DataChannelMedium.SOCKETS ->
                throw NotImplementedError("Socket data channel medium is not implemented yet.")
        }
    }

    /**
     * Sockets will be implemented as cold flows, so a task is only needed for reading from STDIO.
     */
    @Singleton
    @Requires(property = "airbyte.destination.core.data-channel-medium", value = "STDIO")
    fun stdioInputConsumerTask(
        catalog: DestinationCatalog,
        inputFlow: ReservingDeserializingInputFlow,
        checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>>,
        syncManager: SyncManager,
        @Named("fileMessageQueue") fileTransferQueue: MessageQueue<FileTransferQueueMessage>,
        @Named("_pipelineInputQueue")
        pipelineInputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>? =
            null,
        partitioner: InputPartitioner,
        openStreamQueue: QueueWriter<DestinationStream>
    ): InputConsumerTask {
        check(pipelineInputQueue != null) {
            "Pipeline input queue is not initialized. This should never happen in STDIO mode."
        }
        return InputConsumerTask(
            catalog,
            inputFlow,
            checkpointQueue,
            syncManager,
            fileTransferQueue,
            pipelineInputQueue,
            partitioner,
            openStreamQueue
        )
    }

    /**
     * Because sockets will be implemented as cold flows, the heartbeat behavior will have to reside
     * in the readers.
     */
    @Singleton
    @Requires(property = "airbyte.destination.core.data-channel-medium", value = "STDIO")
    fun stdioHeartbeatTask(
        @Named("_pipelineInputQueue")
        pipelineInputQueue: PartitionedQueue<PipelineInputEvent>? = null,
        config: DestinationConfiguration,
        checkpointManager: CheckpointManager<*>,
    ): HeartbeatTask {
        check(pipelineInputQueue != null) {
            "Pipeline input queue is not initialized. This should never happen in STDIO mode."
        }
        return HeartbeatTask(config, pipelineInputQueue, checkpointManager)
    }
}
