package io.airbyte.cdk.load.dataflow

import jakarta.inject.Singleton
import kotlinx.coroutines.flow.Flow
import jakarta.inject.Named

@Singleton
class DataFlowPipeline(
    val input: Flow<DataFlowStageIO>,
    @Named("parse") val parse: DataFlowStage,
    @Named("aggregate") val aggregate: DataFlowStage,
    @Named("flush") val flush: DataFlowStage,
    @Named("state") val state: DataFlowStage,
) {
    fun run() {
        input
            .applyStage(parse)
            .applyStage(aggregate)
            .applyStage(flush)
            .applyStage(state)
    }
}
