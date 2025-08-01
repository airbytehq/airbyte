package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.dataflow.stages.AggAndPublish
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.Flow
import jakarta.inject.Named
import kotlinx.coroutines.flow.buffer
import kotlinx.coroutines.flow.transform

@Singleton
class DataFlowPipeline(
    val input: Flow<DataFlowStageIO>,
    @Named("parse") val parse: DataFlowStage,
    @Named("aggregate") val aggregate: AggAndPublish,
    @Named("flush") val flush: DataFlowStage,
    @Named("state") val state: DataFlowStage,
) {
    suspend fun run() {
        input
            .applyStage(parse)
            .transform(aggregate)
            .buffer(capacity = 5)
            .applyStage(state)
            .collect { value ->
                println("Collecting $value on: ${Thread.currentThread().name}")
            }
    }
}
