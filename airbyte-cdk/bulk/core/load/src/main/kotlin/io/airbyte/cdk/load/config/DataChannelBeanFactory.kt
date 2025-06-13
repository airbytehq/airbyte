/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.config

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.file.ClientSocket
import io.airbyte.cdk.load.file.DataChannelReader
import io.airbyte.cdk.load.file.JSONLDataChannelReader
import io.airbyte.cdk.load.file.ProtobufDataChannelReader
import io.airbyte.cdk.load.file.SocketInputFlow
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.DestinationMessageFactory
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.FileTransferQueueMessage
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.StrictPartitionedQueue
import io.airbyte.cdk.load.pipeline.InputPartitioner
import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.state.PipelineEventBookkeepingRouter
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.task.internal.HeartbeatTask
import io.airbyte.cdk.load.task.internal.InputConsumerTask
import io.airbyte.cdk.load.task.internal.ReservingDeserializingInputFlow
import io.airbyte.cdk.load.util.deserializeToClass
import io.airbyte.cdk.load.write.LoadStrategy
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.File
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow

typealias PipelineInputEvent = PipelineEvent<StreamKey, DestinationRecordRaw>

/** Responsible for all wiring that depends directly on the data channel medium. */
@Factory
class DataChannelBeanFactory {
    private val log = KotlinLogging.logger {}

    /**
     * The medium uses for the data channel. One of [DataChannelMedium]. This value is determined
     * here in order to have a single source of truth.
     */
    @Singleton
    @Named("dataChannelMedium")
    fun dataChannelMedium(
        @Value("\${airbyte.destination.core.data-channel.medium}")
        dataChannelMedium: DataChannelMedium
    ): DataChannelMedium {
        log.info { "Using data channel medium $dataChannelMedium" }
        return dataChannelMedium
    }

    @Singleton
    @Named("dataChannelSocketPaths")
    fun dataChannelSocketPaths(
        @Value("\${airbyte.destination.core.data-channel.socket-paths}") socketPaths: List<String>
    ): List<String> {
        log.info { "Using socket paths $socketPaths" }
        return socketPaths
    }

    @Singleton
    @Named("dataChannelFormat")
    fun dataChannelFormat(
        @Value("\${airbyte.destination.core.data-channel.format}")
        dataChannelFormat: DataChannelFormat
    ): DataChannelFormat {
        log.info { "Using data channel format $dataChannelFormat" }
        return dataChannelFormat
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
        dataChannelMedium: DataChannelMedium,
        @Named("dataChannelSocketPaths") dataChannelSocketPaths: List<String>,
    ): Int {
        return when (dataChannelMedium) {
            DataChannelMedium.STDIO -> {
                if (isFileTransfer) 1 else loadStrategy?.inputPartitions ?: 1
            }
            DataChannelMedium.SOCKET -> {
                dataChannelSocketPaths.size
            }
        }
    }

    @Singleton
    @Named("numDataChannels")
    fun numDataChannels(
        @Named("dataChannelMedium") dataChannelMedium: DataChannelMedium,
        @Named("numInputPartitions") numInputPartitions: Int
    ): Int {
        return when (dataChannelMedium) {
            DataChannelMedium.STDIO -> 1
            DataChannelMedium.SOCKET -> numInputPartitions
        }
    }

    @Singleton
    @Named("markEndOfStreamAtEndOfSync")
    fun markEndOfStreamAtEndOfSync(
        @Named("dataChannelMedium") dataChannelMedium: DataChannelMedium
    ): Boolean {
        // For STDIO, we mark the end of stream when we get the message.
        // For SOCKETs, source will only send end-of-stream on one socket (which is useless),
        // so to avoid constantly syncing across threads we'll mark end of stream at the end of
        // the sync. This means that the last checkpoint might not be flushed until end-of-sync,
        // but it's possible that this happens already anyway.
        return dataChannelMedium == DataChannelMedium.SOCKET
    }

    @Singleton
    @Named("logPerNRecords")
    fun logPerNRecords(
        @Value("\${airbyte.destination.core.data-channel.log-per-n-records:100000}")
        logPerNRecords: Long
    ): Long {
        log.info { "Logging every $logPerNRecords records" }
        return logPerNRecords
    }

    /**
     * Because sockets uses multiple threads, state must be kept coherent by
     * - matching AirbyteRecords to AirbyteStateMessages by CheckpointId (from
     * `additionalProperties['partition_id']`)
     * - ordering AirbyteStateMessages by CheckpointIndex (from `additionalProperties['id']`)
     */
    @Singleton
    @Named("requireCheckpointIdOnRecordAndKeyOnState")
    fun requireCheckpointIdOnRecord(
        @Named("dataChannelMedium") dataChannelMedium: DataChannelMedium
    ): Boolean = dataChannelMedium == DataChannelMedium.SOCKET

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
    @Requires(property = "airbyte.destination.core.data-channel.medium", value = "STDIO")
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

    @Singleton
    fun dataChannelReader(
        @Named("dataChannelFormat") dataChannelFormat: DataChannelFormat,
        destinationMessageFactory: DestinationMessageFactory,
        @Named("dataChannelMedium") dataChannelMedium: DataChannelMedium,
    ) =
        when (dataChannelFormat) {
            DataChannelFormat.JSONL -> JSONLDataChannelReader(destinationMessageFactory)
            DataChannelFormat.PROTOBUF -> {
                check(dataChannelMedium == DataChannelMedium.SOCKET) {
                    "PROTOBUF data channel format is only supported for SOCKETS medium."
                }
                ProtobufDataChannelReader(destinationMessageFactory)
            }
            else ->
                throw IllegalArgumentException(
                    "Unsupported data channel format: $dataChannelFormat"
                )
        }

    /**
     * The input flows from which the pipeline will read. The size of the array will always be equal
     * to @Named("numInputPartitions")[numInputPartitions].
     */
    @Singleton
    @Named("dataChannelInputFlows")
    fun dataChannelInputFlows(
        catalog: DestinationCatalog,
        @Named("globalMemoryManager") queueMemoryManager: ReservationManager,
        @Named("_pipelineInputQueue")
        pipelineInputQueue: PartitionedQueue<PipelineInputEvent>? = null,
        dataChannelMedium: DataChannelMedium,
        dataChannelReader: DataChannelReader,
        pipelineEventBookkeepingRouter: PipelineEventBookkeepingRouter,
        @Named("dataChannelSocketPaths") socketPaths: List<String>,
        @Value("\${airbyte.destination.core.data-channel.socket-buffer-size-bytes}")
        bufferSizeBytes: Int,
        @Value("\${airbyte.destination.core.data-channel.socket-connection-timeout-ms}")
        socketConnectionTimeoutMs: Long,
        @Named("logPerNRecords") logPerNRecords: Long,
    ): Array<Flow<PipelineInputEvent>> {
        return when (dataChannelMedium) {
            DataChannelMedium.STDIO -> {
                check(pipelineInputQueue != null) {
                    "Pipeline input queue is not initialized. This should never happen in STDIO mode."
                }
                return pipelineInputQueue.asOrderedFlows()
            }
            DataChannelMedium.SOCKET -> {
                socketPaths
                    .map { path ->
                        val socket =
                            ClientSocket(
                                path,
                                bufferSizeBytes,
                                connectTimeoutMs = socketConnectionTimeoutMs,
                            )
                        SocketInputFlow(
                            catalog,
                            socket,
                            dataChannelReader,
                            pipelineEventBookkeepingRouter,
                            queueMemoryManager,
                            logPerNRecords
                        )
                    }
                    .toTypedArray()
            }
        }
    }

    /**
     * Sockets will be implemented as cold flows, so a task is only needed for reading from STDIO.
     */
    @Singleton
    @Requires(property = "airbyte.destination.core.data-channel.medium", value = "STDIO")
    fun stdioInputConsumerTask(
        catalog: DestinationCatalog,
        inputFlow: ReservingDeserializingInputFlow,
        @Named("_pipelineInputQueue")
        pipelineInputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>? =
            null,
        partitioner: InputPartitioner,
        pipelineEventBookkeepingRouter: PipelineEventBookkeepingRouter,
    ): InputConsumerTask {
        check(pipelineInputQueue != null) {
            "Pipeline input queue is not initialized. This should never happen in STDIO mode."
        }
        return InputConsumerTask(
            catalog,
            inputFlow,
            pipelineInputQueue,
            partitioner,
            pipelineEventBookkeepingRouter
        )
    }

    /**
     * Because sockets will be implemented as cold flows, the heartbeat behavior will have to reside
     * in the readers.
     */
    @Singleton
    @Requires(property = "airbyte.destination.core.data-channel.medium", value = "STDIO")
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

    @Singleton
    fun namespaceMapper(
        @Named("dataChannelMedium") dataChannelMedium: DataChannelMedium,
        @Value("\${airbyte.destination.core.mappers.namespace-mapping-config-path}")
        namespaceMappingConfigPath: String
    ): NamespaceMapper {
        when (dataChannelMedium) {
            DataChannelMedium.STDIO -> {
                // Source is effectively "identity." In STDIO mode, we just take
                // what we're given.
                log.info {
                    "Going to use the given source value: ${NamespaceDefinitionType.SOURCE} for namespace"
                }
                return NamespaceMapper(NamespaceDefinitionType.SOURCE)
            }
            DataChannelMedium.SOCKET -> {
                log.info { "In a SOCKET scenario. Using alternate version of the NamespaceMapper" }
                val config =
                    File(namespaceMappingConfigPath)
                        .readText(Charsets.UTF_8)
                        .deserializeToClass(NamespaceMappingConfig::class.java)
                return NamespaceMapper(
                    namespaceDefinitionType = config.namespaceDefinitionType,
                    namespaceFormat = config.namespaceFormat,
                    streamPrefix = config.streamPrefix
                )
            }
        }
    }
}
