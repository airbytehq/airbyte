/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.config

import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.AggregateStoreFactory
import io.airbyte.cdk.load.dataflow.finalization.StreamCompletionTracker
import io.airbyte.cdk.load.dataflow.input.DataFlowPipelineInputFlow
import io.airbyte.cdk.load.dataflow.input.JsonDestinationMessageInputFlow
import io.airbyte.cdk.load.dataflow.input.ProtobufDestinationMessageInputFlow
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowPipeline
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStage
import io.airbyte.cdk.load.dataflow.pipeline.PipelineCompletionHandler
import io.airbyte.cdk.load.dataflow.stages.AggregateStage
import io.airbyte.cdk.load.dataflow.state.StateHistogramStore
import io.airbyte.cdk.load.dataflow.state.StateKeyClient
import io.airbyte.cdk.load.dataflow.state.StateStore
import io.airbyte.cdk.load.dataflow.state.stats.CommittedStatsStore
import io.airbyte.cdk.load.dataflow.state.stats.EmittedStatsStore
import io.airbyte.cdk.load.file.ClientSocket
import io.airbyte.cdk.load.file.ProtobufDataChannelReader
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationMessageFactory
import io.airbyte.cdk.load.message.ProtocolMessageDeserializer
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.flow.Flow

/**
 * Conditionally creates input streams / sockets based on channel medium, then wires up a pipeline
 * to each input with separate aggregate stores but shared state stores.
 */
@Factory
class InputBeanFactory {
    @Requires(property = "airbyte.destination.core.data-channel.medium", value = "SOCKET")
    @Singleton
    fun sockets(
        @Value("\${airbyte.destination.core.data-channel.socket-paths}") socketPaths: List<String>,
        @Value("\${airbyte.destination.core.data-channel.socket-buffer-size-bytes}")
        bufferSizeBytes: Int,
        @Value("\${airbyte.destination.core.data-channel.socket-connection-timeout-ms}")
        socketConnectionTimeoutMs: Long,
    ): List<ClientSocket> =
        socketPaths.map {
            ClientSocket(
                socketPath = it,
                bufferSizeBytes = bufferSizeBytes,
                connectTimeoutMs = socketConnectionTimeoutMs,
            )
        }

    @Requires(property = "airbyte.destination.core.data-channel.medium", value = "SOCKET")
    @Named("inputStreams")
    @Singleton
    fun socketStreams(
        sockets: List<ClientSocket>,
    ) = ConnectorInputStreams(sockets.map(ClientSocket::openInputStream))

    @Requires(property = "airbyte.destination.core.data-channel.medium", value = "STDIO")
    @Named("inputStreams")
    @Singleton
    fun stdInStreams() = ConnectorInputStreams(listOf(System.`in`))

    @Named("messageFlows")
    @Singleton
    fun messageFlows(
        @Named("inputStreams") inputStreams: ConnectorInputStreams,
        @Value("\${airbyte.destination.core.data-channel.format}")
        dataChannelFormat: DataChannelFormat,
        deserializer: ProtocolMessageDeserializer,
        destinationMessageFactory: DestinationMessageFactory,
    ): List<Flow<DestinationMessage>> =
        when (dataChannelFormat) {
            DataChannelFormat.JSONL ->
                inputStreams.map {
                    JsonDestinationMessageInputFlow(
                        inputStream = it,
                        deserializer = deserializer,
                    )
                }
            DataChannelFormat.PROTOBUF -> {
                val protobufDataChannelReader = ProtobufDataChannelReader(destinationMessageFactory)
                inputStreams.map {
                    ProtobufDestinationMessageInputFlow(
                        inputStream = it,
                        reader = protobufDataChannelReader,
                    )
                }
            }
        }

    @Singleton
    fun inputFlows(
        @Named("messageFlows") messageFlows: List<Flow<DestinationMessage>>,
        stateStore: StateStore,
        stateKeyClient: StateKeyClient,
        completionTracker: StreamCompletionTracker,
        statsStore: EmittedStatsStore,
    ): List<DataFlowPipelineInputFlow> =
        messageFlows.map {
            DataFlowPipelineInputFlow(
                inputFlow = it,
                stateStore = stateStore,
                stateKeyClient = stateKeyClient,
                completionTracker = completionTracker,
                statsStore = statsStore,
            )
        }

    @Singleton
    fun aggregateStoreFactory(
        aggFactory: AggregateFactory,
        aggregatePublishingConfig: AggregatePublishingConfig,
    ) =
        AggregateStoreFactory(
            aggFactory,
            aggregatePublishingConfig,
        )

    @Singleton
    fun pipes(
        inputFlows: List<DataFlowPipelineInputFlow>,
        @Named("parse") parse: DataFlowStage,
        @Named("flush") flush: DataFlowStage,
        @Named("state") state: DataFlowStage,
        aggregateStoreFactory: AggregateStoreFactory,
        stateHistogramStore: StateHistogramStore,
        statsStore: CommittedStatsStore,
        aggregatePublishingConfig: AggregatePublishingConfig,
        @Named("aggregationDispatcher") aggregationDispatcher: CoroutineDispatcher,
        @Named("flushDispatcher") flushDispatcher: CoroutineDispatcher,
    ): List<DataFlowPipeline> =
        inputFlows.map {
            val aggStore = aggregateStoreFactory.make()
            val aggregate = AggregateStage(aggStore)
            val completionHandler =
                PipelineCompletionHandler(
                    aggStore,
                    stateHistogramStore,
                    statsStore,
                )

            DataFlowPipeline(
                input = it,
                parse = parse,
                aggregate = aggregate,
                flush = flush,
                state = state,
                completionHandler = completionHandler,
                aggregatePublishingConfig = aggregatePublishingConfig,
                aggregationDispatcher = aggregationDispatcher,
                flushDispatcher = flushDispatcher,
            )
        }
}
