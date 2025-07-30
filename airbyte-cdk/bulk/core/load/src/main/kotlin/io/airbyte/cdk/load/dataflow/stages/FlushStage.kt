package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.dataflow.DataFlowStage
import io.airbyte.cdk.load.dataflow.DataFlowStageIO

class FlushStage: DataFlowStage {
    override suspend fun apply(input: DataFlowStageIO): DataFlowStageIO {
        val agg = input.aggregate!!
        agg.flush()
        return input.apply { stateHist = agg.getStateHistogram() }
    }
}
