/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.dataflow.stages.AggregateStage
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.buffer
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.onCompletion
import kotlinx.coroutines.flow.transform

@Singleton
class DataFlowPipeline(
    private val input: Flow<DataFlowStageIO>,
    @Named("parse") private val parse: DataFlowStage,
    @Named("aggregate") private val aggregate: AggregateStage,
    @Named("flush") private val flush: DataFlowStage,
    @Named("state") private val state: DataFlowStage,
    private val completionHandler: PipelineCompletionHandler,
) {
    suspend fun run() {
        input
            .map(parse::apply)
            .transform { aggregate.apply(it, this) }
            .buffer(capacity = 5)
            .map(flush::apply)
            .map(state::apply)
            .onCompletion { completionHandler.apply(it) }
            .collect {}
    }
}
