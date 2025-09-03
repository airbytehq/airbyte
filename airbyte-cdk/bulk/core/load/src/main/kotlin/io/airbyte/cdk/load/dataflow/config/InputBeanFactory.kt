/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.config

import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.AggregateStore
import io.airbyte.cdk.load.dataflow.finalization.StreamCompletionTracker
import io.airbyte.cdk.load.dataflow.input.DataFlowPipelineInputFlow
import io.airbyte.cdk.load.dataflow.input.DestinationMessageInputFlow
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowPipeline
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStage
import io.airbyte.cdk.load.dataflow.pipeline.PipelineCompletionHandler
import io.airbyte.cdk.load.dataflow.stages.AggregateStage
import io.airbyte.cdk.load.dataflow.state.StateHistogramStore
import io.airbyte.cdk.load.dataflow.state.StateKeyClient
import io.airbyte.cdk.load.dataflow.state.StateStore
import io.airbyte.cdk.load.file.ClientSocket
import io.airbyte.cdk.load.message.ProtocolMessageDeserializer
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.InputStream

@Factory
class InputBeanFactory {
    @Requires(property = "airbyte.destination.core.data-channel.medium", value = "SOCKET")
    @Singleton
    @Named("inputStreams")
    fun socketStreams(
        @Value("\${airbyte.destination.core.data-channel.socket-paths}") socketPaths: List<String>,
        @Value("\${airbyte.destination.core.data-channel.socket-buffer-size-bytes}")
        bufferSizeBytes: Int,
        @Value("\${airbyte.destination.core.data-channel.socket-connection-timeout-ms}")
        socketConnectionTimeoutMs: Long,
    ): List<InputStream> {
        return socketPaths.map {
            ClientSocket(
                    socketPath = it,
                    bufferSizeBytes = bufferSizeBytes,
                    connectTimeoutMs = socketConnectionTimeoutMs,
                )
                .openInputStream()
        }
    }

    @Requires(property = "airbyte.destination.core.data-channel.medium", value = "STDIO")
    @Singleton
    @Named("inputStreams")
    fun stdInStreams(): List<InputStream> = listOf(System.`in`)

    @Singleton
    fun messageFlows(
        @Named("inputStreams") inputStreams: List<InputStream>,
        deserializer: ProtocolMessageDeserializer,
    ): List<DestinationMessageInputFlow> =
        inputStreams.map {
            DestinationMessageInputFlow(
                inputStream = it,
                deserializer = deserializer,
            )
        }

    @Singleton
    fun inputFlows(
        messageFlows: List<DestinationMessageInputFlow>,
        stateStore: StateStore,
        stateKeyClient: StateKeyClient,
        completionTracker: StreamCompletionTracker,
    ): List<DataFlowPipelineInputFlow> =
        messageFlows.map {
            DataFlowPipelineInputFlow(
                inputFlow = it,
                stateStore = stateStore,
                stateKeyClient = stateKeyClient,
                completionTracker = completionTracker,
            )
        }

    @Singleton
    fun pipes(
        inputFlows: List<DataFlowPipelineInputFlow>,
        @Named("parse") parse: DataFlowStage,
        @Named("flush") flush: DataFlowStage,
        @Named("state") state: DataFlowStage,
        aggFactory: AggregateFactory,
        stateHistogramStore: StateHistogramStore,
        memoryAndParallelismConfig: MemoryAndParallelismConfig,
    ): List<DataFlowPipeline> =
        inputFlows.map {
            val aggStore = AggregateStore(aggFactory, memoryAndParallelismConfig)
            val aggregate = AggregateStage(aggStore)
            val completionHandler = PipelineCompletionHandler(aggStore, stateHistogramStore)

            DataFlowPipeline(
                input = it,
                parse = parse,
                aggregate = aggregate,
                flush = flush,
                state = state,
                completionHandler = completionHandler,
                memoryAndParallelismConfig = memoryAndParallelismConfig,
            )
        }
}
