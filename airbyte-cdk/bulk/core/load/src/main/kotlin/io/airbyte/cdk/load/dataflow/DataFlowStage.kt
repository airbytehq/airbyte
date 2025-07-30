package io.airbyte.cdk.load.dataflow

import kotlinx.coroutines.flow.Flow

interface DataFlowStage {
    suspend fun apply(input: DataFlowStageIO): DataFlowStageIO
}
