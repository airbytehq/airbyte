package io.airbyte.cdk.load.dataflow

import jakarta.inject.Singleton
import kotlinx.coroutines.flow.Flow
import jakarta.inject.Named
import kotlinx.coroutines.flow.buffer

@Singleton
class DataFlowPipeline(
    val input: Flow<DataFlowStageIO>,
    @Named("parse") val parse: DataFlowStage,
    @Named("aggregate") val aggregate: DataFlowStage,
    @Named("flush") val flush: DataFlowStage,
    @Named("state") val state: DataFlowStage,
) {
    suspend fun run() {
        input
            .buffer(capacity = 128)
            .applyStage(parse)
            .applyStage(aggregate)
            .buffer(capacity = 8)
            .applyStage(flush)
            .applyStage(state)
            .collect { value ->
                println("Collecting $value on: ${Thread.currentThread().name}")
            }
    }
}
