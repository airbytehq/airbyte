package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.dataflow.DataFlowStage
import io.airbyte.cdk.load.dataflow.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.state.StateWatermarkStore
import jakarta.inject.Named
import jakarta.inject.Singleton

@Named("state")
@Singleton
class StateStage(
    val stateStore: StateWatermarkStore,
): DataFlowStage {
    override suspend fun apply(input: DataFlowStageIO): DataFlowStageIO {
        val stateUpdates = input.aggregate!!.getStateHistogram()

        stateStore.updateOrCreate(
            input.munged!!.stateId,
            stateUpdates,
        )

        return input
    }
}
