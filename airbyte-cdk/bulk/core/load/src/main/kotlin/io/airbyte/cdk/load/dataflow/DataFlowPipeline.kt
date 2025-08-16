/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.dataflow.config.MemoryAndParallelismConfig
import io.airbyte.cdk.load.dataflow.stages.AggregateStage
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.buffer
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.onCompletion
import kotlinx.coroutines.flow.onStart
import kotlinx.coroutines.flow.transform

@Singleton
class DataFlowPipeline(
    private val input: Flow<DataFlowStageIO>,
    @Named("parse") private val parse: DataFlowStage,
    @Named("aggregate") private val aggregate: AggregateStage,
    @Named("flush") private val flush: DataFlowStage,
    @Named("state") private val state: DataFlowStage,
    private val startHandler: PipelineStartHandler,
    private val completionHandler: PipelineCompletionHandler,
    private val memoryAndParallelismConfig: MemoryAndParallelismConfig,
) {
    suspend fun run() {
        input
            .onStart { startHandler.run() }
            .map(parse::apply)
            .transform { aggregate.apply(it, this) }
            .buffer(capacity = memoryAndParallelismConfig.maxBufferedAggregates)
            .flowOn(Dispatchers.Default)
            .map(flush::apply)
            .map(state::apply)
            .onCompletion { completionHandler.apply(it) }
            .flowOn(Dispatchers.IO)
            .collect {}
    }
}
