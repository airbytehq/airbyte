package io.airbyte.cdk.load.dataflow

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

class DataFlowPipeline(
    val input: Flow<DataFlowStageIO>,
    val parse: DataFlowStage,
    val aggregate: DataFlowStage,
    val flush: DataFlowStage,
    val state: DataFlowStage,
) {
    fun run() {
        input
            .map(parse::apply)
            .map(aggregate::apply)
            .map(flush::apply)
            .map(state::apply)
    }

}
