/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.pipeline

import io.airbyte.cdk.load.dataflow.config.MemoryAndParallelismConfig
import io.airbyte.cdk.load.dataflow.stages.AggregateStage
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.buffer
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.onCompletion
import kotlinx.coroutines.flow.transform

class DataFlowPipeline(
    private val input: Flow<DataFlowStageIO>,
    private val parse: DataFlowStage,
    private val aggregate: AggregateStage,
    private val flush: DataFlowStage,
    private val state: DataFlowStage,
    private val completionHandler: PipelineCompletionHandler,
    private val memoryAndParallelismConfig: MemoryAndParallelismConfig,
) {
    suspend fun run() {
        input
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
