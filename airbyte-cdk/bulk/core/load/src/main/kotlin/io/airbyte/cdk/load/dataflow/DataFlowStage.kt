package io.airbyte.cdk.load.dataflow

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.filterNot
import kotlinx.coroutines.flow.map

interface DataFlowStage {
    suspend fun apply(input: DataFlowStageIO): DataFlowStageIO
}

fun Flow<DataFlowStageIO>.applyStage(
    mapper: DataFlowStage,
): Flow<DataFlowStageIO> =
    this.map(mapper::apply)
        .filterNot { it.skip }
