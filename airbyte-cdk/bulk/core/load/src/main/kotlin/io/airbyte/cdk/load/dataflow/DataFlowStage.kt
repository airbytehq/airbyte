package io.airbyte.cdk.load.dataflow

interface DataFlowStage {
    suspend fun apply(input: DataFlowStageIO): DataFlowStageIO
}
