package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.dataflow.stages.AggregateStage
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.Flow
import jakarta.inject.Named
import kotlinx.coroutines.flow.buffer
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
            .applyStage(parse)
            .transform { aggregate.apply(it, this) }
            .buffer(capacity = 5)
            .applyStage(flush)
            .applyStage(state)
            .onCompletion { completionHandler.apply(it) }
            .collect {}
    }
}
