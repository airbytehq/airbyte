package io.airbyte.cdk.load.config

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.FileTransferQueueMessage
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.StrictPartitionedQueue
import io.airbyte.cdk.load.pipeline.InputPartitioner
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TaskGroup
import io.airbyte.cdk.load.task.internal.HeartbeatTask
import io.airbyte.cdk.load.task.internal.InputConsumerTask
import io.airbyte.cdk.load.task.internal.ReservingDeserializingInputFlow
import io.airbyte.cdk.load.write.LoadStrategy
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow

typealias InputEventType = PipelineEvent<StreamKey, DestinationRecordRaw>

/**
 * Specific factory for setting up the input flows and their private dependencies. Has two
 * public targets
 *
 * [inputFlows]: Flows of incoming records, agnostic of data channel medium
 * [inputConsumerTask]: [Task] responsible for populating the flows (if any)
 */
@Factory
class DataChannelMediumBeanFactory {
    /**
     * PRIVATE: Do not use outside the factory.
     *
     * A record queue containing all streams, partitioned, for use in routing from smaller-
     * cardinality input sources (ie, STDIN pipe.)
     *
     * NOTE: The platform is sending STDOUT to both connectors to mean: "use standard streams"
     */
    @Singleton
    @Named("_pipelineInputQueue")
    @Requires(property = "airbyte.destination.core.data-channel-medium", value = "STDOUT")
    fun pipelineInputQueue(
        loadStrategy: LoadStrategy,
        @Named("isFileTransfer") isFileTransfer: Boolean = false,
    ): PartitionedQueue<InputEventType> {
        return StrictPartitionedQueue(
            Array(if (isFileTransfer) 1 else loadStrategy.inputPartitions) {
                ChannelMessageQueue(Channel(Channel.UNLIMITED))
            }
        )
    }

    /**
     * Input flow(s) consumed by the LoadPipeline.
     */
    @Singleton
    @Named("inputFlows")
    @Requires(property = "airbyte.destination.core.data-channel-medium", value = "STDOUT")
    fun inputFlows(
        @Named("_pipelineInputQueue") pipelineInputQueue:
        PartitionedQueue<InputEventType>,
    ): Array<Flow<InputEventType>> = pipelineInputQueue.asOrderedFlows()

    /**
      * Task that populates the input flows (if any)
      */
    @Singleton
    @Requires(property = "airbyte.destination.core.data-channel-medium", value = "STDOUT")
    @Named("inputConsumerTasks")
    fun inputConsumerTasks(
        config: DestinationConfiguration,
        catalog: DestinationCatalog,
        stdinInputFlow: ReservingDeserializingInputFlow,
        checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>>,
        syncManager: SyncManager,
        @Named("fileMessageQueueLegacy")
        fileTransferQueue: MessageQueue<FileTransferQueueMessage>,
        @Named("_pipelineInputQueue")
        pipelineInputQueue: PartitionedQueue<InputEventType>,
        partitioner: InputPartitioner,
        openStreamQueue: QueueWriter<DestinationStream>,
        @Named("recordsWithFilesQueue") fileQueue: PartitionedQueue<InputEventType>
    ): TaskGroup {
        val inputConsumerTask = InputConsumerTask(
            catalog,
            stdinInputFlow,
            checkpointQueue,
            syncManager,
            fileTransferQueue,
            pipelineInputQueue,
            partitioner,
            openStreamQueue,
            fileQueue,
        )
        val heartbeatTask = HeartbeatTask(
            config,
            pipelineInputQueue
        )

        return object : TaskGroup {
            override suspend fun start(launcher: suspend (Task) -> Unit) {
                launcher(inputConsumerTask)
                launcher(heartbeatTask)
            }
        }
    }
}
