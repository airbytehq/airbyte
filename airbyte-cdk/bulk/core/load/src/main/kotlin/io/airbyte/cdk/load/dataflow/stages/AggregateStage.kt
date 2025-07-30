package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.dataflow.Aggregate
import io.airbyte.cdk.load.dataflow.AggregateStore
import io.airbyte.cdk.load.dataflow.DataFlowStage
import io.airbyte.cdk.load.dataflow.DataFlowStageIO

class AggregateStage(
    val store: AggregateStore,
): DataFlowStage {
    override suspend fun apply(input: DataFlowStageIO): DataFlowStageIO {
        val agg = store.getOrCreate(input.rec!!.stream.mappedDescriptor)

        val result = agg.accept(input.munged!!)

        return when (result) {
            Aggregate.Status.COMPLETE -> input.apply { aggregate = agg }
            Aggregate.Status.INCOMPLETE -> input.apply { skip = true }
        }
    }
}
